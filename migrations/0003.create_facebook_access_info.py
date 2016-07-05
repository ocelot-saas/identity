"""Create the FacebookAccessInfo table."""

from yoyo import step


__depends__ = ['0002.create_basic_access_info']


step("""
CREATE TABLE FacebookAccessInfo (
    user_id INTEGER NOT NULL,
    access_token VARCHAR,
    expiry_time DATETIME,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
)""", """
DROP TABLE FacebookAccessInfo
""")
