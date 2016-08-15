import unittest

import falcon.testing
from mockito import mock

import identity.handlers as identity


class UserResourceTestCase(falcon.testing.TestCase):
    def setUp(self):
        super(UserResourceTestCase, self).setUp()

        auth0_client = mock()
        auth0_user_validator = mock()
        access_token_header_validator = mock()
        the_clock = mock()
        sql_engine = mock()

        user_resource = identity.UserResource(
            auth0_client=auth0_client,
            auth0_user_validator=auth0_user_validator,
            access_token_header_validator=access_token_header_validator,
            the_clock=the_clock,
            sql_engine=sql_engine)

        self.api.add_route('/user', user_resource)

    def test_post(self):
        """GET /user works."""
        pass

    def test_get(self):
        """GET /user works."""
        pass


if __name__ == '__main__':
    unittest.main()
