"""Create the Users table."""

import secrets
from yoyo import step


step("""
CREATE TABLE Users (
    id INTEGER NOT NULL,
    external_id VARCHAR({external_id_size}),
    status VARCHAR(8),
    name VARCHAR,
    time_joined DATETIME,
    time_left DATETIME,
    PRIMARY KEY (id),
    CHECK (status IN ('ACTIVE', 'INACTIVE'))
)
""".format(external_id_size=secrets.USER_SECRET_SIZE), """
DROP TABLE Users
""")
