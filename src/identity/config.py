import multiprocessing
import os

# Application config.
ADDRESS = '0.0.0.0'
PORT = int(os.environ.get('PORT', '10000'))
MIGRATIONS_PATH = '/ocelot/pack/identity/migrations'
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////ocelot/var/db/identity/db')

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
