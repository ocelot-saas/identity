"""Create the Users table."""

import secrets
from yoyo import step


__depends__ = ['0001.create_schema']

step("""
CREATE TABLE identity.user (
    id SERIAL,
    external_id CHAR({external_id_size}),
    status CHAR(8) NOT NULL,
    name VARCHAR NOT NULL,
    time_joined TIMESTAMP NOT NULL,
    time_left TIMESTAMP,
    PRIMARY KEY (id),
    CHECK (status IN ('ADDED', 'ACTIVE', 'INACTIVE'))
)
""".format(external_id_size=secrets.USER_SECRET_SIZE), """
DROP TABLE identity.User
""")
