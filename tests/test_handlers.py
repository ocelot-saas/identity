import unittest
from mockito import mock

import falcon.testing

import identity.handlers as identity


class UsersResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(UsersResourceTestCase, self).setUp()

        email_address_validator = mock()
        password_validator = mock()
        self.api.add_route('/users', identity.UsersResource(
            email_address_validator, password_validator))

    def test_get(self):
        """GET /users works."""

        res = self.simulate_get('/users')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello falcon')


class CheckEmailAddressResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(CheckEmailAddressResourceTestCase, self).setUp()

        email_address_validator = mock()
        self.api.add_route('/users/check-email', identity.CheckEmailAddressResource(
            email_address_validator))

    def test_get(self):
        """GET /users/check-email works."""

        res = self.simulate_get('/users/check-email')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello falcon')


if __name__ == '__main__':
    unittest.main()
