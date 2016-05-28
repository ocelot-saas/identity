import multiprocessing
import os


address = '0.0.0.0'
port = int(os.environ['PORT'])
bind = '{}:{}'.format(address, port)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
