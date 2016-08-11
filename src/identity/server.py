"""Identity service main module."""

from wsgiref import simple_server

import falcon
import auth0.v2.authentication as auth0

import clock
import identity.config as config
import identity.handlers as identity
import identity.validation as validation
import sqlalchemy


# /user
#   POST creates a user, via Auth0
#   GET retrieves a user, via Auth0
app = falcon.API()

auth0_client = auth0.Users(config.AUTH0_DOMAIN)
auth0_user_validator = validation.Auth0UserValidator()
id_token_header_validator = validation.IdTokenHeaderValidator()
the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)

user_resource = identity.UserResource(
    auth0_client=auth0_client,
    auth0_user_validator=auth0_user_validator,
    id_token_header_validator=id_token_header_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

app.add_route('/user', user_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
