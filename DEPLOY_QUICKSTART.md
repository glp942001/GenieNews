# GenieNews - Quick Deploy Guide

## Deploy in 3 Simple Steps (30 minutes)

### Step 1: Deploy Backend to Fly.io (15 min)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy backend
cd backend
fly launch --name genienews-backend --region sjc

# Create database
fly postgres create --name genienews-db --region sjc --vm-size shared-cpu-1x --volume-size 1
fly postgres attach genienews-db

# Set secrets
fly secrets set DJANGO_SECRET_KEY="$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
fly secrets set OPENAI_API_KEY="sk-YOUR-KEY-HERE"
fly secrets set ENVIRONMENT="production"
fly secrets set DJANGO_DEBUG="False"
fly secrets set FRONTEND_URL="https://genienews.vercel.app"

# Deploy
fly deploy

# Run migrations
fly ssh console
python manage.py migrate
python manage.py createsuperuser
python manage.py import_sources
exit
```

### Step 2: Setup Free Redis (5 min)

1. Go to https://console.upstash.com/
2. Create database (FREE tier)
3. Copy REDIS_URL
4. Run: `fly secrets set REDIS_URL="YOUR-REDIS-URL"`

### Step 3: Deploy Frontend to Vercel (10 min)

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Settings:
   - Root: `frontend`
   - Framework: Vite
   - Build: `npm run build`
   - Output: `dist`
4. Environment Variable:
   - `VITE_API_URL` = `https://genienews-backend.fly.dev`
5. Click "Deploy"

**Done! Your app is live!** 🎉

---

## Your Live URLs

- Frontend: https://genienews.vercel.app
- Backend API: https://genienews-backend.fly.dev/api/
- Admin: https://genienews-backend.fly.dev/admin/

---

## Cost

**$0.00/month** - Completely FREE! ✨

---

For detailed instructions, see `DEPLOYMENT.md`

