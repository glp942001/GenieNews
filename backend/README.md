# GenieNews Backend

Django REST API backend for GenieNews with PostgreSQL (pgvector), Redis, and Celery for AI-powered news curation.

## Quick Links

- **Main README**: [../README.md](../README.md)
- **Setup Guide**: [../SETUP.md](../SETUP.md)
- **Deployment Guide**: [../DEPLOYMENT.md](../DEPLOYMENT.md)
- **Frontend README**: [../frontend/README.md](../frontend/README.md)

## Features

- Django 5.2 with Django REST Framework
- PostgreSQL with pgvector extension for vector similarity search
- Redis for Celery task queue
- CORS enabled for React frontend
- Models for news sources, raw articles, curated content, and user interactions
- RESTful API endpoints for articles
- Celery tasks for feed ingestion and AI curation (placeholders)

## Tech Stack

- **Framework**: Django 5.2.7, Django REST Framework 3.16.1
- **Database**: PostgreSQL 16 with pgvector
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery 5.5.3
- **Python**: 3.14+

## Prerequisites

- Python 3.14+
- Docker and Docker Compose
- Virtual environment (venv)

## Setup Instructions

### 1. Virtual Environment

Create and activate the virtual environment:

```bash
# From project root
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Docker Services

Start PostgreSQL and Redis:

```bash
docker compose up -d
```

Check services are running:

```bash
docker compose ps
```

### 4. Database Setup

The pgvector extension is automatically enabled. Run migrations:

```bash
python manage.py migrate
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 7. Start Celery Worker (Optional)

In a separate terminal:

```bash
cd backend
source ../venv/bin/activate
celery -A genienews_backend worker -l info
```

## API Endpoints

### Articles

- `GET /api/articles/` - List all curated articles (paginated)
  - Query params: `ordering` (e.g., `-created_at`, `relevance_score`)
- `GET /api/articles/{id}/` - Get article details

### User Interactions

- `GET /api/interactions/` - List user interactions
- `POST /api/interactions/` - Create interaction
- `GET /api/interactions/{id}/` - Get interaction details

### Admin Panel

- `http://localhost:8000/admin/` - Django admin interface

## Project Structure

```
backend/
├── genienews_backend/      # Django project settings
│   ├── settings.py         # Configuration with env vars
│   ├── celery.py          # Celery configuration
│   └── urls.py            # Main URL routing
├── news/                   # Main Django app
│   ├── models.py          # Data models (Source, Article, etc.)
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API viewsets
│   ├── urls.py            # API URL routing
│   ├── tasks.py           # Celery tasks (placeholders)
│   └── admin.py           # Django admin config
├── docker-compose.yml     # PostgreSQL + Redis services
├── .env                   # Environment variables
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Models

### Source
RSS/Atom feed sources for news articles.

### ArticleRaw
Raw article data ingested from feeds.

### MediaAsset
Images and videos associated with articles.

### ArticleCurated
AI-enhanced articles with summaries, tags, and vector embeddings.

### UserInteraction
User engagement tracking (views, likes, shares, bookmarks).

## Environment Variables

See `.env` file for configuration:

- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - PostgreSQL credentials
- `REDIS_URL` - Redis connection
- `DJANGO_SECRET_KEY` - Django secret
- `DJANGO_DEBUG` - Debug mode (True/False)
- `CELERY_BROKER_URL` - Celery broker

## Docker Services

### PostgreSQL
- Port: 5432
- Image: pgvector/pgvector:pg16
- Data: Persisted in Docker volume

### Redis
- Port: 6379
- Image: redis:7-alpine
- Data: Persisted in Docker volume

## Development Commands

```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Start Celery worker
celery -A genienews_backend worker -l info

# Start Celery beat (for scheduled tasks)
celery -A genienews_backend beat -l info

# Django shell
python manage.py shell

# Stop Docker services
docker compose down

# View Docker logs
docker compose logs -f postgres
docker compose logs -f redis
```

## Testing the API

Using curl:

```bash
# List articles
curl http://localhost:8000/api/articles/

# Get article details
curl http://localhost:8000/api/articles/1/

# Create interaction
curl -X POST http://localhost:8000/api/interactions/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "article": 1, "action": "view"}'
```

## Next Steps

1. **Implement Feed Ingestion**: Complete `ingest_feeds_task()` in `news/tasks.py`
   - Parse RSS/Atom feeds with feedparser
   - Create ArticleRaw entries
   - Extract media assets

2. **Implement AI Curation**: Complete `curate_articles_task()` in `news/tasks.py`
   - Generate AI summaries
   - Create embeddings for vector search
   - Calculate relevance scores

3. **Add Authentication**: Implement user authentication if needed

4. **Vector Search**: Add similarity search endpoint using pgvector

5. **Scheduled Tasks**: Configure Celery Beat for periodic ingestion

## Troubleshooting

### PostgreSQL connection issues
- Ensure Docker containers are running: `docker compose ps`
- Check logs: `docker compose logs postgres`
- Verify credentials in `.env` match `docker-compose.yml`

### Redis connection issues
- Check Redis is running: `docker compose ps`
- Test connection: `redis-cli ping`

### Celery not picking up tasks
- Ensure Redis is running
- Check Celery worker logs
- Verify `CELERY_BROKER_URL` in `.env`

## License

MIT

