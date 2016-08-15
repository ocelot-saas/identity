"""Client interface for users of the identity service."""

import requests

from .validation import IdTokenHeaderValidator


class Error(Exception):
    """Error raised by the client library."""

    def __init__(self, reason):
        self._reason = reason


    def __str__(self):
        return 'Identity client error! Reason: \n {}'.format(str(self._reason))


class AuthMiddleware(object):
    """Falcon middleware component which makes all routes of the API require auth.

    The component also makes available a `.user` property on the request object which will
    be passed to resource handlers. This is a Python JSON object which follows the
    `schemas.USER` schema.

    If the user is not valid, a 401 Unauthorized is returned.
    """

    def __init__(self, identity_service_domain, id_token_header_validator=None):
        self._identity_service_url = 'http:{}/user'.format(identity_service_domain)
        self._id_token_header_validator = id_token_header_validator if id_token_header_validator \
            is not None else IdTokenHeaderValidator()

    def process_resource(self, req, resp, resource, params):
        try:
            id_token = self._id_token_header_validator.validate(req.auth)
            user_get_req = requests.get(self._identity_service_user_url, headers={'Authorization: Bearer {}'.format(id_token)})
            user_json = user_get_req.json()
            jsonschema.validate(schemas.USER_RESPONSE)
 
           req.user = user_json['user']
        except Exception as e:
            raise Error(e)
