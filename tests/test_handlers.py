import unittest

import falcon.testing

import identity.handlers as identity


class IdentityResourceTest(falcon.testing.TestCase):
    def setUp(self):
        super(IdentityResourceTest, self).setUp()
        self.api.add_route('/hello', identity.IdentityResource())

    def test_get(self):
        """GET /hello works."""

        res = self.simulate_get('/hello')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello falcon')


if __name__ == '__main__':
    unittest.main()
