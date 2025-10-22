# ✅ GenieNews Sevalla Migration - Complete!

Your GenieNews project has been successfully configured for Sevalla deployment with a unified approach (Django serving React).

## What Was Done

### 1. Removed Fly.io Configuration ✅
- Deleted `backend/fly.toml`
- Deleted `backend/Dockerfile`
- Deleted `frontend/fly.toml`
- Deleted `frontend/Dockerfile`
- Removed Fly.io-specific settings

### 2. Configured Django to Serve React ✅
- Updated `settings.py` TEMPLATES to include `frontend/dist`
- Added `frontend/dist/assets` to STATICFILES_DIRS
- Updated `urls.py` with catch-all route for React SPA
- Updated ALLOWED_HOSTS for Sevalla domains

### 3. Created Sevalla Configuration Files ✅
- **`nixpacks.toml`** - Build configuration for Sevalla
- **`Procfile`** - Multi-process definitions (web, worker, beat)

### 4. Updated API Configuration ✅
- Frontend API calls use relative paths in production
- Works seamlessly when served from same domain

### 5. Created Documentation ✅
- **`SEVALLA_DEPLOYMENT.md`** - Comprehensive deployment guide
- **`QUICK_START_SEVALLA.md`** - 5-minute quick start
- **`ENV_VARIABLES_SEVALLA.md`** - Environment variables reference
- Updated main `README.md` for Sevalla

### 6. Restored pgvector ✅
- Reverted temporary pgvector workarounds
- Ready for PostgreSQL with pgvector extension

## Project Structure

```
GenieNews/
├── backend/               # Django REST API
│   ├── genienews_backend/
│   │   ├── settings.py   # ✅ Updated for Sevalla + React serving
│   │   └── urls.py       # ✅ Catch-all route for React
│   ├── news/             # Django app
│   ├── media/            # Uploaded/generated files
│   ├── requirements.txt  # Python dependencies
│   └── manage.py
├── frontend/             # React SPA
│   ├── src/
│   │   └── services/
│   │       └── api.js    # ✅ Updated for relative API paths
│   ├── dist/             # Built files (created during deployment)
│   ├── package.json
│   └── vite.config.js
├── nixpacks.toml         # ✅ NEW: Sevalla build config
├── Procfile              # ✅ NEW: Process definitions
├── SEVALLA_DEPLOYMENT.md # ✅ NEW: Full deployment guide
├── QUICK_START_SEVALLA.md# ✅ NEW: Quick start guide
├── ENV_VARIABLES_SEVALLA.md # ✅ NEW: Environment variables
└── README.md             # ✅ Updated for Sevalla
```

## How It Works

### Deployment Flow

1. **You push to GitHub/GitLab**
2. **Sevalla detects changes**
3. **Build phase (nixpacks.toml):**
   - Installs Python dependencies
   - Installs Node dependencies
   - Builds React frontend (`npm run build`)
   - Collects Django static files
4. **Start phase (Procfile):**
   - Runs migrations
   - Starts Gunicorn (web server)
   - Starts Celery worker
   - Starts Celery beat
5. **Django serves:**
   - API at `/api/`
   - React app at `/` (all other routes)
   - Admin at `/admin/`
   - Media files at `/media/`

### Request Flow

```
User visits https://your-app.sevalla.app
         ↓
    Sevalla Load Balancer
         ↓
    Gunicorn (Django)
         ↓
    ┌────────────────────┐
    │  API Request?      │
    │  /api/*            │──→ Django REST API
    └────────────────────┘
         │
         │ No (frontend route)
         ↓
    Serve index.html
         ↓
    React Router handles routing
```

## Configuration Files Explained

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ['postgresql', 'nodejs-18_x']  # System dependencies

[phases.install]
cmds = ['cd backend && pip install -r requirements.txt']  # Install Python deps

[phases.build]
cmds = [
  'cd frontend && npm ci && npm run build',  # Build React
  'cd backend && python manage.py collectstatic --noinput'  # Collect static
]

[start]
cmd = 'cd backend && python manage.py migrate --noinput && gunicorn...'  # Start server
```

### Procfile
```
web: ... gunicorn ...      # Main web server
worker: ... celery worker  # Async task processor
beat: ... celery beat      # Task scheduler
```

## What You Need to Deploy

### Required:
1. ✅ Sevalla account
2. ✅ Git repository (GitHub/GitLab)
3. ✅ OpenAI API key
4. ✅ Add PostgreSQL database in Sevalla
5. ✅ Add Redis instance in Sevalla
6. ✅ Set environment variables
7. ✅ Enable 3 processes (web, worker, beat)

### That's It!
Sevalla handles everything else automatically.

## Next Steps

### Option 1: Quick Deploy (5 minutes)
Follow: [QUICK_START_SEVALLA.md](./QUICK_START_SEVALLA.md)

### Option 2: Detailed Deploy (with full understanding)
Follow: [SEVALLA_DEPLOYMENT.md](./SEVALLA_DEPLOYMENT.md)

### Option 3: Test Locally First
```bash
# Terminal 1: Build frontend
cd frontend
npm install
npm run build

# Terminal 2: Run backend
cd backend
source ../venv/bin/activate
python manage.py runserver

# Visit: http://localhost:8000
# Both frontend and API should work!
```

## Environment Variables Quick Reference

**Minimum required for Sevalla:**
```bash
DJANGO_SECRET_KEY=<generate-random-50-char>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.sevalla.com,.sevalla.app
ENVIRONMENT=production
DATABASE_URL=<auto-provided-by-sevalla>
REDIS_URL=<auto-provided-by-sevalla>
OPENAI_API_KEY=sk-your-key-here
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

See full list: [ENV_VARIABLES_SEVALLA.md](./ENV_VARIABLES_SEVALLA.md)

## Benefits of This Approach

✅ **Single deployment** - Everything in one place  
✅ **No CORS issues** - Same domain for frontend and backend  
✅ **Simpler management** - One app to monitor  
✅ **Cost efficient** - Single instance instead of two  
✅ **Easy updates** - Push to git, auto-deploys  
✅ **Built-in SSL** - HTTPS automatically  
✅ **Multi-process** - Web, worker, beat all running  

## Key Features Preserved

✅ RSS feed ingestion  
✅ AI-powered curation  
✅ Vector embeddings (pgvector)  
✅ Daily audio briefings  
✅ AI chat assistant  
✅ Scheduled tasks (Celery Beat)  
✅ Async processing (Celery Worker)  
✅ Admin panel  
✅ REST API  
✅ React frontend  

## Comparison: Before vs After

### Before (Fly.io - Attempted)
- ❌ Complex multi-app setup
- ❌ Separate backend and frontend
- ❌ CORS configuration needed
- ❌ Two Docker files
- ❌ Multiple fly.toml files
- ❌ Database connection issues
- ❌ pgvector extension problems

### After (Sevalla - Ready!)
- ✅ Single unified app
- ✅ Django serves everything
- ✅ No CORS issues
- ✅ Simple configuration (nixpacks.toml + Procfile)
- ✅ Auto-provided database and Redis
- ✅ Built-in pgvector support
- ✅ Easy deployment (git push)

## Testing Checklist

Before deploying to Sevalla, test locally:

```bash
# 1. Build frontend
cd frontend && npm run build

# 2. Check build output
ls -la dist/  # Should show index.html and assets/

# 3. Run Django
cd backend
python manage.py collectstatic --noinput
python manage.py runserver

# 4. Test endpoints
curl http://localhost:8000/health/  # Health check
curl http://localhost:8000/api/articles/  # API
open http://localhost:8000/  # Frontend (should load React app)
open http://localhost:8000/admin/  # Admin panel
```

All should work! If they do, deployment will work too.

## Troubleshooting

### Frontend not loading locally?
- Check `frontend/dist/` exists
- Verify `settings.py` TEMPLATES includes `frontend/dist`
- Check `urls.py` has catch-all route

### API not working?
- Check `backend/urls.py` has `/api/` routes
- Verify Django server is running
- Check API calls in browser DevTools Network tab

### Build issues on Sevalla?
- Verify `nixpacks.toml` syntax
- Check `Procfile` format
- Review Sevalla build logs

## Support Resources

- **Full Guide**: [SEVALLA_DEPLOYMENT.md](./SEVALLA_DEPLOYMENT.md)
- **Quick Start**: [QUICK_START_SEVALLA.md](./QUICK_START_SEVALLA.md)
- **Environment Vars**: [ENV_VARIABLES_SEVALLA.md](./ENV_VARIABLES_SEVALLA.md)
- **Main README**: [README.md](./README.md)
- **Sevalla Docs**: https://sevalla.com/docs

## Summary

Your GenieNews project is now **100% ready** for Sevalla deployment! 🎉

### What's Different:
- ❌ Removed Fly.io configuration
- ✅ Added Sevalla configuration
- ✅ Configured unified Django + React deployment
- ✅ Created comprehensive documentation

### What's Next:
1. **Push to GitHub/GitLab**
2. **Follow [QUICK_START_SEVALLA.md](./QUICK_START_SEVALLA.md)**
3. **Deploy and enjoy!**

---

**Your app is ready to deploy! Good luck! 🚀**

