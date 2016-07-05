"""Create the BasicAccessInfo table."""

import secrets
from yoyo import step


__depends__ = ['0001.create_users']


step("""
CREATE TABLE BasicAccessInfo (
    user_id INTEGER NOT NULL,
    email_address VARCHAR,
    hidden_password VARCHAR({hidden_password_size}),
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
)
""".format(hidden_password_size=secrets.HIDDEN_PASSWORD_SIZE), """
DROP TABLE BasicAccessInfo
""")
