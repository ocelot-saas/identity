"""Identity validation."""

import re
import json

import identity.schemas as schemas
import jsonschema


class Error(Exception):
    """Error raised by validation methods."""

    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return 'Validation error because ""'.format(self._reason)


class Auth0UserValidator(object):
    """Validator for Auth0 user JSON."""

    def __init__(self):
        pass

    def validate(self, auth0_user_raw):
        try:
            auth0_user = json.loads(auth0_user_raw)
            jsonschema.validate(auth0_user, schemas.AUTH0_USER_RESPONSE)
        except ValueError as e:
            raise Error('Could not decode Auth0 JSON response') from e
        except jsonschema.ValidationError as e:
            raise Error('Could not validate Auth0 user data') from e
        except Exception as e:
            raise Error('Other error') from e

        return auth0_user


class AccessTokenHeaderValidator(object):
    """Validator for the access token header."""

    def __init__(self):
        self._auth_re = re.compile('Bearer (.+)')

    def validate(self, auth_header):
        if not isinstance(auth_header, str):
            raise Error('Missing Authorization header')

        match = self._auth_re.match(auth_header)

        if match is None:
            raise Error('Invalid Authorization header')

        return match.group(1)
