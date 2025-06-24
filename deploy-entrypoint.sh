#!/bin/sh
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn -c '/app/gunicorn.conf.py' djangobackend.wsgi:application