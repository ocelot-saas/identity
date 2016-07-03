"""Identity validation."""

import validate_email


class Error(Exception):
    """Error raised by validation methods."""
    pass


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
