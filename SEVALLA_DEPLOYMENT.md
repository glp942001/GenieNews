# GenieNews Sevalla Deployment Guide

Complete guide for deploying GenieNews to Sevalla with Django serving the React frontend in a unified application.

## Architecture

**Unified Deployment on Sevalla:**
- Django REST API (backend)
- React/Vite SPA (frontend) - served by Django
- PostgreSQL database (with pgvector extension)
- Redis for Celery task queue
- Multi-process: web server, Celery worker, Celery beat

**Benefits:**
- Single deployment
- No CORS issues (same domain)
- Simpler configuration
- One place to manage everything

## Prerequisites

1. **Sevalla Account**: Sign up at https://sevalla.com
2. **Git Repository**: Your code must be in a Git repository (GitHub, GitLab, etc.)
3. **OpenAI API Key**: Get from https://platform.openai.com/api-keys

## Step-by-Step Deployment

### Part 1: Prepare Your Repository

1. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Prepare for Sevalla deployment"
   git push origin main
   ```

2. **Required files (already in your project):**
   - `nixpacks.toml` - Build configuration
   - `Procfile` - Multi-process definitions
   - `backend/requirements.txt` - Python dependencies
   - `frontend/package.json` - Node dependencies

### Part 2: Create Sevalla Project

1. **Login to Sevalla Dashboard**
   - Go to https://sevalla.com/dashboard
   - Click "Create New Project"

2. **Connect Your Repository**
   - Choose "Import from Git"
   - Select your GitHub/GitLab repository
   - Branch: `main` (or your default branch)

3. **Configure Build Settings**
   Sevalla will auto-detect the configuration from `nixpacks.toml`:
   - Framework: Django + Node.js (auto-detected)
   - Build Command: (handled by nixpacks.toml)
   - Start Command: (defined in Procfile)
   - Root Directory: `/` (project root)

### Part 3: Add PostgreSQL Database

1. **Create PostgreSQL Database**
   - In Sevalla dashboard, go to "Databases"
   - Click "Add Database"
   - Type: PostgreSQL 16
   - Name: `genienews-db`
   - Plan: Choose appropriate size (start with smallest)

2. **Enable pgvector Extension**
   - Once database is created, go to database settings
   - Click "Connect" or "SQL Console"
   - Run: `CREATE EXTENSION IF NOT EXISTS vector;`
   - Verify: `\dx` should show vector extension

3. **Link Database to Project**
   - Sevalla will automatically create `DATABASE_URL` environment variable
   - Format: `postgresql://user:password@host:port/database`

### Part 4: Add Redis

1. **Create Redis Instance**
   - In Sevalla dashboard, go to "Databases" or "Redis"
   - Click "Add Redis"
   - Name: `genienews-redis`
   - Plan: Choose appropriate size

2. **Link Redis to Project**
   - Sevalla will automatically create `REDIS_URL` environment variable
   - Format: `redis://host:port/0`

### Part 5: Configure Environment Variables

In Sevalla dashboard, go to your project → "Environment" tab:

#### Required Variables:

```bash
# Django Configuration
DJANGO_SECRET_KEY=<generate-random-50-char-string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.sevalla.com,.sevalla.app
ENVIRONMENT=production

# Database (auto-set by Sevalla)
DATABASE_URL=<auto-provided-by-sevalla>

# Redis (auto-set by Sevalla)
REDIS_URL=<auto-provided-by-sevalla>

# OpenAI API
OPENAI_API_KEY=sk-your-actual-openai-key-here

# AI Configuration (optional, uses defaults if not set)
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000

# TTS Configuration (optional)
TTS_VOICE=nova
TTS_SPEED=1.15
TTS_MODEL=tts-1-hd

# Feed Ingestion (optional)
FEED_FETCH_TIMEOUT=30
FEED_USER_AGENT=GenieNewsBot/1.0
CONTENT_FETCH_TIMEOUT=60
MAX_RETRIES=3
```

#### How to Generate DJANGO_SECRET_KEY:

```python
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

### Part 6: Enable Multi-Process

Sevalla uses the `Procfile` to run multiple processes:

1. **In Sevalla dashboard:**
   - Go to "Processes" or "Scale"
   - Enable:
     - **web**: 1 instance (required)
     - **worker**: 1 instance (for Celery)
     - **beat**: 1 instance (for scheduled tasks)

2. **Scaling (optional):**
   - You can scale `web` and `worker` processes
   - Keep `beat` at 1 (only one scheduler needed)

### Part 7: Deploy

1. **Trigger Deployment**
   - Click "Deploy" button in Sevalla dashboard
   - Or: Push to your main branch (auto-deploys)

2. **Monitor Build**
   - Watch build logs in real-time
   - Build process:
     - Install Python dependencies
     - Install Node dependencies
     - Build React frontend
     - Collect Django static files
     - Run migrations
     - Start Gunicorn server

3. **Check Deployment Status**
   - Status should show "Running"
   - All 3 processes (web, worker, beat) should be active

### Part 8: Verify Deployment

1. **Access Your App**
   - Sevalla will provide URL: `https://your-project.sevalla.app`
   - Frontend should load (React app)
   - API accessible at: `https://your-project.sevalla.app/api/`

2. **Test Health Check**
   ```bash
   curl https://your-project.sevalla.app/health/
   ```
   Should return: `{"status": "healthy", "service": "genienews"}`

3. **Access Admin Panel**
   - Go to: `https://your-project.sevalla.app/admin/`
   - You'll need to create a superuser first

### Part 9: Create Admin User

**Option A: Via Sevalla Console**
1. Go to Sevalla dashboard → "Console" tab
2. Run:
   ```bash
   cd backend && python manage.py createsuperuser
   ```
3. Follow prompts to create admin user

**Option B: Via SSH** (if available)
1. SSH into your Sevalla instance
2. Navigate to project
3. Run: `python manage.py createsuperuser`

### Part 10: Populate Initial Data

1. **Add News Sources**
   - Login to admin: `https://your-project.sevalla.app/admin/`
   - Go to "Sources"
   - Add RSS feed sources:
     - TechCrunch AI: `https://techcrunch.com/tag/artificial-intelligence/feed/`
     - VentureBeat AI: `https://venturebeat.com/category/ai/feed/`
     - The Verge AI: `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml`

2. **Trigger Initial Feed Ingestion**
   - Via console or SSH:
     ```bash
     cd backend && python manage.py update_rss_feeds
     ```

3. **Run AI Curation**
   - Via console:
     ```bash
     cd backend && python manage.py test_curation
     ```

4. **Verify Articles**
   - Visit your app homepage
   - Articles should now appear
   - Check: `https://your-project.sevalla.app/api/articles/`

## Monitoring and Maintenance

### View Logs

In Sevalla dashboard:
- **Application Logs**: Real-time logs from web server
- **Worker Logs**: Celery worker activity
- **Beat Logs**: Scheduled task execution
- **Database Logs**: PostgreSQL queries (if enabled)

### Check Process Status

- **Dashboard → Processes**: Shows all running processes
- Ensure all 3 processes are "Running"

### Monitor Resources

- **Dashboard → Metrics**: CPU, memory, requests
- Scale up if needed

### Restart Processes

If something goes wrong:
- **Dashboard → Processes → Restart**
- Or redeploy: Push to main branch

## Scheduled Tasks

Celery Beat runs these tasks automatically:

- **Weekly Feed Ingestion**: Every Monday at 2 AM UTC
- **Content Fetching**: Every Monday at 4 AM UTC
- **AI Curation**: Every hour on the hour

Verify in logs:
```
Beat logs → Should show scheduled task execution
Worker logs → Should show task processing
```

## Updating Your App

### Deploy Updates

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. **Sevalla auto-deploys** (or click "Deploy" button)
4. **Migrations run automatically** via Procfile

### Manual Migration

If needed:
```bash
# Via Sevalla console
cd backend && python manage.py migrate
```

## Troubleshooting

### Build Fails

**Check build logs:**
- Look for Python or Node errors
- Ensure all dependencies in `requirements.txt` and `package.json`
- Verify Node version compatibility

**Common fixes:**
- Update `nixpacks.toml` if needed
- Check Python version (using 3.11)
- Ensure frontend builds successfully locally

### Application Won't Start

**Check application logs:**
- Look for Django errors
- Verify DATABASE_URL is set
- Check REDIS_URL is set
- Ensure migrations ran

**Common fixes:**
- Verify environment variables
- Check database connection
- Restart processes

### Frontend Not Loading

**Symptoms:**
- API works but frontend shows errors
- 404 on frontend routes

**Fixes:**
1. Verify frontend built successfully:
   - Check build logs for `npm run build`
2. Check `frontend/dist` exists after build
3. Verify Django settings:
   - `TEMPLATES['DIRS']` includes `frontend/dist`
   - `STATICFILES_DIRS` includes `frontend/dist/assets`

### Celery Tasks Not Running

**Check:**
- Worker process is running
- Redis connection works
- Check worker logs for errors

**Test manually:**
```bash
# Via console
cd backend
celery -A genienews_backend inspect active
```

### pgvector Extension Not Found

**Fix:**
1. Connect to database (Sevalla console)
2. Run: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Redeploy application

### CORS Errors

**Should not happen** (frontend and backend same domain)

If you see CORS errors:
- Check if you're accessing from external domain
- Verify CORS_ALLOWED_ORIGINS in settings.py
- Add external domain to ALLOWED_HOSTS

## Cost Optimization

### Free Tier

Sevalla offers a generous free tier. Monitor usage:
- **Database**: Start small, scale up if needed
- **Redis**: Minimal instance sufficient
- **Processes**: 3 processes (web, worker, beat)

### Reduce Costs

1. **Scale down when not in use** (if available)
2. **Optimize database queries**
3. **Use caching** (Redis already configured)
4. **Monitor API usage** (OpenAI costs)

## Custom Domain (Optional)

1. **In Sevalla dashboard:**
   - Go to "Domains"
   - Click "Add Custom Domain"
   - Enter your domain: `genienews.com`

2. **Update DNS:**
   - Add CNAME record pointing to Sevalla
   - Follow Sevalla's instructions

3. **Update Settings:**
   - Add domain to `DJANGO_ALLOWED_HOSTS`
   - Redeploy

4. **SSL Certificate:**
   - Sevalla automatically provisions SSL
   - HTTPS enabled automatically

## Backup and Recovery

### Database Backups

Sevalla automatically backs up your PostgreSQL database:
- **Daily automatic backups**
- **Point-in-time recovery** (depending on plan)
- **Manual snapshots** available

### Manual Backup

Via console:
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore

Via Sevalla dashboard or console:
```bash
psql $DATABASE_URL < backup.sql
```

## Performance Tips

1. **Enable caching** (Redis already configured)
2. **Optimize database queries** (use `select_related`, `prefetch_related`)
3. **Use CDN for static files** (optional)
4. **Monitor slow queries** in database logs
5. **Scale worker processes** if tasks are backing up

## Support

- **Sevalla Documentation**: https://sevalla.com/docs
- **Sevalla Support**: Contact via dashboard
- **Django Documentation**: https://docs.djangoproject.com/
- **Celery Documentation**: https://docs.celeryproject.org/

## Summary

**Your GenieNews app is now deployed on Sevalla! 🎉**

- **URL**: `https://your-project.sevalla.app`
- **Admin**: `https://your-project.sevalla.app/admin/`
- **API**: `https://your-project.sevalla.app/api/`

**Next Steps:**
1. Add news sources
2. Trigger feed ingestion
3. Run AI curation
4. Monitor logs and performance
5. Enjoy your unified deployment!

---

**Note**: This guide assumes you're using Sevalla's default PostgreSQL and Redis offerings. Adjust as needed for your specific plan and requirements.

