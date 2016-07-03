import unittest

import falcon.testing

import identity.handlers as identity


class UsersResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(UsersResourceTestCase, self).setUp()
        self.api.add_route('/users', identity.UsersResource())

    def test_get(self):
        """GET /users works."""

        res = self.simulate_get('/users')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello falcon')


class CheckEmailAddressResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(UsersResourceTestCase, self).setUp()
        self.api.add_route('/users/check-email', identity.CheckEmailAddressResouce())

    def test_get(self):
        """GET /users/check-email works."""

        res = self.simulate_get('/users/check-email')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello falcon')


if __name__ == '__main__':
    unittest.main()
