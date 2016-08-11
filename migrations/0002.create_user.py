"""Create the Users table."""

from yoyo import step


__depends__ = ['0001.create_schema']

step("""
CREATE TABLE identity.user (
    id SERIAL,
    auth0_user_id_hash CHAR(64) NOT NULL,
    time_joined TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX user_auth0_user_id_hash ON identity.user(auth0_user_id_hash);
""", """
DROP INDEX IF EXISTS identity.user_auth0_user_id_hash;
DROP TABLE IF EXISTS identity.user;
""")
