"""Create the Users table."""

import secrets
from yoyo import step


__depends__ = ['0001.create_schema.py']


step("""
CREATE TABLE identity.User (
    id SERIAL,
    external_id VARCHAR({external_id_size}) NOT NULL,
    status VARCHAR(8) NOT NULL,
    name VARCHAR NOT NULL,
    time_joined DATETIME NOT NULL,
    time_left DATETIME,
    PRIMARY KEY (id),
    CHECK (status IN ('ACTIVE', 'INACTIVE')),
)
""".format(external_id_size=secrets.USER_SECRET_SIZE), """
DROP TABLE identity.User
""")
