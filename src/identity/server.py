"""Identity service main module."""

from wsgiref import simple_server

import auth0.v2.authentication as auth0
import clock
import falcon
import falcon_cors
import sqlalchemy
import startup_migrations

import identity_sdk as sdk
import identity.config as config
import identity.handlers as identity
import identity.model as model
import validation_common


def debug_error_handler(ex, req, resp, params):
    print(ex)
    raise ex


startup_migrations.migrate(config.DATABASE_URL, config.MIGRATIONS_PATH)


id_validator = validation_common.IdValidator()
datetime_ts_validator = validation_common.DateTimeTsValidator()
url_validator = validation_common.URLValidator()
auth0_user_validator = sdk.Auth0UserValidator(
    url_validator=url_validator)
access_token_header_validator = sdk.AccessTokenHeaderValidator()
user_validator = sdk.UserValidator(
    id_validator=id_validator,
    datetime_ts_validator=datetime_ts_validator,
    url_validator=url_validator)
user_response_validator = sdk.UserResponseValidator(
    user_validator=user_validator)

auth0_client = auth0.Users(config.AUTH0_DOMAIN)
the_clock = clock.Clock()
sql_engine = sqlalchemy.create_engine(config.DATABASE_URL, echo=True)
model = model.Model(the_clock=the_clock, sql_engine=sql_engine)

user_resource = identity.UserResource(
    auth0_client=auth0_client,
    auth0_user_validator=auth0_user_validator,
    access_token_header_validator=access_token_header_validator,
    user_response_validator=user_response_validator,
    model=model)

cors_middleware = falcon_cors.CORS(
    allow_origins_list=config.CLIENTS,
    allow_headers_list=['Authorization', 'Content-Type'],
    allow_all_methods=True).middleware

app = falcon.API(middleware=[cors_middleware])

if config.ENV != 'PROD':
    app.add_error_handler(Exception, handler=debug_error_handler)

app.add_route('/user', user_resource)


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.ADDRESS, config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    main()
