# GenieNews Fly.io Deployment Checklist

Use this checklist to deploy GenieNews to Fly.io step by step.

## Pre-Deployment Preparation

### ✅ Prerequisites

- [ ] Fly.io account created (https://fly.io/app/sign-up)
- [ ] flyctl CLI installed (`brew install flyctl` or see https://fly.io/docs/hands-on/install-flyctl/)
- [ ] Logged in to Fly.io (`flyctl auth login`)
- [ ] OpenAI API key ready (https://platform.openai.com/api-keys)
- [ ] Git repository up to date with latest changes

### ✅ Verify Local Changes

- [ ] All code changes committed to git
- [ ] Backend Dockerfile exists and updated
- [ ] Frontend Dockerfile exists
- [ ] Backend fly.toml exists in `backend/` directory
- [ ] Frontend fly.toml exists in `frontend/` directory
- [ ] No duplicate fly.toml in root directory

## Backend Deployment

### Step 1: Create Backend App

```bash
cd backend
flyctl apps create genienews-backend
```

- [ ] Backend app created successfully
- [ ] Note: If app name is taken, choose a different name and update all references

### Step 2: Provision PostgreSQL

```bash
# Create PostgreSQL with pgvector
flyctl postgres create \
  --name genienews-db \
  --region sjc \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1

# Attach to backend
flyctl postgres attach genienews-db --app genienews-backend
```

- [ ] PostgreSQL cluster created
- [ ] Database attached to backend app
- [ ] DATABASE_URL automatically set

### Step 3: Enable pgvector Extension

```bash
flyctl postgres connect -a genienews-db
```

In the psql shell:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

- [ ] pgvector extension enabled
- [ ] Confirmed with `\dx` in psql

### Step 4: Provision Redis

**Option A: Upstash Redis (Recommended)**

1. Go to https://upstash.com/
2. Create account and new Redis database
3. Copy the Redis URL
4. Set secret:

```bash
flyctl secrets set REDIS_URL="redis://default:your-password@your-host:port" --app genienews-backend
```

- [ ] Upstash account created
- [ ] Redis database created
- [ ] Redis URL copied and set as secret

**Option B: Fly.io Redis** (if available)

```bash
flyctl redis create --name genienews-redis --region sjc
flyctl redis attach genienews-redis --app genienews-backend
```

- [ ] Redis created and attached

### Step 5: Create Volume for Media Files

```bash
flyctl volumes create genienews_media \
  --size 1 \
  --region sjc \
  --app genienews-backend
```

- [ ] Volume created successfully
- [ ] Volume name matches `fly.toml` mount source (`genienews_media`)

### Step 6: Generate and Set Secrets

Generate Django secret key:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set required secrets:
```bash
flyctl secrets set \
  DJANGO_SECRET_KEY="<paste-generated-key-here>" \
  DJANGO_DEBUG="False" \
  DJANGO_ALLOWED_HOSTS=".fly.dev" \
  OPENAI_API_KEY="sk-your-actual-key-here" \
  --app genienews-backend
```

- [ ] Django secret key generated
- [ ] DJANGO_SECRET_KEY set
- [ ] DJANGO_DEBUG set to False
- [ ] DJANGO_ALLOWED_HOSTS set
- [ ] OPENAI_API_KEY set

Optional: Set additional secrets:
```bash
flyctl secrets set \
  AI_MODEL="gpt-4" \
  TTS_VOICE="nova" \
  TTS_SPEED="1.15" \
  --app genienews-backend
```

- [ ] Optional secrets set (if desired)

### Step 7: Deploy Backend

```bash
cd backend
flyctl deploy --app genienews-backend
```

- [ ] Docker image built successfully
- [ ] Migrations ran successfully (via release command)
- [ ] App deployed successfully
- [ ] Health checks passing

### Step 8: Verify Backend

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

- [ ] App status shows "running"
- [ ] Health check returns `{"status": "healthy"}`
- [ ] API endpoint accessible (may return empty list initially)
- [ ] No errors in logs

### Step 9: Create Admin User

```bash
flyctl ssh console --app genienews-backend
```

In SSH session:
```bash
python manage.py createsuperuser
# Follow prompts to create admin user
exit
```

- [ ] Superuser created
- [ ] Admin panel accessible at https://genienews-backend.fly.dev/admin/
- [ ] Can login with superuser credentials

## Frontend Deployment

### Step 10: Create Frontend App

```bash
cd frontend
flyctl apps create genienews-frontend
```

- [ ] Frontend app created successfully
- [ ] Note: If name is taken, choose different name and update references

### Step 11: Verify Frontend Configuration

Check that `frontend/fly.toml` has correct backend URL:

```toml
[env]
  VITE_API_URL = "https://genienews-backend.fly.dev"
```

- [ ] Backend URL in fly.toml matches your backend app name
- [ ] Update if you used a different backend app name

### Step 12: Deploy Frontend

```bash
cd frontend
flyctl deploy --app genienews-frontend
```

- [ ] Vite build completed successfully
- [ ] Nginx container deployed
- [ ] App running
- [ ] Health checks passing

### Step 13: Verify Frontend

```bash
# Check status
flyctl status --app genienews-frontend

# Open in browser
flyctl open --app genienews-frontend
```

- [ ] Frontend accessible in browser
- [ ] No console errors in browser DevTools
- [ ] Frontend loads (may not show articles yet due to CORS)

## Final Configuration

### Step 14: Update Backend CORS

```bash
flyctl secrets set FRONTEND_URL="https://genienews-frontend.fly.dev" --app genienews-backend
```

- [ ] FRONTEND_URL secret set
- [ ] Backend automatically redeployed
- [ ] Redeploy successful

### Step 15: Verify End-to-End

Visit https://genienews-frontend.fly.dev and check:

- [ ] Frontend loads without errors
- [ ] No CORS errors in browser console
- [ ] API calls work (even if no articles yet)
- [ ] Health checks working

## Data Population

### Step 16: Add News Sources

Via admin panel at https://genienews-backend.fly.dev/admin/:

- [ ] Login to admin panel
- [ ] Add at least 3-5 RSS feed sources
- [ ] Mark sources as active

Example sources:
- TechCrunch AI: `https://techcrunch.com/tag/artificial-intelligence/feed/`
- VentureBeat AI: `https://venturebeat.com/category/ai/feed/`
- The Verge AI: `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml`

### Step 17: Initial Feed Ingestion

```bash
flyctl ssh console --app genienews-backend
```

In SSH session:
```bash
# Ingest from all active sources
python manage.py update_rss_feeds

# Check results
python manage.py shell
>>> from news.models import ArticleRaw
>>> ArticleRaw.objects.count()
>>> exit()
exit
```

- [ ] Feed ingestion completed
- [ ] Articles created in database
- [ ] No critical errors

### Step 18: Curate Articles

```bash
flyctl ssh console --app genienews-backend
```

In SSH session:
```bash
# Run AI curation
python manage.py test_curation

# Verify curated articles
python manage.py shell
>>> from news.models import ArticleCurated
>>> ArticleCurated.objects.count()
>>> exit()
exit
```

- [ ] Curation completed successfully
- [ ] Curated articles created
- [ ] Embeddings generated

### Step 19: Final Verification

Visit https://genienews-frontend.fly.dev:

- [ ] Articles now visible on homepage
- [ ] Articles display correctly with images and summaries
- [ ] Can click on article cards
- [ ] No errors in browser console

Test backend API:
```bash
curl https://genienews-backend.fly.dev/api/articles/
```

- [ ] API returns articles as JSON
- [ ] Article data includes title, summary, images, etc.

## Post-Deployment

### Step 20: Monitor and Test

Monitor logs:
```bash
# Backend logs
flyctl logs --app genienews-backend

# Frontend logs
flyctl logs --app genienews-frontend
```

- [ ] No errors in backend logs
- [ ] No errors in frontend logs
- [ ] Celery worker running
- [ ] Celery beat running

### Step 21: Test Celery Tasks

The following tasks should run automatically:
- Feed ingestion: Weekly (Mondays at 2 AM UTC)
- Content fetching: Weekly (Mondays at 4 AM UTC)
- Article curation: Hourly

To test manually:
```bash
flyctl ssh console --app genienews-backend
celery -A genienews_backend inspect active
```

- [ ] Celery worker responding
- [ ] Can see scheduled tasks
- [ ] Tasks can be triggered manually

### Step 22: Test Features

Test each feature:

- [ ] Homepage loads articles
- [ ] Article cards display correctly
- [ ] Images load properly
- [ ] AI chat feature works (if implemented)
- [ ] Audio generation works (if implemented)
- [ ] Responsive design works on mobile

### Step 23: Performance Check

```bash
# Check resource usage
flyctl status --app genienews-backend
flyctl status --app genienews-frontend

# Check metrics
flyctl dashboard --app genienews-backend
```

- [ ] Memory usage acceptable
- [ ] CPU usage normal
- [ ] No performance issues

## Optional Enhancements

### Custom Domain (Optional)

If you want to use a custom domain:

**Frontend:**
```bash
flyctl certs create yourdomain.com --app genienews-frontend
flyctl certs show yourdomain.com --app genienews-frontend
# Follow DNS instructions
```

**Backend:**
```bash
flyctl certs create api.yourdomain.com --app genienews-backend
flyctl certs show api.yourdomain.com --app genienews-backend
# Follow DNS instructions
```

- [ ] Custom domains configured (if desired)
- [ ] SSL certificates issued
- [ ] DNS records updated
- [ ] Apps accessible via custom domains

### Scaling (Optional)

If you need more resources:

```bash
# Scale backend memory
flyctl scale memory 2048 --app genienews-backend

# Scale instances
flyctl scale count 2 --app genienews-backend
```

- [ ] Scaled appropriately (if needed)

### Monitoring Setup (Optional)

Consider setting up:
- [ ] Sentry for error tracking
- [ ] Uptime monitoring
- [ ] Log aggregation
- [ ] Performance monitoring

## Deployment Complete! 🎉

### Your URLs

- **Frontend**: https://genienews-frontend.fly.dev
- **Backend API**: https://genienews-backend.fly.dev/api/
- **Admin Panel**: https://genienews-backend.fly.dev/admin/

### Useful Commands

```bash
# Deploy updates
./deploy.sh deploy-all

# Check status
./deploy.sh status-all

# View logs
./deploy.sh logs-backend
./deploy.sh logs-frontend

# SSH access
./deploy.sh ssh-backend

# Open apps
./deploy.sh open-all
```

### Next Steps

1. **Populate more sources**: Add additional RSS feeds via admin panel
2. **Monitor usage**: Watch Fly.io dashboard for resource usage
3. **Set up backups**: Fly.io PostgreSQL backs up automatically
4. **Configure monitoring**: Set up error tracking and alerts
5. **Test thoroughly**: Test all features in production
6. **Share with users**: Your app is live!

### Documentation

- [Main README](./README.md)
- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

### Support

- **Fly.io Issues**: https://community.fly.io/
- **Django Issues**: https://docs.djangoproject.com/
- **React Issues**: https://react.dev/

---

**Congratulations! Your GenieNews app is deployed on Fly.io! 🚀**

