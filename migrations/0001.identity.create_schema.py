"""Crete the schema for the identity service."""

from yoyo import step


step("""
CREATE SCHEMA identity;
""", """
DROP SCHEMA IF EXISTS identity;
""")
