# Procfile for Sevalla Multi-Process Support
# This allows running web server, Celery worker, and Celery beat together

# Main web server (serves Django API + React frontend)
web: cd backend && python manage.py migrate --noinput && gunicorn genienews_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

# Celery worker for async tasks (feed ingestion, AI curation, etc.)
worker: cd backend && celery -A genienews_backend worker -l info --concurrency=2

# Celery beat for scheduled tasks (weekly feed ingestion, hourly curation)
beat: cd backend && celery -A genienews_backend beat -l info

