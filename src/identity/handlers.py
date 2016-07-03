"""Handlers for HTTP resources."""

import falcon


class UsersResource(object):
    """A collection of users.

    Handles creation, and 'retrieval' via auth token.
    """

    def __init__(self, email_address_validator, password_validator):
        self._email_address_validator = email_address_validator
        self._password_validator = password_validator

    def on_get(self, req, resp):
        """GET a particular user.

        GET with a given auth token retrieves the respective user.
        GET with an email and password retrieves the respective user.
        """

        resp.status = falcon.HTTP_200
        resp.body = 'Hello falcon'

    def on_post(self, req, resp):
        """POST creates a user, with a given email and password."""
        resp.status = falcon.HTTP_200
        resp.body = 'Hello falcon'

    def _on_get_auth_token(self, req, resp):
        pass

    def _on_get_email_address_and_pass(self, req, resp):
        pass


class CheckEmailAddressResource(object):
    """An RPC style resource for checking whether an email is in use or not."""

    def __init__(self, email_address_validator):
        self._email_address_validator = email_address_validator

    def on_get(self, req, resp):
        """GET checks to see if a particular email is in use."""

        resp.status = falcon.HTTP_200
        resp.body = 'Hello falcon'
