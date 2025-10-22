# GenieNews Initial Setup Guide

This guide will help you set up GenieNews for the first time, both for local development and production deployment on Fly.io.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Fly.io Production Setup](#flyio-production-setup)
3. [Initial Data Population](#initial-data-population)
4. [Testing Your Setup](#testing-your-setup)

## Local Development Setup

### 1. Prerequisites

Install the following on your local machine:

- **Python 3.11+**: https://www.python.org/downloads/
- **Node.js 18+**: https://nodejs.org/
- **PostgreSQL 16**: https://www.postgresql.org/download/
- **Redis 7**: https://redis.io/download/
- **Git**: https://git-scm.com/downloads

Alternatively, use Docker for PostgreSQL and Redis:
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/

### 2. Clone Repository

```bash
git clone <your-repo-url>
cd GenieNews
```

### 3. Backend Setup

#### 3.1 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

#### 3.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 3.3 Start PostgreSQL and Redis

**Option A: Using Docker (Recommended)**

Create `backend/docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: genienews
      POSTGRES_USER: genienews_user
      POSTGRES_PASSWORD: genienews_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Start services:

```bash
cd backend
docker-compose up -d
```

**Option B: Using Local Installation**

Install PostgreSQL and Redis using your package manager, then start the services.

#### 3.4 Configure Environment Variables

Create `backend/.env`:

```bash
cd backend
cp .env.example .env  # If you have one, otherwise create manually
```

Edit `.env`:

```bash
# Environment
ENVIRONMENT=development

# Django Configuration
DJANGO_SECRET_KEY=your-local-dev-secret-key-change-this
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=genienews
DB_USER=genienews_user
DB_PASSWORD=genienews_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Optional: Leave defaults for these
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000
TTS_VOICE=nova
TTS_SPEED=1.15
TTS_MODEL=tts-1-hd
```

#### 3.5 Enable pgvector Extension

```bash
# Connect to PostgreSQL
psql -U genienews_user -d genienews -h localhost

# In psql shell:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### 3.6 Run Migrations

```bash
cd backend
python manage.py migrate
```

#### 3.7 Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### 3.8 Start Development Server

```bash
python manage.py runserver
```

Backend is now running at: http://localhost:8000

#### 3.9 Start Celery (Optional, in separate terminals)

Terminal 2 - Celery Worker:
```bash
cd backend
source ../venv/bin/activate
celery -A genienews_backend worker -l info
```

Terminal 3 - Celery Beat (Scheduler):
```bash
cd backend
source ../venv/bin/activate
celery -A genienews_backend beat -l info
```

### 4. Frontend Setup

#### 4.1 Install Dependencies

```bash
cd frontend
npm install
```

#### 4.2 Configure Environment

Create `frontend/.env`:

```bash
cd frontend
cp env.example .env
```

Edit `.env`:

```bash
VITE_API_URL=http://localhost:8000
```

#### 4.3 Start Development Server

```bash
npm run dev
```

Frontend is now running at: http://localhost:3000

### 5. Verify Local Setup

1. **Backend API**: http://localhost:8000/api/articles/
2. **Admin Panel**: http://localhost:8000/admin/ (login with superuser)
3. **Health Check**: http://localhost:8000/health/
4. **Frontend**: http://localhost:3000/

## Fly.io Production Setup

### 1. Prerequisites

#### 1.1 Install flyctl

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

#### 1.2 Sign Up and Login

```bash
# Sign up (if you don't have an account)
flyctl auth signup

# Or login (if you have an account)
flyctl auth login
```

### 2. Backend Setup

#### 2.1 Create Backend App

```bash
cd backend
flyctl apps create genienews-backend
```

#### 2.2 Provision PostgreSQL

```bash
# Create PostgreSQL cluster
flyctl postgres create \
  --name genienews-db \
  --region sjc \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1

# Attach to backend app
flyctl postgres attach genienews-db --app genienews-backend
```

This automatically sets `DATABASE_URL` secret.

#### 2.3 Enable pgvector Extension

```bash
# Connect to PostgreSQL
flyctl postgres connect -a genienews-db

# In psql shell:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### 2.4 Provision Redis

**Option A: Upstash Redis (Recommended - Has Free Tier)**

1. Go to https://upstash.com/
2. Sign up and create a Redis database
3. Copy the Redis URL
4. Set as secret:

```bash
flyctl secrets set REDIS_URL="redis://default:password@host:port" --app genienews-backend
```

**Option B: Fly.io Redis** (if available in your region)

```bash
flyctl redis create --name genienews-redis --region sjc
flyctl redis attach genienews-redis --app genienews-backend
```

#### 2.5 Create Volume for Media Files

```bash
flyctl volumes create genienews_media \
  --size 1 \
  --region sjc \
  --app genienews-backend
```

#### 2.6 Generate Django Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output.

#### 2.7 Set Backend Secrets

```bash
cd backend

# Required secrets
flyctl secrets set \
  DJANGO_SECRET_KEY="<paste-generated-key>" \
  DJANGO_DEBUG="False" \
  DJANGO_ALLOWED_HOSTS=".fly.dev" \
  OPENAI_API_KEY="sk-your-openai-api-key" \
  --app genienews-backend

# Optional: Override defaults
flyctl secrets set \
  AI_MODEL="gpt-4" \
  EMBEDDING_MODEL="text-embedding-3-small" \
  TTS_VOICE="nova" \
  TTS_SPEED="1.15" \
  TTS_MODEL="tts-1-hd" \
  --app genienews-backend
```

Note: Don't set `FRONTEND_URL` yet - we'll do that after frontend is deployed.

#### 2.8 Deploy Backend

```bash
cd backend
flyctl deploy --app genienews-backend
```

This will:
- Build Docker image
- Run migrations
- Start web server, Celery worker, and beat scheduler

#### 2.9 Verify Backend

```bash
# Check status
flyctl status --app genienews-backend

# View logs
flyctl logs --app genienews-backend

# Test health check
curl https://genienews-backend.fly.dev/health/

# Test API
curl https://genienews-backend.fly.dev/api/articles/
```

#### 2.10 Create Superuser

```bash
flyctl ssh console --app genienews-backend

# In SSH session:
python manage.py createsuperuser
exit
```

Visit https://genienews-backend.fly.dev/admin/ and login.

### 3. Frontend Setup

#### 3.1 Create Frontend App

```bash
cd frontend
flyctl apps create genienews-frontend
```

#### 3.2 Deploy Frontend

```bash
cd frontend
flyctl deploy --app genienews-frontend
```

This will:
- Build React app with Vite
- Create nginx container
- Deploy to Fly.io

#### 3.3 Verify Frontend

```bash
# Check status
flyctl status --app genienews-frontend

# View logs
flyctl logs --app genienews-frontend

# Open in browser
flyctl open --app genienews-frontend
```

### 4. Final Configuration

#### 4.1 Update Backend CORS

Now that frontend is deployed, update backend to allow CORS:

```bash
flyctl secrets set FRONTEND_URL="https://genienews-frontend.fly.dev" --app genienews-backend
```

This will automatically trigger a redeploy.

#### 4.2 Verify End-to-End

1. Visit: https://genienews-frontend.fly.dev
2. Check if articles load (they won't if database is empty)
3. Test health check works

## Initial Data Population

### 1. Add News Sources

#### Via Admin Panel

1. Go to https://genienews-backend.fly.dev/admin/
2. Login with superuser credentials
3. Navigate to "Sources"
4. Add RSS feed sources manually

#### Via Django Shell

```bash
flyctl ssh console --app genienews-backend

# In SSH session:
python manage.py shell

# In Python shell:
from news.models import Source

# Example: Add TechCrunch AI
Source.objects.create(
    name="TechCrunch AI",
    feed_url="https://techcrunch.com/tag/artificial-intelligence/feed/",
    site_url="https://techcrunch.com",
    active=True
)

# Add more sources...
exit()
exit
```

### 2. Ingest Articles

#### Manual Ingestion

```bash
flyctl ssh console --app genienews-backend

# Run feed ingestion command
python manage.py update_rss_feeds
exit
```

#### Trigger Celery Task

```bash
flyctl ssh console --app genienews-backend

python manage.py shell

# In Python shell:
from news.tasks import ingest_all_feeds_task
ingest_all_feeds_task.delay()
exit()
exit
```

### 3. Curate Articles

```bash
flyctl ssh console --app genienews-backend

# Run curation
python manage.py test_curation
exit
```

### 4. Verify Data

```bash
flyctl postgres connect -a genienews-db

# In psql:
SELECT COUNT(*) FROM news_articleraw;
SELECT COUNT(*) FROM news_articlecurated;
SELECT COUNT(*) FROM news_source;
\q
```

## Testing Your Setup

### Local Testing

1. **Backend API**:
   ```bash
   curl http://localhost:8000/api/articles/
   ```

2. **Health Check**:
   ```bash
   curl http://localhost:8000/health/
   ```

3. **Frontend**:
   Open http://localhost:3000 in browser

4. **Admin Panel**:
   Open http://localhost:8000/admin/ and login

### Production Testing

1. **Backend API**:
   ```bash
   curl https://genienews-backend.fly.dev/api/articles/
   ```

2. **Health Check**:
   ```bash
   curl https://genienews-backend.fly.dev/health/
   ```

3. **Frontend**:
   Visit https://genienews-frontend.fly.dev

4. **Admin Panel**:
   Visit https://genienews-backend.fly.dev/admin/

### Test Celery Tasks

```bash
# SSH into backend
flyctl ssh console --app genienews-backend

# Check active tasks
celery -A genienews_backend inspect active

# Check scheduled tasks
celery -A genienews_backend inspect scheduled

# Trigger test task
python manage.py shell
>>> from news.tasks import ingest_all_feeds_task
>>> result = ingest_all_feeds_task.delay()
>>> result.id
```

## Common Issues

### Issue: Database connection error

**Solution**: Verify DATABASE_URL is set:
```bash
flyctl secrets list --app genienews-backend
```

### Issue: Redis connection error

**Solution**: Verify REDIS_URL is set:
```bash
flyctl secrets list --app genienews-backend
```

### Issue: pgvector extension not found

**Solution**: Connect to postgres and enable extension:
```bash
flyctl postgres connect -a genienews-db
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: Frontend can't reach backend

**Solution**: 
1. Check CORS settings in backend
2. Verify FRONTEND_URL is set
3. Check if backend is running: `flyctl status --app genienews-backend`

### Issue: Celery tasks not running

**Solution**:
1. Check worker is running: `flyctl logs --app genienews-backend | grep worker`
2. Verify Redis connection
3. Check task queue: SSH in and run `celery -A genienews_backend inspect active`

## Next Steps

After setup is complete:

1. **Configure Scheduled Tasks**: Celery Beat is already running with weekly schedules
2. **Add More Sources**: Populate with relevant RSS feeds
3. **Monitor Usage**: Watch Fly.io dashboard for resource usage
4. **Set Up Monitoring**: Consider adding Sentry or similar
5. **Custom Domain**: Configure custom domain if desired (see DEPLOYMENT.md)
6. **Backup Strategy**: Set up regular backups (automatic for Postgres on Fly.io)

## Useful Commands

### Quick Reference

```bash
# Deploy backend
./deploy.sh deploy-backend

# Deploy frontend
./deploy.sh deploy-frontend

# Deploy both
./deploy.sh deploy-all

# Check status
./deploy.sh status-all

# View logs
./deploy.sh logs-backend
./deploy.sh logs-frontend

# SSH into backend
./deploy.sh ssh-backend

# Open apps
./deploy.sh open-all
```

## Getting Help

- **Fly.io Docs**: https://fly.io/docs/
- **Django Docs**: https://docs.djangoproject.com/
- **Celery Docs**: https://docs.celeryproject.org/
- **React Docs**: https://react.dev/

For deployment-specific help, see [DEPLOYMENT.md](./DEPLOYMENT.md).

---

**Congratulations! Your GenieNews app is now set up! 🎉**

