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

    def __init__(self, auth0_client, auth0_user_validator, access_token_header_validator,
                 the_clock, sql_engine):
        self._auth0_client = auth0_client
        self._auth0_user_validator = auth0_user_validator
        self._access_token_header_validator = access_token_header_validator
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
            try:
                create_user = _user \
                    .insert() \
                    .values(auth0_user_id_hash=auth0_user_id_hash, time_joined=right_now)
                result = conn.execute(create_user)
                user_id = result.inserted_primary_key[0]
                result.close()
            except sql.exc.IntegrityError as e:
                raise falcon.HTTPConflict(
                    title='User already exists',
                    description='User already exists') from e

        response = {
            'user': {
                'id': user_id,
                'timeJoinedTs': int(right_now.timestamp()),
                'name': auth0_user['name'],
                'pictureUrl': auth0_user['picture']
            }
        }

        jsonschema.validate(response, schemas.USER_RESPONSE)

        resp.status = falcon.HTTP_201
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
                    title='User does not exist',
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
        try:
            access_token = self._access_token_header_validator.validate(req.auth)
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid Authorization header',
                description='Invalid value "{}" for Authorization header'.format(req.auth)) from e

        try:
            auth0_user_raw = self._auth0_client.userinfo(access_token)
            if auth0_user_raw == 'Unauthorized':
                raise falcon.HTTPUnauthorized(
                    title='Could not retrieve data from Auth0',
                    description='Auth0 refused to authorized with accesss token "{}"'.format(access_token),
                    challenges='Bearer')
            auth0_user = self._auth0_user_validator.validate(auth0_user_raw)
        except falcon.HTTPUnauthorized:
            raise
        except validation.Error as e:
            raise falcon.HTTPInternalServerError(
                title='Could not parse response from Auth0',
                description='Could not parse response from Auth0') from e
        except Exception as e:
            raise falcon.HTTPBadGateway(
                title='Cannot retrieve data from Auth0',
                description='Could not retrieve data from Auth0') from e

        return (auth0_user, hashlib.sha256(auth0_user['user_id'].encode('utf-8')).hexdigest())

    def _cors_response(self, resp):
        resp.append_header('Access-Control-Allow-Origin', self._cors_clients)
        resp.append_header('Access-Control-Allow-Methods', 'OPTIONS, POST, GET')
        resp.append_header('Access-Control-Allow-Headers', 'Authorization')
