"""Create the AuthTokens table."""

from yoyo import step


__depends__ = ['0005.create_facebook_access_info']


step("""
CREATE TABLE identity.AuthToken (
    token VARCHAR NOT NULL,
    expiry_time DATETIME NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (token),
    FOREIGN KEY(user_id) REFERENCES identity.User(id)
)""", """
DROP TABLE identity.AuthTokens
""")
