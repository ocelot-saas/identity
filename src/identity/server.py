"""Identity service main module."""

from wsgiref import simple_server

import clock
import auth0.v2.authentication as auth0
import falcon
import falcon_cors
import sqlalchemy

import identity.config as config
import identity.handlers as identity
import identity.validation as validation

cors_middleware = falcon_cors.CORS(
    allow_origins_list=config.CLIENTS,
    allow_headers_list=['Authorization', 'Content-Type'],
    allow_all_methods=True).middleware

app = falcon.API(middleware=[cors_middleware])

auth0_client = auth0.Users(config.AUTH0_DOMAIN)
auth0_user_validator = validation.Auth0UserValidator()
access_token_header_validator = validation.AccessTokenHeaderValidator()
the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)

user_resource = identity.UserResource(
    auth0_client=auth0_client,
    auth0_user_validator=auth0_user_validator,
    access_token_header_validator=access_token_header_validator,
    the_clock=the_clock,
    sql_engine=sql_engine)

app.add_route('/user', user_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
