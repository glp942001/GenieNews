# GenieNews Fly.io Deployment Guide

This guide walks you through deploying GenieNews (backend + frontend) to Fly.io.

## Prerequisites

1. Install flyctl CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Sign up for Fly.io account: https://fly.io/app/sign-up
3. Login to flyctl: `flyctl auth login`

## Architecture Overview

- **Backend**: Django REST API with Celery workers and beat scheduler
- **Frontend**: React/Vite SPA served via nginx
- **Database**: Fly.io PostgreSQL with pgvector extension
- **Cache/Queue**: Fly.io Redis for Celery
- **Storage**: Persistent volume for media files (audio segments)

## Part 1: Deploy Backend

### 1. Create Backend App

```bash
cd backend
flyctl apps create genienews-backend
```

### 2. Provision PostgreSQL Database

Create a PostgreSQL database with pgvector extension:

```bash
# Create postgres cluster
flyctl postgres create --name genienews-db --region sjc

# Attach to backend app
flyctl postgres attach genienews-db --app genienews-backend
```

This will automatically set the `DATABASE_URL` secret.

**Important**: Enable pgvector extension:

```bash
# Connect to postgres
flyctl postgres connect -a genienews-db

# In postgres shell:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Provision Redis

Option A: Use Upstash Redis (Recommended - Free tier available)

```bash
# Visit https://upstash.com/ and create a Redis database
# Copy the REDIS_URL and set it as a secret:
flyctl secrets set REDIS_URL="redis://default:password@host:port" --app genienews-backend
```

Option B: Use Fly.io Redis (Coming soon to all regions)

```bash
flyctl redis create --name genienews-redis --region sjc
flyctl redis attach genienews-redis --app genienews-backend
```

### 4. Create Persistent Volume for Media Files

```bash
flyctl volumes create genienews_media --size 1 --region sjc --app genienews-backend
```

### 5. Set Backend Secrets

Generate a Django secret key:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set all required secrets:

```bash
cd backend

# Django configuration
flyctl secrets set DJANGO_SECRET_KEY="your-generated-secret-key" --app genienews-backend
flyctl secrets set DJANGO_DEBUG="False" --app genienews-backend
flyctl secrets set DJANGO_ALLOWED_HOSTS=".fly.dev" --app genienews-backend

# OpenAI API (required for AI features)
flyctl secrets set OPENAI_API_KEY="sk-your-openai-api-key" --app genienews-backend

# Optional: Override defaults
flyctl secrets set AI_MODEL="gpt-4" --app genienews-backend
flyctl secrets set EMBEDDING_MODEL="text-embedding-3-small" --app genienews-backend
flyctl secrets set TTS_VOICE="nova" --app genienews-backend
flyctl secrets set TTS_SPEED="1.15" --app genienews-backend
flyctl secrets set TTS_MODEL="tts-1-hd" --app genienews-backend

# Frontend URL (will be set after frontend deployment)
# flyctl secrets set FRONTEND_URL="https://genienews-frontend.fly.dev" --app genienews-backend
```

### 6. Deploy Backend

```bash
cd backend
flyctl deploy --app genienews-backend
```

This will:
- Build the Docker image
- Run migrations (via release command)
- Start the web server, Celery worker, and Celery beat processes
- Health checks will ensure the app is running

### 7. Verify Backend Deployment

```bash
# Check app status
flyctl status --app genienews-backend

# View logs
flyctl logs --app genienews-backend

# Test health check
curl https://genienews-backend.fly.dev/health/

# Test API
curl https://genienews-backend.fly.dev/api/articles/
```

### 8. Scale Backend Processes (Optional)

By default, all processes run on a single machine. For production, you may want to scale:

```bash
# Scale web processes
flyctl scale count app=2 --app genienews-backend

# You can run worker and beat on separate machines if needed
flyctl scale count worker=1 beat=1 --app genienews-backend
```

## Part 2: Deploy Frontend

### 1. Create Frontend App

```bash
cd frontend
flyctl apps create genienews-frontend
```

### 2. Deploy Frontend

The `fly.toml` already includes the backend API URL. Deploy:

```bash
cd frontend
flyctl deploy --app genienews-frontend
```

This will:
- Build the React app with Vite
- Serve it with nginx
- Configure SPA routing

### 3. Verify Frontend Deployment

```bash
# Check app status
flyctl status --app genienews-frontend

# View logs
flyctl logs --app genienews-frontend

# Open in browser
flyctl open --app genienews-frontend
```

## Part 3: Final Configuration

### 1. Update Backend CORS Settings

Now that the frontend is deployed, update the backend to allow CORS from the frontend:

```bash
flyctl secrets set FRONTEND_URL="https://genienews-frontend.fly.dev" --app genienews-backend
```

This will automatically redeploy the backend with updated CORS settings.

### 2. Test End-to-End

1. Visit your frontend: `https://genienews-frontend.fly.dev`
2. Verify articles load from the backend
3. Test the AI chat feature
4. Test audio generation

## Part 4: Populate Data (Initial Setup)

### 1. Create Admin User

```bash
flyctl ssh console --app genienews-backend

# In the SSH session:
python manage.py createsuperuser
exit
```

### 2. Access Admin Panel

Visit: `https://genienews-backend.fly.dev/admin/`

### 3. Import News Sources

You can import sources via the admin panel or run management commands:

```bash
flyctl ssh console --app genienews-backend

# Import sources (if you have a command)
python manage.py import_sources

# Manually trigger feed ingestion
python manage.py update_rss_feeds
exit
```

### 4. Trigger Initial Curation

```bash
flyctl ssh console --app genienews-backend
python manage.py test_curation
exit
```

## Monitoring and Maintenance

### View Logs

```bash
# Backend logs (all processes)
flyctl logs --app genienews-backend

# Frontend logs
flyctl logs --app genienews-frontend

# Follow logs in real-time
flyctl logs --app genienews-backend -f
```

### Check Database

```bash
# Connect to PostgreSQL
flyctl postgres connect -a genienews-db

# Run queries
SELECT COUNT(*) FROM news_articleraw;
SELECT COUNT(*) FROM news_articlecurated;
\q
```

### Check Redis

```bash
# If using Fly.io Redis
flyctl redis connect genienews-redis
```

### SSH into App

```bash
# Backend
flyctl ssh console --app genienews-backend

# Frontend (nginx)
flyctl ssh console --app genienews-frontend
```

### Restart App

```bash
flyctl apps restart genienews-backend
flyctl apps restart genienews-frontend
```

### Scale Resources

```bash
# Increase memory
flyctl scale memory 2048 --app genienews-backend

# Add more instances
flyctl scale count 2 --app genienews-backend
```

## Updating the App

### Backend Updates

```bash
cd backend
flyctl deploy --app genienews-backend
```

Migrations will run automatically via the release command.

### Frontend Updates

```bash
cd frontend
flyctl deploy --app genienews-frontend
```

## Troubleshooting

### Backend won't start

1. Check logs: `flyctl logs --app genienews-backend`
2. Verify secrets are set: `flyctl secrets list --app genienews-backend`
3. Check health endpoint: `curl https://genienews-backend.fly.dev/health/`
4. SSH and check manually: `flyctl ssh console --app genienews-backend`

### Database connection issues

1. Verify DATABASE_URL: `flyctl secrets list --app genienews-backend`
2. Check postgres is running: `flyctl status --app genienews-db`
3. Test connection: `flyctl postgres connect -a genienews-db`

### Redis connection issues

1. Verify REDIS_URL: `flyctl secrets list --app genienews-backend`
2. Check Redis is accessible (if using Upstash, check their dashboard)

### Celery tasks not running

1. Check worker logs: `flyctl logs --app genienews-backend | grep worker`
2. Verify Redis connection
3. SSH and test manually:
   ```bash
   flyctl ssh console --app genienews-backend
   celery -A genienews_backend inspect active
   ```

### Frontend not loading

1. Check logs: `flyctl logs --app genienews-frontend`
2. Verify nginx is serving files: `flyctl ssh console --app genienews-frontend`
3. Check if build was successful during deployment

### CORS errors

1. Verify FRONTEND_URL is set: `flyctl secrets list --app genienews-backend`
2. Check Django settings include `.fly.dev` in CORS_ALLOWED_ORIGINS
3. Redeploy backend after updating CORS settings

## Cost Optimization

### Free Tier

Fly.io offers generous free tier:
- 3 shared-cpu VMs with 256MB RAM
- 3GB persistent storage
- 160GB outbound data transfer

### Optimize Costs

1. **Auto-stop machines**: Already enabled in `fly.toml`
   - Machines stop when idle
   - Auto-start on incoming requests

2. **Reduce memory**: If app runs fine with less
   ```bash
   flyctl scale memory 512 --app genienews-backend
   ```

3. **Reduce processes**: Run worker/beat on-demand instead of 24/7
   - Comment out worker/beat in `fly.toml` [processes]
   - Run them manually when needed via SSH

4. **Use external services**:
   - Upstash Redis (free tier)
   - Supabase PostgreSQL (free tier)

## Security Best Practices

1. **Rotate secrets regularly**
   ```bash
   flyctl secrets set DJANGO_SECRET_KEY="new-key" --app genienews-backend
   ```

2. **Use strong passwords** for admin users

3. **Enable 2FA** on your Fly.io account

4. **Monitor logs** for suspicious activity

5. **Keep dependencies updated**
   ```bash
   pip list --outdated
   npm outdated
   ```

6. **Set up custom domain with SSL** (optional)
   ```bash
   flyctl certs create yourdomain.com --app genienews-frontend
   ```

## Custom Domain Setup (Optional)

### Frontend Domain

```bash
# Add certificate
flyctl certs create genienews.com --app genienews-frontend

# Get DNS instructions
flyctl certs show genienews.com --app genienews-frontend

# Add DNS records as instructed (A and AAAA records)
```

### Backend Domain

```bash
# Add certificate
flyctl certs create api.genienews.com --app genienews-backend

# Get DNS instructions and configure DNS
flyctl certs show api.genienews.com --app genienews-backend
```

Then update:
1. Frontend `fly.toml` VITE_API_URL to use custom domain
2. Backend CORS_ALLOWED_ORIGINS to include custom frontend domain

## Backup and Recovery

### Database Backups

Fly.io PostgreSQL automatically backs up daily. Manual backup:

```bash
flyctl postgres backup create --app genienews-db
flyctl postgres backup list --app genienews-db
```

### Volume Snapshots

```bash
# List volumes
flyctl volumes list --app genienews-backend

# Create snapshot
flyctl volumes snapshots create <volume-id> --app genienews-backend

# List snapshots
flyctl volumes snapshots list <volume-id> --app genienews-backend
```

## Support

- Fly.io Docs: https://fly.io/docs/
- Fly.io Community: https://community.fly.io/
- Django Docs: https://docs.djangoproject.com/
- Celery Docs: https://docs.celeryproject.org/

---

**Your GenieNews app is now live on Fly.io! 🚀**

- Backend: `https://genienews-backend.fly.dev`
- Frontend: `https://genienews-frontend.fly.dev`

