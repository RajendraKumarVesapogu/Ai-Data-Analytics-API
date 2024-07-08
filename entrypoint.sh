#!/bin/sh
python manage.py makemigration --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

python manage.py createsuperuser --username  --noinput

gunicorn Data_Analisys_API.wsgi:application --bind 0.0.0.0:8000

