import falcon

import identity.handlers as identity

app = falcon.API()

app.add_route('/hello', identity.IdentityResource())
