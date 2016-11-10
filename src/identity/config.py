import json
import multiprocessing
import os


# Application config.
ENV = os.getenv('ENV')
ADDRESS = os.getenv('ADDRESS')
PORT = os.getenv('PORT')
MASTER_DOMAIN = os.getenv('MASTER_DOMAIN')
MIGRATIONS_PATH = os.getenv('MIGRATIONS_PATH')
DATABASE_URL = os.getenv('DATABASE_URL')
CLIENTS = ['http://{}'.format(c) for c in os.getenv('CLIENTS').split(',')]

if ENV == 'LOCAL':
    with open('/ocelot-saas/var/secrets.json') as f:
        secrets = json.load(f)
        AUTH0_DOMAIN = secrets['AUTH0_DOMAIN']
else:
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
