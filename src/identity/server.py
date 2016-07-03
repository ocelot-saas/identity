"""Identity service main module."""

from wsgiref import simple_server

import falcon

import identity.config as config
import identity.handlers as identity
import identity.validation as validation
import secrets


# /users
#   GET with a given auth token retrieves the respective user
#   GET with an email and password retrieves the respective user
#   POST creates a user, with an email&password
# /users/check-email
#   GET with a given email checks if a user can be created with it
app = falcon.API()

secret_generator = secrets.SecretGenerator()

email_address_validator = validation.EmailAddressValidator()
password_validator = validation.PasswordValidator(secret_generator)

app.add_route('/users', identity.UsersResource(
    email_address_validator, password_validator))
app.add_route('/users/check-email', identity.CheckEmailAddressResource(
    email_address_validator))


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.address, config.port, app)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
