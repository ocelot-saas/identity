"""Client interface for users of the identity service."""

import json

import falcon
import jsonschema
import requests

import identity.validation as validation
import identity.schemas as schemas


class Error(Exception):
    """Error raised by the client library."""

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return 'Identity client error because ""'.format(self._reason)


class AuthMiddleware(object):
    """Falcon middleware component which makes all routes of the API require auth.

    The component also makes available a `.user` property on the request object which will
    be passed to resource handlers. This is a Python JSON object which follows the
    `schemas.USER` schema.

    If the user is not valid, a 401 Unauthorized is returned. Other errors raise appropriate
    error responses.
    """

    def __init__(self, identity_service_domain, access_token_header_validator=None):
        self._identity_service_user_url = 'http://{}/user'.format(identity_service_domain)
        self._access_token_header_validator = \
            access_token_header_validator if access_token_header_validator is not None \
            else validation.AccessTokenHeaderValidator()

    def process_resource(self, req, resp, resource, params):
        # No auth is expected on the OPTIONS header.
        if req.method == 'OPTIONS':
            return

        if hasattr(resource, 'AUTH_NOT_REQUIRED') and resource.AUTH_NOT_REQUIRED:
            return
        
        try:
            access_token = self._access_token_header_validator.validate(req.auth)
            user_get_req = requests.get(
                self._identity_service_user_url,
                headers={'Authorization': 'Bearer {}'.format(access_token)})
            user_get_req.raise_for_status()
            user_json = json.loads(user_get_req.text)
            jsonschema.validate(user_json, schemas.USER_RESPONSE)
            req.context['user'] = user_json['user']
        except validation.Error as e:
            raise falcon.HTTPBadRequest(
                title='Invalid Authorization header',
                description='Invalid value "{}" for Authorization header'.format(req.auth)) from e
        except (requests.ConnectionError, requests.Timeout) as e:
            raise falcon.HTTPBadGateway(
                title='Cannot retrieve data from identity service',
                description='Could not retrieve data from identity service') from e
        except requests.HTTPError as e:
            if user_get_req.status_code == 401:
                raise falcon.HTTPUnauthorized(
                    title='Could not retrieve data from identity service',
                    description='Identity service refused to auhtorize ' +
                    'with access token "{}"'.format(access_token),
                    challenges='Bearer') from e
            elif user_get_req.status_code == 404:
                raise falcon.HTTPNotFound(
                    title='User does not exist',
                    description='User does not exist')
            else:
                raise falcon.HTTPBadGateway(
                    title='Cannot retrieve data from identity service',
                    description='Could not retrieve data from identity service') from e
        except (ValueError, jsonschema.ValidationError) as e:
            raise falcon.HTTPInternalServerError(
                    title='Cannot decode data from identity service',
                    description='Could not decode data from identity service') from e
        except Exception as e:
            raise falcon.HTTPInternalServerError(
                    title='Unkown error when retrieving data from identity service',
                    description='Unkown error when retrieving data from identity service') from e
