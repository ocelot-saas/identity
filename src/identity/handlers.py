import falcon


class IdentityResource(object):
    def on_get(self, req, resp):
        """Handles GET requestss"""
        resp.status = falcon.HTTP_200
        resp.body = 'Hello falcon'
