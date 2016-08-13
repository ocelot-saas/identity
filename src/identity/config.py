import multiprocessing
import os

# Application config.
ENV = os.getenv('ENV')
ADDRESS = '0.0.0.0'
PORT = os.getenv('PORT')
MIGRATIONS_PATH = os.getenv('MIGRATIONS_PATH')
DATABASE_URL = os.getenv('DATABASE_URL')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
CLIENTS = os.getenv('CLIENTS').split(',')

# WSGI config. Not exported, technically.
bind = '{}:{}'.format(ADDRESS, PORT)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
