# GenieNews - FREE Cloud Deployment Guide

## 🚀 100% Free Architecture

This guide will help you deploy GenieNews completely FREE using:

- **Frontend**: Vercel (FREE forever - unlimited deployments, 100GB bandwidth/month)
- **Backend**: Fly.io (FREE tier - 3 VMs, 3GB storage, 160GB bandwidth/month)
- **Database**: Fly.io PostgreSQL (FREE - within 3GB storage)
- **Redis**: Upstash (FREE tier - 10,000 commands/day)

**Total Monthly Cost: $0.00**

Perfect for prototypes, demos, and portfolio projects!

---

## Prerequisites

Before you start, sign up for these free accounts:

1. **GitHub** - https://github.com (for code repository)
2. **Vercel** - https://vercel.com (for frontend hosting)
3. **Fly.io** - https://fly.io (for backend hosting)
4. **Upstash** - https://upstash.com (for Redis)
5. **OpenAI** - https://platform.openai.com (for AI features)

**Estimated Setup Time**: 30-45 minutes

---

## Part 1: Prepare Your Repository

### 1. Push Code to GitHub

```bash
cd /Users/gregoriolozano/Desktop/GenieNews

# Initialize git if not already done
git add .
git commit -m "Prepare for deployment"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/genienews.git
git branch -M main
git push -u origin main
```

---

## Part 2: Deploy Backend (Fly.io)

### 1. Install Fly CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Login to Fly.io

```bash
fly auth login
```

### 3. Create and Deploy Backend App

```bash
cd backend

# Launch app (this creates your app configuration)
fly launch --no-deploy --name genienews-backend --region sjc

# When prompted:
# - App name: genienews-backend (or choose your own)
# - Region: sjc (San Jose) or choose closest to you
# - PostgreSQL: YES
# - Redis: NO (we'll use Upstash free tier)
```

### 4. Create PostgreSQL Database (FREE)

```bash
# Create a PostgreSQL cluster (FREE tier - 1GB storage)
fly postgres create --name genienews-db --region sjc --vm-size shared-cpu-1x --volume-size 1

# Attach database to your app
fly postgres attach genienews-db --app genienews-backend
```

This automatically sets the `DATABASE_URL` secret in your app.

### 5. Setup Upstash Redis (FREE)

1. Go to https://console.upstash.com/
2. Click "Create Database"
3. Choose:
   - Name: genienews-redis
   - Type: Regional
   - Region: Closest to your Fly.io region
   - **Free tier** (10,000 commands/day)
4. Copy the `UPSTASH_REDIS_REST_URL`
5. Add to Fly.io:

```bash
fly secrets set REDIS_URL="<paste-your-upstash-redis-url>"
```

### 6. Set Environment Variables

```bash
# Generate a secure Django secret key
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set all secrets (replace values with your own)
fly secrets set DJANGO_SECRET_KEY="<paste-generated-secret-key>"
fly secrets set OPENAI_API_KEY="sk-your-openai-api-key"
fly secrets set ENVIRONMENT="production"
fly secrets set DJANGO_DEBUG="False"
fly secrets set FRONTEND_URL="https://genienews.vercel.app"

# Optional: Set AI configuration (or use defaults)
fly secrets set AI_MODEL="gpt-4"
fly secrets set EMBEDDING_MODEL="text-embedding-3-small"
fly secrets set TTS_VOICE="nova"
fly secrets set TTS_SPEED="1.10"
```

### 7. Deploy Backend

```bash
fly deploy
```

**Wait 2-3 minutes for deployment to complete.**

### 8. Run Database Migrations

```bash
# SSH into your app
fly ssh console --app genienews-backend

# Run migrations
python manage.py migrate

# Create superuser for Django admin
python manage.py createsuperuser
# Follow prompts to set username, email, password

# Import RSS sources
python manage.py import_sources

# Exit SSH
exit
```

### 9. Test Backend

Visit these URLs:
- **Admin Panel**: https://genienews-backend.fly.dev/admin/
- **API Endpoint**: https://genienews-backend.fly.dev/api/news/articles/

If both load successfully, your backend is live! 🎉

---

## Part 3: Deploy Frontend (Vercel)

### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://genienews-backend.fly.dev` (your Fly.io backend URL)
6. Click "Deploy"

**Wait 1-2 minutes for deployment.**

### Option B: Deploy via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: genienews
# - Directory: ./ (current directory)
# - Override settings? N

# After deployment, set environment variable
vercel env add VITE_API_URL
# Value: https://genienews-backend.fly.dev

# Redeploy with environment variable
vercel --prod
```

### 10. Test Frontend

Visit your Vercel URL (shown after deployment):
- **Production URL**: https://genienews.vercel.app

You should see:
- Articles loading from your Fly.io backend
- Images displaying
- AI chat working
- Audio player loading

---

## Part 4: Setup Celery Worker (Background Tasks)

Your app needs a Celery worker for background tasks (RSS ingestion, AI curation, audio generation).

### Create Worker Machine on Fly.io

```bash
cd backend

# Create a separate worker machine
fly machine create --app genienews-backend \
  --name genienews-worker \
  --region sjc \
  --vm-size shared-cpu-1x \
  --vm-memory 512 \
  --dockerfile Dockerfile \
  --entrypoint "celery -A genienews_backend worker --loglevel=info"

# Create Celery Beat for scheduled tasks (optional)
fly machine create --app genienews-backend \
  --name genienews-beat \
  --region sjc \
  --vm-size shared-cpu-1x \
  --vm-memory 256 \
  --dockerfile Dockerfile \
  --entrypoint "celery -A genienews_backend beat --loglevel=info"
```

**Note**: Fly.io free tier includes 3 VMs total, so you can run:
1. Web server (main app)
2. Celery worker (for background tasks)
3. Database (PostgreSQL)

---

## Part 5: Initial Data Setup

### Trigger First Data Ingestion

1. SSH into your backend:
```bash
fly ssh console --app genienews-backend
```

2. Manually trigger RSS ingestion:
```bash
python manage.py shell
```

```python
from news.tasks import ingest_all_feeds_task, curate_articles_task, generate_audio_segment_task

# Ingest RSS feeds
result = ingest_all_feeds_task()
print(result)

# Curate articles with AI
result = curate_articles_task()
print(result)

# Generate audio segment
result = generate_audio_segment_task()
print(result)

exit()
```

3. Exit SSH:
```bash
exit
```

### Verify Data

Visit your frontend at https://genienews.vercel.app - you should now see:
- 8 curated articles
- AI-generated summaries
- Audio news segment
- All features working!

---

## Environment Variables Reference

### Backend (Fly.io Secrets)

**Required:**
```bash
ENVIRONMENT=production
DJANGO_SECRET_KEY=<random-secret-key>
DJANGO_DEBUG=False
DATABASE_URL=<auto-set-by-fly-postgres>
REDIS_URL=<from-upstash>
OPENAI_API_KEY=<your-openai-key>
FRONTEND_URL=https://genienews.vercel.app
```

**Optional (with defaults):**
```bash
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000
TTS_VOICE=nova
TTS_SPEED=1.10
TTS_MODEL=tts-1-hd
```

### Frontend (Vercel Environment Variables)

**Required:**
```bash
VITE_API_URL=https://genienews-backend.fly.dev
```

---

## Monitoring & Maintenance

### View Logs

**Backend Logs:**
```bash
fly logs --app genienews-backend
```

**Real-time logs:**
```bash
fly logs --app genienews-backend -f
```

**Worker logs:**
```bash
fly machine logs <worker-machine-id>
```

### Check App Status

```bash
fly status --app genienews-backend
```

### Scale/Manage Machines

```bash
# List all machines
fly machine list --app genienews-backend

# Stop a machine
fly machine stop <machine-id>

# Start a machine
fly machine start <machine-id>
```

### Update Secrets

```bash
fly secrets set KEY=value --app genienews-backend
```

### Redeploy After Code Changes

```bash
# Backend
cd backend
fly deploy

# Frontend (auto-deploys on git push to main)
# Or manually:
cd frontend
vercel --prod
```

---

## Free Tier Limits

### Fly.io
- **3 shared-cpu VMs** (1x web + 1x worker + 1x database = perfect!)
- **3GB persistent storage** (database)
- **160GB bandwidth/month** (plenty for demos)
- **Auto-suspend**: Machines sleep after inactivity, wake on request

### Vercel
- **Unlimited deployments**
- **100GB bandwidth/month**
- **Automatic SSL**
- **Global CDN**

### Upstash Redis
- **10,000 commands/day**
- **Max 256MB data**
- **Automatic eviction**

**For a demo/prototype**: These limits are more than sufficient!

---

## Troubleshooting

### Backend not responding?
```bash
# Check if app is running
fly status --app genienews-backend

# Check logs
fly logs --app genienews-backend

# Restart app
fly machine restart <machine-id>
```

### Database connection errors?
```bash
# Verify DATABASE_URL is set
fly secrets list --app genienews-backend

# Check database status
fly postgres db list --app genienews-db
```

### Frontend not connecting to backend?
- Check `VITE_API_URL` in Vercel dashboard
- Verify CORS settings in Django
- Check backend logs for CORS errors

### Celery tasks not running?
- Ensure worker machine is running: `fly machine list`
- Check Redis connection: `fly secrets list | grep REDIS`
- View worker logs

---

## Updating Your Deployment

### When you make code changes:

**Backend changes:**
```bash
cd backend
git add .
git commit -m "Update backend"
git push
fly deploy  # Manual deploy to Fly.io
```

**Frontend changes:**
```bash
cd frontend
git add .
git commit -m "Update frontend"
git push  # Vercel auto-deploys from main branch!
```

---

## Cost Monitoring

All services have free dashboards to monitor usage:

- **Fly.io**: https://fly.io/dashboard (check bandwidth, VM usage)
- **Vercel**: https://vercel.com/dashboard (check deployments, bandwidth)
- **Upstash**: https://console.upstash.com (check Redis commands)

**Stay within free tiers**:
- Fly.io: Don't exceed 160GB/month bandwidth
- Upstash: Don't exceed 10,000 Redis commands/day
- Vercel: Don't exceed 100GB/month bandwidth

For a demo with moderate traffic (100-500 visitors/month), you'll stay well within limits!

---

## Security Checklist

Before going live:

- [ ] `DJANGO_DEBUG=False` in production
- [ ] Unique `DJANGO_SECRET_KEY` (not the default)
- [ ] Valid `OPENAI_API_KEY`
- [ ] CORS configured for your frontend URL only
- [ ] `.env` files NOT committed to git
- [ ] Strong superuser password set
- [ ] SSL/HTTPS enabled (automatic on Fly.io and Vercel)

---

## Quick Reference Commands

```bash
# Backend
fly logs                    # View logs
fly ssh console            # SSH into backend
fly postgres connect       # Connect to database
fly secrets set KEY=val    # Update environment variable
fly deploy                 # Deploy new version

# Frontend
vercel                     # Deploy preview
vercel --prod             # Deploy to production
vercel logs               # View logs
vercel env add            # Add environment variable

# Local development
cd backend
source ../venv/bin/activate
python manage.py runserver

cd frontend
npm run dev
```

---

## Support & Resources

- **Fly.io Docs**: https://fly.io/docs/
- **Vercel Docs**: https://vercel.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/
- **Upstash Docs**: https://docs.upstash.com/

---

## What Gets Deployed

### Frontend (Vercel)
- React app built with Vite
- Static files served via global CDN
- Automatic SSL certificate
- Auto-deploys on git push to main

### Backend (Fly.io)
- Django REST API
- PostgreSQL database with pgvector
- Celery worker for background tasks
- Redis for task queue
- Media file storage
- Admin panel at `/admin/`

---

## Post-Deployment Tasks

After successful deployment:

1. **Visit your live site**: https://genienews.vercel.app
2. **Login to admin**: https://genienews-backend.fly.dev/admin/
3. **Trigger first data sync**:
   - Go to admin panel
   - Navigate to "Feed ingestion logs"
   - Monitor the automated weekly sync or trigger manually
4. **Test all features**:
   - Articles loading
   - AI chat working
   - Audio player functional
   - Article summaries generating

---

## Congratulations! 🎉

Your GenieNews app is now live and accessible to anyone with the URL!

**Share your demo**:
- Frontend: https://genienews.vercel.app
- Backend API: https://genienews-backend.fly.dev/api/

**Your live AI news aggregator is ready for the world!**

