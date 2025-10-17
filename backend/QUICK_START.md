# GenieNews Backend - Quick Start Guide

## Starting the Backend

### Terminal 1: Start Docker Services
```bash
cd backend
docker compose up -d
```

### Terminal 2: Start Django Server
```bash
cd backend
source ../venv/bin/activate
python manage.py runserver
```

### Terminal 3 (Optional): Start Celery Worker
```bash
cd backend
source ../venv/bin/activate
celery -A genienews_backend worker -l info
```

## Access Points

- **API Base**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin`

## API Endpoints

- `GET /api/articles/` - List curated articles
- `GET /api/articles/{id}/` - Article details
- `GET /api/interactions/` - List interactions
- `POST /api/interactions/` - Create interaction

## Test the API

```bash
# List articles (empty for now)
curl http://localhost:8000/api/articles/

# Check CORS
curl -I http://localhost:8000/api/articles/ -H "Origin: http://localhost:3000"
```

## Stop Services

```bash
# Stop Django (Ctrl+C in Terminal 2)
# Stop Celery (Ctrl+C in Terminal 3)

# Stop Docker
cd backend
docker compose down
```

## Admin Panel

Access http://localhost:8000/admin/ to:
- Add news sources
- View articles
- Check user interactions
- Manage all data

## Common Commands

```bash
# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Create new admin user
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## Next: Implement Feed Ingestion

Edit `news/tasks.py` to implement:
1. `ingest_feeds_task()` - Parse RSS feeds
2. `curate_articles_task()` - AI processing

See `README.md` for full documentation.

