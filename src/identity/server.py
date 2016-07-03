"""Identity service main module."""

from wsgiref import simple_server

import falcon

import clock
import identity.config as config
import identity.handlers as identity
import identity.validation as validation
import secrets
import sqlalchemy


# /users
#   GET with a given auth token retrieves the respective user
#   GET with an email and password retrieves the respective user
#   POST creates a user, with an email&password
# /users/check-email
#   GET with a given email checks if a user can be created with it
app = falcon.API()

secret_generator = secrets.SecretGenerator()

auth_token_validator = validation.AuthTokenValidator()
name_validator = validation.NameValidator()
email_address_validator = validation.EmailAddressValidator()
password_validator = validation.PasswordValidator(secret_generator)
user_creation_data_validator = validation.UserCreationDataValidator(
    name_validator=name_validator,
    email_address_validator=email_address_validator,
    password_validator=password_validator)
the_clock = clock.Clock()
secret_generator = secrets.SecretGenerator()
sql_engine = sqlalchemy.create_engine(config.db_path, echo=True)

users_resource = identity.UsersResource(
    auth_token_validator=auth_token_validator,
    name_validator=name_validator,
    email_address_validator=email_address_validator,
    user_creation_data_validator=user_creation_data_validator,
    password_validator=password_validator,
    the_clock=the_clock,
    secret_generator=secret_generator,
    sql_engine=sql_engine)
check_email_address_resource = identity.CheckEmailAddressResource(
    email_address_validator=email_address_validator,
    sql_engine=sql_engine)

identity.set_up_database(sql_engine)

app.add_route('/users', users_resource)
app.add_route('/users/check-email', check_email_address_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.address, config.port, app)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
