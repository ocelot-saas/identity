"""Handlers for HTTP resources for the identity service."""

import json
import hashlib

import falcon
import retry
import sqlalchemy as sql
import validation

import identity.model as model


class UserResource(object):
    """A collection of users, linked to Auth0."""

    def __init__(self, auth0_client, auth0_user_validator, access_token_header_validator,
                 user_response_validator, model):
        self._auth0_client = auth0_client
        self._auth0_user_validator = auth0_user_validator
        self._access_token_header_validator = access_token_header_validator
        self._user_response_validator = user_response_validator
        self._model = model

    def on_post(self, req, resp):
        """Create a particular user.

        Requires the Authorization header to be present and contain an JWT for Auth0.
        """

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        try:
            user = self._model.create_user(auth0_user_id_hash)

            response = self._user_response_validator.validate({
                'user': {
                    'id': user['id'],
                    'timeJoinedTs': user['timeJoinedTs'],
                    'name': auth0_user['name'],
                    'pictureUrl': auth0_user['picture']
                }
            })

            resp.status = falcon.HTTP_201
            resp.body = json.dumps(response)
        except model.UserAlreadyExistsError as e:
            raise falcon.HTTPConflict(
                title='User already exists',
                description='User already exists') from e
        except model.Error as e:
            raise falcon.HTTPBadRequest(
                title='Could not create user',
                description='Coult not create user') from e

    def on_get(self, req, resp):
        """Retrieve a particular user.

        Requires the Authorization header to be present and contain an JWT from Auth0.
        """

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        try:
            user = self._model.get_user(auth0_user_id_hash)

            response = self._user_response_validator.validate({
                'user': {
                    'id': user['id'],
                    'timeJoinedTs': user['timeJoinedTs'],
                    'name': auth0_user['name'],
                    'pictureUrl': auth0_user['picture']
                }
            })

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response)
        except model.UserDoesNotExistError as e:
            raise falcon.HTTPNotFound(
                title='User does not exist',
                description='User does not exist')

    @retry.retry((validation.Error), tries=3)
    def _get_auth0_user(self, req):
        try:
            access_token = self._access_token_header_validator.validate(req.auth)
            auth0_user_raw_raw = self._auth0_client.userinfo(access_token)
            if auth0_user_raw_raw == 'Unauthorized':
                raise falcon.HTTPUnauthorized(
                    title='Could not retrieve data from Auth0',
                    description='Auth0 refused to authorized with accesss token "{}"'.format(access_token),
                    challenges='Bearer')
            auth0_user_raw = json.loads(auth0_user_raw_raw)
            auth0_user = self._auth0_user_validator.validate(auth0_user_raw)
        except ValueError as e:
            raise e
            raise falcon.HTTPBadGateway(
                title='Invalid data from Auth0',
                description='Invalid data from Auth0') from e
        except validation.Error as e:
            raise e
            raise falcon.HTTPBadRequest(
                title='Invalid Authorization header',
                description='Invalid value "{}" for Authorization header'.format(req.auth)) from e
        except falcon.HTTPUnauthorized:
            raise
        except Exception as e:
            raise e
            raise falcon.HTTPBadGateway(
                title='Cannot retrieve data from Auth0',
                description='Could not retrieve data from Auth0') from e

        return (auth0_user, hashlib.sha256(auth0_user['user_id'].encode('utf-8')).hexdigest())
