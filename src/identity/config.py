import multiprocessing

address = '0.0.0.0'
port = 10000
bind = '{}:{}'.format(address, port)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
