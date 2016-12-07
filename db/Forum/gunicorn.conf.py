bind = "127.0.0.1:8000"                   # Don't use port 80 becaue nginx occupied it already. 
errorlog = '/Users/serqeycheremisin/venv/logs/gunicorn-error.log'  # Make sure you have the log folder create
accesslog = '/Users/serqeycheremisin/venv/logs/gunicorn-access.log'
backlog = 2048
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

