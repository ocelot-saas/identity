"""Identity validation."""

import validate_email
import secrets

import identity.schemas as schemas
import jsonschema


class Error(Exception):
    """Error raised by validation methods."""
    pass


class UserCreationDataValidator(object):
    """Validator for user creation data."""

    def __init__(self, name_validator, email_address_validator, password_validator):
        self._name_validator = name_validator
        self._email_address_validator = email_address_validator
        self._password_validator = password_validator

    def validate(self, user_creation_data):
        try:
            jsonschema.validate(user_creation_data, schemas.USER_CREATION_DATA)
        except jsonschema.ValidationError:
            raise Error()
        
        user_creation_data['name'] = \
            self._name_validator.validate(user_creation_data['name'])
        user_creation_data['email_address'] = \
            self._email_address_validator.validate(user_creation_data['email_address'])
        user_creation_data['password'] = \
            self._password_validator.validate(user_creation_data['password'])

        return user_creation_data


class NameValidator(object):
    """Validator for names."""

    def validate(self, name):
        """Validate a name."""
        name = name.strip()
        
        if name == u'':
            raise Error()

        return name


class AuthTokenValidator(object):
    """Validator for auth tokens."""

    def validate(self, auth_token):
        """Validate an auth token."""
        auth_token = auth_token.strip()

        if len(auth_token) != secrets.USER_SECRET_SIZE:
            raise Error()

        return auth_token


class EmailAddressValidator(object):
    """Validator for email addresses."""

    def validate(self, email_address):
        """Validate an email address."""
        email_address = email_address.strip()

        if not validate_email.validate_email(email_address):
            raise Error()

        return email_address


class PasswordValidator(object):
    """Validator for passwords."""

    def __init__(self, secret_generator):
        self._secret_generator = secret_generator

    def validate(self, password):
        """Validate a password."""

        if password == '':
            raise Error()

        if not self._secret_generator.is_password_allowed(password):
            raise Error()

        return password
