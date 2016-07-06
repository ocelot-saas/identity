"""Create the AuthTokens table."""

import secrets
from yoyo import step


__depends__ = ['0004.create_facebook_access_info']


step("""
CREATE TABLE identity.auth_token (
    token CHAR({token_size}) NOT NULL,
    expiry_time TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (token),
    FOREIGN KEY (user_id) REFERENCES identity.User(id)
)""".format(token_size=secrets.USER_SECRET_SIZE), """
DROP TABLE identity.AuthTokens
""")
