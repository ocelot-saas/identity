"""Create the FacebookAccessInfo table."""

from yoyo import step


__depends__ = ['0003.create_basic_access_info']


step("""
CREATE TABLE identity.FacebookAccessInfo (
    user_id INTEGER NOT NULL,
    access_token VARCHAR NOT NULL,
    expiry_time DATETIME NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES identity.User(id)
)""", """
DROP TABLE identity.FacebookAccessInfo
""")
