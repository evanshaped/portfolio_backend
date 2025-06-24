# Run gunicorn with this config file via
# gunicorn myapp.wsgi:application -c /path/to/gunicorn.conf.py

bind = '0.0.0.0:8000'
workers = 3
# accesslog = '/var/log/gunicorn.access.log'   # Default None (use '-' for stdout)
# errorlog = '/var/log/gunicorn.error.log'   # Default '-' (stderr)
accesslog = '-'
errorlog = '-'
capture_output = True   # Redirect stdout/stderr (Django output) to error log
loglevel = 'debug'   # Options are: debug, info, warning, error, critical