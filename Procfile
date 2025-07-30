release: python manage.py migrate --noinput
web:     gunicorn config.wsgi:application --bind :8000