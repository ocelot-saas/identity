"""Create the AuthTokens table."""

from yoyo import step


__depends__ = ['0001.create_users']


step("""
CREATE TABLE "AuthTokens" (
    token VARCHAR NOT NULL,
    expiry_time DATETIME,
    user_id INTEGER,
    PRIMARY KEY (token),
    FOREIGN KEY(user_id) REFERENCES "Users" (id)
)""", """
DROP TABLE AuthTokens
""")
