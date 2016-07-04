"""Handlers for HTTP resources for the identity service."""

import datetime
import json

import falcon

import identity.validation as validation
import identity.schemas as schemas
import pytz
import secrets
import sqlalchemy as sql
import jsonschema


_metadata = sql.MetaData()


_users = sql.Table(
    'Users', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('external_id', sql.String(secrets.USER_SECRET_SIZE), index=True),
    sql.Column('status', sql.Enum('ACTIVE', 'INACTIVE')),
    sql.Column('name', sql.String),
    sql.Column('time_joined', sql.DateTime(timezone=True)),
    sql.Column('time_left', sql.DateTime(timezone=True), nullable=True))


_basic_access_info = sql.Table(
    'BasicAccessInfo', _metadata,
    sql.Column('user_id', sql.Integer, primary_key=True),
    sql.Column('email_address', sql.String, index=True),
    sql.Column('hidden_password', sql.String(secrets.HIDDEN_PASSWORD_SIZE)))


_facebook_access_info = sql.Table(
    'FacebookAccessInfo', _metadata,
    sql.Column('user_id', sql.Integer, primary_key=True),
    sql.Column('access_token', sql.String),
    sql.Column('expiry_time', sql.DateTime(timezone=pytz.utc)))


_auth_tokens = sql.Table(
    'AuthTokens', _metadata,
    sql.Column('token', sql.String, primary_key=True),
    sql.Column('expiry_time', sql.DateTime(timezone=pytz.utc)),
    sql.Column('user_id', sql.ForeignKey(_users.c.id)))


AUTH_TOKEN_LIFETIME_DURATION = datetime.timedelta(milliseconds=2592000000)


def set_up_database(sql_engine):
    """Set up database tables for the identity service."""
    _metadata.create_all(sql_engine)


class UsersResource(object):
    """A collection of users.

    Handles creation, and 'retrieval' via auth token.
    """

    def __init__(self, auth_token_validator, name_validator, email_address_validator,
                 password_validator, user_creation_data_validator, the_clock,
                 secret_generator, sql_engine):
        self._auth_token_validator = auth_token_validator
        self._name_validator = name_validator
        self._email_address_validator = email_address_validator
        self._password_validator = password_validator
        self._user_creation_data_validator = user_creation_data_validator
        self._clock = the_clock
        self._secret_generator = secret_generator
        self._sql_engine = sql_engine

    def on_get(self, req, resp):
        """GET a particular user.

        GET with a given auth token retrieves the respective user.
        GET with an email and password retrieves the respective user.
        """

        get_type = req.get_param('t', required=True)

        if get_type == 'a':
            self._on_get_auth_token(req, resp)
        elif get_type == 'ep':
            self._on_get_email_address_and_pass(req, resp)
        else:
            raise falcon.HTTPBadRequest(
                title='Bad GET type param',
                description='Invalid value "{}" for type param'.format(get_type))

    def on_post(self, req, resp):
        """POST creates a user, with a given email and password."""
        try:
            user_creation_data = json.loads(req.stream.read().decode('utf-8'))
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title='Bad user creation data',
                description='Could not parse user creation data')
        try:
            user_creation_data = self._user_creation_data_validator.validate(user_creation_data)

            name = user_creation_data['name']
            email_address = user_creation_data['emailAddress']
            password = user_creation_data['password']
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Bad user creation data',
                description='Invalid value "{}" for user creation data'.format(json.dumps(user_creation_data)))

        # This is going to be the time we always use when a creation date is required.
        right_now = self._clock.now()

        with self._sql_engine.begin() as conn:
            # Figure out if we already have a user with the same userId.
            basic_access_info_row = _fetch_basic_info(conn, email_address)

            if basic_access_info_row is not None:
                raise falcon.HTTPBadRequest(
                    title='Email already exists',
                    description='Email address "{}" is already in use'.format(email_address))

            # Create an entry for the person in the Users table.
            create_user = _users \
                .insert() \
                .values(status='ACTIVE', name=name, time_joined=right_now)
            result = conn.execute(create_user)
            user_id = result.inserted_primary_key[0]
            result.close()
            user_external_id = self._secret_generator.gen_user_secret(user_id)
            complete_user_with_external_id = _users \
                .update() \
                .where(_users.c.id == user_id) \
                .values(external_id=user_external_id)
            conn.execute(complete_user_with_external_id).close()

            #  Create an entry for the person in the basic access info table.
            hidden_password = self._secret_generator.hash_password_and_gen_salt(password)
            create_basic_access_info = _basic_access_info \
                .insert() \
                .values(
                    user_id=user_id, email_address=email_address, hidden_password=hidden_password)
            conn.execute(create_basic_access_info).close()

            # Create an auth token for the person.
            auth_token_row = self._create_auth_token(conn, right_now, user_id)

        response = {
            'user': {
                'externalId': user_external_id,
                'name': user_creation_data['name'],
                'timeJoinedTs': int(right_now.timestamp())
            },
            'authToken': {
                'token': auth_token_row['token'],
                'expiryTimeTs': int(auth_token_row['expiry_time'].timestamp())
            }
        }

        jsonschema.validate(response, schemas.USERS_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def _on_get_auth_token(self, req, resp):
        auth_token = req.get_param('authtoken', required=True)
        try:
            auth_token = self._auth_token_validator.validate(auth_token)
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Bad auth token',
                description='Invalid value "{}" for auth token param'.format(auth_token))

        right_now = self._clock.now()

        with self._sql_engine.begin() as conn:
            # Figure out whether there is an auth token.
            fetch_auth_token = sql.sql \
                .select([_auth_tokens]) \
                .where(_auth_tokens.c.token == auth_token)

            result = conn.execute(fetch_auth_token)
            auth_token_row = result.fetchone()
            result.close()

            if auth_token_row is None:
                raise falcon.HTTPUnauthorized(
                    title='Cannot find auth token',
                    description='Cannot find auth token',
                    challenges='Cannot find auth token')

            if auth_token_row['expiry_time'].replace(tzinfo=pytz.utc) < right_now:
                raise falcon.HTTPUnauthorized(
                    title='Cannot find auth token',
                    description='Cannot find auth token',
                    challenges='Cannot find auth token')

            # Fetch full user information.
            user_row = _fetch_user(conn, auth_token_row['user_id'])

        response = {
            'user': {
                'externalId': user_row['external_id'],
                'name': user_row['name'],
                'timeJoinedTs': int(user_row['time_joined'].timestamp())
            },
            'authToken': {
                'token': auth_token_row['token'],
                'expiryTimeTs': int(auth_token_row['expiry_time'].timestamp())
            }
        }

        jsonschema.validate(response, schemas.USERS_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _on_get_email_address_and_pass(self, req, resp):
        email_address = req.get_param('email', required=True)
        try:
            email_address = self._email_address_validator.validate(email_address)
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Bad email address',
                description='Invalid value "{}" for email address param'.format(email_address))

        password = req.get_param('pass', required=True)
        try:
            password = self._password_validator.validate(password)
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Bad password',
                description='Invalid value "{}" for password param'.format(password))

        right_now = self._clock.now()

        with self._sql_engine.begin() as conn:
            # Figure out if we have a user with the same email.
            basic_access_info_row = _fetch_basic_info(conn, email_address)

            if basic_access_info_row is None:
                raise falcon.HTTPUnauthorized(
                    title='Cannot find email address or password is invalid',
                    description='Cannot find email address or password is invalid',
                    challenges='Cannot find email address or password is invalid')

            if not self._secret_generator.check_password(
                    password, basic_access_info_row['hidden_password']):
                raise falcon.HTTPUnauthorized(
                    title='Cannot find email address or password is invalid',
                    description='Cannot find email address or password is invalid',
                    challenges='Cannot find email address or password is invalid')

            # Fetch full user information.
            user_row = _fetch_user(conn, basic_access_info_row['user_id'])

            # Create an auth token for the person.
            auth_token_row = self._create_auth_token(
                conn, right_now, basic_access_info_row['user_id'])

        response = {
            'user': {
                'externalId': user_row['external_id'],
                'name': user_row['name'],
                'timeJoinedTs': int(user_row['time_joined'].timestamp())
            },
            'authToken': {
                'token': auth_token_row['token'],
                'expiryTimeTs': int(auth_token_row['expiry_time'].timestamp())
            }
        }

        jsonschema.validate(response, schemas.USERS_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def _create_auth_token(self, conn, right_now, user_id):
        token = self._secret_generator.gen_user_secret(user_id)
        expiry_time = right_now + AUTH_TOKEN_LIFETIME_DURATION
        create_auth_token = \
            _auth_tokens \
            .insert() \
            .values(token=token, expiry_time=expiry_time, user_id=user_id)
        conn.execute(create_auth_token).close()

        return {
            'token': token,
            'expiry_time': expiry_time
        }


class CheckEmailAddressResource(object):
    """An RPC style resource for checking whether an email is in use or not."""

    def __init__(self, email_address_validator, sql_engine):
        self._email_address_validator = email_address_validator
        self._sql_engine = sql_engine

    def on_get(self, req, resp):
        """GET checks to see if a particular email is in use."""
        email_address = req.get_param('email', required=True)
        try:
            email_address = self._email_address_validator.validate(email_address)
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Bad email address',
                description='Invalid value "{}" for email address param'.format(email_address))

        with self._sql_engine.begin() as conn:
            basic_access_info_row = _fetch_basic_info(conn, email_address)

        response = {
            "inUse": basic_access_info_row is not None
        }

        jsonschema.validate(response, schemas.CHECK_EMAIL_ADDRESS_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


def _fetch_basic_info(conn, email_address):
    fetch_by_email = sql.sql \
                        .select([_basic_access_info]) \
                        .where(_basic_access_info.c.email_address == email_address)

    result = conn.execute(fetch_by_email)
    basic_access_info_row = result.fetchone()
    result.close()

    return basic_access_info_row


def _fetch_user(conn, user_id):
    fetch_by_user_id = sql.sql \
                          .select([_users]) \
                          .where(_users.c.id == user_id)

    result = conn.execute(fetch_by_user_id)
    user_row = result.fetchone()
    result.close()

    return user_row
