"""Create the BasicAccessInfo table."""

import secrets
from yoyo import step


__depends__ = ['0002.create_user']


step("""
CREATE TABLE identity.BasicAccessInfo (
    user_id INTEGER NOT NULL,
    email_address VARCHAR NOT NULL,
    hidden_password VARCHAR({hidden_password_size}) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES identity.User(id)
)
""".format(hidden_password_size=secrets.HIDDEN_PASSWORD_SIZE), """
DROP TABLE identity.BasicAccessInfo
""")
