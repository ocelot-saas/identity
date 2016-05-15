from wsgiref import simple_server

import falcon

import identity.config as config
import identity.handlers as identity


app = falcon.API()

app.add_route('/hello', identity.IdentityResource())


if __name__ == '__main__':
    httpd = simple_server.make_server(config.address, config.port, app)
    httpd.serve_forever()
