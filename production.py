bind = '0.0.0.0:8080'
pid = 'gunicorn.pid'
django_settings = 'hydra.settings'
debug = True
errorlog = 'gunicorn_error.log'
workers = 40
max_requests = 200