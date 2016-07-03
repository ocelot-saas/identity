"""Identity service main module."""

from wsgiref import simple_server

import falcon

import identity.config as config
import identity.handlers as identity


app = falcon.API()

# /users
#   GET with a given auth token retrieves the respective user
#   GET with an email and password retrieves the respective user
#   POST creates a user, with an email&password
# /users/check-email
#   GET with a given email checks if a user can be created with it
app.add_route('/users', identity.UsersResource())
app.add_route('/users/check-mail', identity.CheckMailResouce())


def main():
    """Server entry point."""
    httpd = simple_server.make_server(config.address, config.port, app)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
