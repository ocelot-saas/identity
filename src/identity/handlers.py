"""Handlers for HTTP resources for the identity service."""

import json
import hashlib

import falcon
import jsonschema
import retry
import sqlalchemy as sql

import identity.model as model
import identity.validation as validation
import identity.schemas as schemas


class UserResource(object):
    """A collection of users, linked to Auth0."""

    def __init__(self, auth0_client, auth0_user_validator, access_token_header_validator, model):
        self._auth0_client = auth0_client
        self._auth0_user_validator = auth0_user_validator
        self._access_token_header_validator = access_token_header_validator
        self._model = model

    def on_post(self, req, resp):
        """Create a particular user.

        Requires the Authorization header to be present and contain an JWT for Auth0.
        """

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        try:
            user = self._model.create_user(auth0_user_id_hash)
        except model.UserAlreadgExistsError as e:
            raise falcon.HTTPConflict(
                title='User already exists',
                description='User already exists') from e
        except model.Error as e:
            raise falcon.HTTPBadRequest(
                title='Could not create user',
                description='Coult not create user') from e

        response = {
            'user': {
                'id': user['id'],
                'timeJoinedTs': user['timeJoinedTs'],
                'name': auth0_user['name'],
                'pictureUrl': auth0_user['picture']
            }
        }

        jsonschema.validate(response, schemas.USER_RESPONSE)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps(response)

    def on_get(self, req, resp):
        """Retrieve a particular user.

        Requires the Authorization header to be present and contain an JWT from Auth0.
        """

        (auth0_user, auth0_user_id_hash) = self._get_auth0_user(req)

        try:
            user = self._model.get_user(auth0_user_id_hash)
        except model.UserDoesNotExistError as e:
            raise falcon.HTTPNotFound(
                title='User does not exist',
                description='User does not exist')
            
        response = {
            'user': {
                'id': user['id'],
                'timeJoinedTs': user['timeJoinedTs'],
                'name': auth0_user['name'],
                'pictureUrl': auth0_user['picture']
            }
        }

        jsonschema.validate(response, schemas.USER_RESPONSE)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    @retry.retry((validation.Error), tries=3)
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
