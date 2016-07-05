#!/usr/bin/python3

from yoyo import read_migrations, get_backend
import identity.config as config


def main():
    """Migrations script entry point."""
    backend = get_backend(config.db_path)
    migrations = read_migrations(config.migrations_path)
    backend.apply_migrations(backend.to_apply(migrations))


if __name__ == '__main__':
    main()
