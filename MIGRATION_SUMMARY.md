# GenieNews Fly.io Migration Summary

This document summarizes all changes made to migrate GenieNews from Vercel to Fly.io.

## Migration Date

October 22, 2025

## Overview

Successfully migrated GenieNews from a split deployment (backend on Fly.io, frontend on Vercel) to a unified Fly.io deployment for both backend and frontend.

## Changes Made

### 1. Configuration Files

#### ✅ Removed
- `/fly.toml` - Duplicate root configuration (deleted)
- `/frontend/vercel.json` - Vercel-specific configuration (deleted)

#### ✅ Created
- `/frontend/Dockerfile` - Multi-stage build (Node.js + nginx)
- `/frontend/fly.toml` - Frontend Fly.io configuration
- `/frontend/.dockerignore` - Frontend Docker ignore rules
- `/frontend/README.md` - Frontend documentation

#### ✅ Updated
- `/backend/Dockerfile` - Enhanced with health checks and production optimizations
- `/backend/fly.toml` - Added PostgreSQL, Redis, volumes, and multi-process config
- `/backend/genienews_backend/urls.py` - Added health check endpoint
- `/backend/.dockerignore` - Improved exclusions
- `/.dockerignore` - Removed fly.toml exclusion
- `/frontend/env.example` - Updated for Fly.io deployment

### 2. Backend Changes

#### Dockerfile Improvements
- Added Python environment variables for production
- Installed PostgreSQL client for database operations
- Created media directory for volume mounting
- Added health check using requests library
- Configured gunicorn with 2 workers and 120s timeout
- Optimized build with multi-stage considerations

#### fly.toml Configuration
- **Build**: Explicit Dockerfile reference
- **Deploy**: Added release command for migrations
- **Environment**: Set ENVIRONMENT=production
- **HTTP Service**: 
  - Internal port 8000
  - Force HTTPS enabled
  - Auto-stop/start machines
  - Health checks at `/health/`
  - Process filtering for web service
- **Mounts**: Persistent volume for media files
- **Processes**:
  - `app`: Gunicorn web server
  - `worker`: Celery worker for async tasks
  - `beat`: Celery beat for scheduled tasks
- **VM**: Increased to 1GB RAM for production workload

#### Health Check Endpoint
- Added `/health/` endpoint in `urls.py`
- Returns JSON: `{"status": "healthy", "service": "genienews-backend"}`
- Used by Fly.io health checks and Docker healthcheck

#### Media File Serving
- Updated to serve media files in production (not just development)
- Media served from mounted volume at `/app/media`

### 3. Frontend Changes

#### Dockerfile (New)
- **Stage 1**: Node.js 18 Alpine for building
  - Copies package files and source
  - Runs `npm ci` for clean install
  - Builds with `npm run build`
- **Stage 2**: Nginx Alpine for serving
  - Custom nginx configuration
  - SPA routing support (try_files)
  - Gzip compression enabled
  - Security headers added
  - Static asset caching (1 year)
  - Health check at `/health`
  - Serves on port 8080

#### fly.toml Configuration (New)
- **App**: genienews-frontend
- **Region**: sjc (San Jose, California)
- **Build**: Multi-stage Dockerfile
- **Environment**: VITE_API_URL set to backend
- **HTTP Service**:
  - Internal port 8080
  - Force HTTPS
  - Auto-stop/start machines
  - Health checks at `/health`
- **VM**: 256MB RAM (sufficient for nginx)

#### Environment Configuration
- Removed Vercel-specific configs
- Set backend URL via VITE_API_URL
- Local dev uses `http://localhost:8000`
- Production uses `https://genienews-backend.fly.dev`

### 4. Documentation

#### New Documentation Files
1. **DEPLOYMENT.md** (Comprehensive)
   - Complete step-by-step deployment guide
   - Backend and frontend deployment instructions
   - PostgreSQL and Redis setup
   - Volume configuration
   - Secrets management
   - Monitoring and troubleshooting
   - Cost optimization tips
   - Custom domain setup
   - Backup and recovery

2. **SETUP.md** (Initial Setup)
   - Local development setup
   - Fly.io production setup
   - Initial data population
   - Testing procedures
   - Common issues and solutions

3. **DEPLOYMENT_CHECKLIST.md**
   - Step-by-step checklist format
   - Pre-deployment verification
   - Backend deployment steps
   - Frontend deployment steps
   - Data population
   - Post-deployment testing

4. **MIGRATION_SUMMARY.md** (This file)
   - Summary of all changes
   - Migration overview
   - What's new

#### Updated Documentation
1. **README.md** (Root)
   - Complete project overview
   - Feature list
   - Tech stack details
   - Project structure
   - Development instructions
   - Deployment links
   - Contributing guidelines

2. **frontend/README.md** (New)
   - Frontend-specific documentation
   - Local development setup
   - Component structure
   - API integration
   - Deployment instructions
   - Troubleshooting

3. **backend/README.md** (Updated)
   - Added quick links section
   - References to new documentation

#### Helper Scripts
1. **deploy.sh**
   - Executable deployment helper script
   - Commands for common operations:
     - `deploy-backend` - Deploy backend
     - `deploy-frontend` - Deploy frontend
     - `deploy-all` - Deploy both
     - `status-*` - Check status
     - `logs-*` - View logs
     - `ssh-backend` - SSH access
     - `open-*` - Open in browser

### 5. Architecture Changes

#### Before Migration
```
Frontend: Vercel (React/Vite)
Backend: Fly.io (Django + Celery)
Database: Fly.io PostgreSQL
Cache: External Redis (Upstash)
```

#### After Migration
```
Frontend: Fly.io (React/Vite + Nginx)
Backend: Fly.io (Django + Celery)
Database: Fly.io PostgreSQL (with pgvector)
Cache: Fly.io Redis or Upstash
Storage: Fly.io Volumes (media files)
```

#### Benefits
1. **Unified Platform**: Everything on Fly.io
2. **Better Integration**: Internal network communication
3. **Simplified Deployment**: Single platform to manage
4. **Cost Efficiency**: Consolidated billing and free tier usage
5. **Consistent Configuration**: Similar patterns for backend and frontend

## Infrastructure Requirements

### Backend App (`genienews-backend`)
- **VM**: 1GB RAM, 1 shared CPU
- **Database**: PostgreSQL 16 with pgvector extension
- **Cache**: Redis (Upstash or Fly.io)
- **Storage**: 1GB persistent volume for media files
- **Processes**:
  - Web server (Gunicorn)
  - Celery worker (async tasks)
  - Celery beat (scheduled tasks)

### Frontend App (`genienews-frontend`)
- **VM**: 256MB RAM, 1 shared CPU
- **Web Server**: Nginx
- **Static Assets**: Vite build output

### Required Secrets (Backend)
- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - Debug mode (False in production)
- `DJANGO_ALLOWED_HOSTS` - Allowed hosts (.fly.dev)
- `DATABASE_URL` - PostgreSQL connection (auto-set)
- `REDIS_URL` - Redis connection
- `OPENAI_API_KEY` - OpenAI API key
- `FRONTEND_URL` - Frontend URL for CORS

### Optional Secrets (Backend)
- `AI_MODEL` - OpenAI model (default: gpt-4)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)
- `TTS_VOICE` - Text-to-speech voice (default: nova)
- `TTS_SPEED` - TTS speed (default: 1.15)
- `TTS_MODEL` - TTS model (default: tts-1-hd)

## Deployment URLs

### Production URLs (Expected)
- **Frontend**: https://genienews-frontend.fly.dev
- **Backend API**: https://genienews-backend.fly.dev/api/
- **Admin Panel**: https://genienews-backend.fly.dev/admin/
- **Health Checks**: 
  - Backend: https://genienews-backend.fly.dev/health/
  - Frontend: https://genienews-frontend.fly.dev/health

## Testing Checklist

### Pre-Deployment
- [x] Removed duplicate fly.toml files
- [x] Updated Dockerfiles
- [x] Created fly.toml configurations
- [x] Added health check endpoints
- [x] Updated documentation
- [x] Created helper scripts

### Post-Deployment (User Action Required)
- [ ] Create Fly.io apps
- [ ] Provision PostgreSQL with pgvector
- [ ] Provision Redis
- [ ] Create persistent volume
- [ ] Set secrets
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Update CORS settings
- [ ] Add news sources
- [ ] Ingest initial articles
- [ ] Run AI curation
- [ ] Verify end-to-end functionality

## Key Features Preserved

All existing functionality is preserved:
- ✅ RSS feed ingestion
- ✅ AI-powered curation
- ✅ Article summarization
- ✅ Vector embeddings (pgvector)
- ✅ Daily audio briefings
- ✅ AI chat assistant
- ✅ Scheduled tasks (Celery Beat)
- ✅ Media file storage
- ✅ Admin panel
- ✅ REST API
- ✅ CORS support

## Breaking Changes

### For Users
- Frontend URL changed from Vercel to Fly.io
- Need to update any bookmarks or external links

### For Developers
- Vercel-specific configurations removed
- Must use Fly.io CLI for deployment
- Environment variables set via Fly.io secrets
- Nginx serves frontend instead of Vercel Edge Network

## Migration Steps Summary

1. **Preparation**
   - Updated all configuration files
   - Created frontend Dockerfile
   - Enhanced backend Dockerfile
   - Removed Vercel configs

2. **Backend Setup**
   - Create app on Fly.io
   - Provision PostgreSQL
   - Enable pgvector extension
   - Provision Redis
   - Create volume
   - Set secrets
   - Deploy

3. **Frontend Setup**
   - Create app on Fly.io
   - Deploy with Dockerfile

4. **Configuration**
   - Update CORS in backend
   - Verify connectivity

5. **Data Population**
   - Add news sources
   - Run feed ingestion
   - Run AI curation

## Files Modified

### Created
- `/frontend/Dockerfile`
- `/frontend/fly.toml`
- `/frontend/.dockerignore`
- `/frontend/README.md`
- `/DEPLOYMENT.md`
- `/SETUP.md`
- `/DEPLOYMENT_CHECKLIST.md`
- `/MIGRATION_SUMMARY.md`
- `/deploy.sh`

### Modified
- `/backend/Dockerfile`
- `/backend/fly.toml`
- `/backend/genienews_backend/urls.py`
- `/frontend/env.example`
- `/README.md`
- `/backend/README.md`
- `/.dockerignore`

### Deleted
- `/fly.toml` (root duplicate)
- `/frontend/vercel.json`

## Next Steps for User

1. **Review Documentation**
   - Read DEPLOYMENT.md for detailed instructions
   - Review DEPLOYMENT_CHECKLIST.md for step-by-step guide
   - Check SETUP.md for initial setup help

2. **Deploy to Fly.io**
   - Install flyctl
   - Login to Fly.io
   - Follow deployment checklist
   - Test thoroughly

3. **Verify Functionality**
   - Test all features
   - Check health endpoints
   - Monitor logs
   - Verify Celery tasks

4. **Ongoing Maintenance**
   - Use deploy.sh for updates
   - Monitor Fly.io dashboard
   - Review logs regularly
   - Keep dependencies updated

## Support Resources

- **Documentation**: All docs in project root
- **Helper Script**: `./deploy.sh help`
- **Fly.io Docs**: https://fly.io/docs/
- **Community**: https://community.fly.io/

## Migration Status

✅ **COMPLETE** - All code changes implemented and documented

⏳ **PENDING** - User deployment to Fly.io (follow DEPLOYMENT_CHECKLIST.md)

---

**Migration completed successfully! Follow DEPLOYMENT_CHECKLIST.md to deploy to Fly.io.**

