"""Handlers for HTTP resources for the identity service."""

import json
import hashlib

import falcon

import identity.config as config
import identity.validation as validation
import identity.schemas as schemas
import sqlalchemy as sql
import jsonschema


_metadata = sql.MetaData(schema='identity')

_user = sql.Table(
    'user', _metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('auth0_user_id_hash', sql.String(64), index=True),
    sql.Column('time_joined', sql.DateTime(timezone=True)))


class UserResource(object):
    """A collection of users, linked to Auth0."""

    def __init__(self, auth0_client, auth0_user_validator, id_token_header_validator,
                 the_clock, sql_engine):
        self._auth0_client = auth0_client
        self._auth0_user_validator = auth0_user_validator
        self._id_token_header_validator = id_token_header_validator
        self._the_clock = the_clock
        self._sql_engine = sql_engine

        self._cors_clients = ','.join('http://{}'.format(c) for c in config.CLIENTS)

    def on_options(self, req, resp):
        """Check CORS is OK."""

        resp.status = falcon.HTTP_204
        self._cors_response(resp)

    def on_post(self, req, resp):
        """Create a particular user.

        Requires the Authorization header to be present and contain an JWT for Auth0.
        """

        right_now = self._the_clock.now()

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        with self._sql_engine.begin() as conn:
            user_row = self._fetch_user(conn, auth0_user_id_hash)

            if user_row is not None:
                is_new = False
                user_id = user_row.id
                user_time_joined = user_row['time_joined']
            else:
                is_new = True
                create_user = _user \
                    .insert() \
                    .values(auth0_user_id_hash=auth0_user_id_hash, time_joined=right_now)
                result = conn.execute(create_user)
                user_id = result.lastrowid
                user_time_joined = right_now
                result.close()

        response = {
            'user': {
                'id': user_id,
                'timeJoinedTs': int(user_time_joined.timestamp()),
                'name': auth0_user['name'],
                'pictureUrl': auth0_user['picture']
            }
        }

        jsonschema.validate(response, schemas.USER_RESPONSE)

        resp.status = falcon.HTTP_201 if is_new else falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Retrieve a particular user.

        Requires the Authorization header to be present and contain an JWT from Auth0.
        """

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        with self._sql_engine.begin() as conn:
            fetch_by_auth0_user_id_hash = sql.sql \
                .select([_user]) \
                .where(_user.c.auth0_user_id_hash == auth0_user_id_hash)

            result = conn.execute(fetch_by_auth0_user_id_hash)
            user_row = result.fetchone()
            result.close()

            if user_row is None:
                raise falcon.HTTPNotFound(
                    title='Something went wrong',
                    description='User does not exist')

        response = {
            'user': {
                'id': user_row['id'],
                'timeJoinedTs': int(user_row['time_joined'].timestamp()),
                'name': auth0_user['name'],
                'pictureUrl': auth0_user['picture']
            }
        }

        jsonschema.validate(response, schemas.USER_RESPONSE)

        resp.status = falcon.HTTP_200
        self._cors_response(resp)
        resp.body = json.dumps(response)

    def _get_auth0_user(self, req):
        # TODO(horia141): make this prettier.
        try:
            id_token = self._id_token_header_validator.validate(req.auth)
        except validation.Error:
            raise falcon.HTTPBadRequest(
                title='Invalid Authorization header',
                description='Invalid value "{}" for Authorization header'.format(req.auth))

        try:
            auth0_user_raw = self._auth0_client.userinfo(id_token)
            auth0_user = self._auth0_user_validator.validate(auth0_user_raw)
        except Exception as e:
            raise falcon.HTTPBadRequest(
               title='Something went wrong',
               description='Cannot retrieve data from Auth0 because "{}"'.format(str(e)))

        return (auth0_user, hashlib.sha256(auth0_user['user_id'].encode('utf-8')).hexdigest())

    def _fetch_user(self, conn, auth0_user_id_hash):
        fetch_by_auth0_user_id_hash = sql.sql \
            .select([_user]) \
            .where(_user.c.auth0_user_id_hash == auth0_user_id_hash)

        result = conn.execute(fetch_by_auth0_user_id_hash)
        user_row = result.fetchone()
        result.close()

        return user_row

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
