import multiprocessing
import os


address = '0.0.0.0'
port = int(os.environ.get('PORT', '10000'))
bind = '{}:{}'.format(address, port)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
db_path = 'sqlite:////ocelot/var/db/identity/db'
