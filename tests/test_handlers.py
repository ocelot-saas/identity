import unittest
from mockito import mock

import falcon.testing

import identity.handlers as identity


class UsersResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(UsersResourceTestCase, self).setUp()

        auth_token_validator = mock()
        email_address_validator = mock()
        password_validator = mock()
        user_creation_data_validator = mock()
        the_clock = mock()
        secret_generator = mock()
        sql_engine = mock()
        users_resource = identity.UsersResource(
            auth_token_validator=auth_token_validator,
            name_validator=name_validator,
            email_address_validator=email_address_validator,
            user_creation_data_validator=user_creation_data_validator,
            password_validator=password_validator,
            the_clock=the_clock,
            secret_generator=secret_generator,
            sql_engine=sql_engine)
        self.api.add_route('/users', users_resource)

    def test_get(self):
        """GET /users works."""
        pass


class CheckEmailAddressResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(CheckEmailAddressResourceTestCase, self).setUp()

        email_address_validator = mock()
        sql_engine = mock()
        check_email_address_resource = identity.CheckEmailAddressResource(
            email_address_validator=email_address_validator,
            sql_engine=sql_engine)
        self.api.add_route('/users/check-email', check_email_address_resource)

    def test_get(self):
        """GET /users/check-email works."""
        pass


if __name__ == '__main__':
    unittest.main()
