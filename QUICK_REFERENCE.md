# GenieNews Quick Reference

Quick commands and information for managing GenieNews on Fly.io.

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Install flyctl
brew install flyctl  # macOS
# or visit: https://fly.io/docs/hands-on/install-flyctl/

# 2. Login
flyctl auth login

# 3. Follow deployment checklist
# See DEPLOYMENT_CHECKLIST.md
```

### Deploy Updates
```bash
# Deploy backend
cd backend && flyctl deploy --app genienews-backend

# Deploy frontend
cd frontend && flyctl deploy --app genienews-frontend

# Or use helper script
./deploy.sh deploy-all
```

## 📋 Helper Script Commands

The `deploy.sh` script provides shortcuts for common operations:

```bash
# Make it executable (first time only)
chmod +x deploy.sh

# Deploy
./deploy.sh deploy-backend        # Deploy backend only
./deploy.sh deploy-frontend       # Deploy frontend only
./deploy.sh deploy-all            # Deploy both

# Status
./deploy.sh status-backend        # Backend status
./deploy.sh status-frontend       # Frontend status
./deploy.sh status-all            # Both statuses

# Logs
./deploy.sh logs-backend          # View backend logs
./deploy.sh logs-frontend         # View frontend logs

# Access
./deploy.sh ssh-backend           # SSH into backend
./deploy.sh open-backend          # Open admin in browser
./deploy.sh open-frontend         # Open frontend in browser
./deploy.sh open-all              # Open both

# Help
./deploy.sh help                  # Show all commands
```

## 🔧 Flyctl Commands

### App Management
```bash
# List your apps
flyctl apps list

# App status
flyctl status --app genienews-backend
flyctl status --app genienews-frontend

# App info
flyctl info --app genienews-backend

# Restart app
flyctl apps restart genienews-backend

# Open in browser
flyctl open --app genienews-frontend
```

### Deployment
```bash
# Deploy from current directory
cd backend
flyctl deploy --app genienews-backend

# Force rebuild (ignore cache)
flyctl deploy --app genienews-backend --no-cache

# Deploy specific Dockerfile
flyctl deploy --app genienews-backend --dockerfile Dockerfile
```

### Logs
```bash
# View recent logs
flyctl logs --app genienews-backend

# Follow logs (real-time)
flyctl logs --app genienews-backend -f

# Filter logs by process
flyctl logs --app genienews-backend | grep worker
flyctl logs --app genienews-backend | grep beat
```

### Secrets Management
```bash
# List secrets (not values)
flyctl secrets list --app genienews-backend

# Set a secret
flyctl secrets set KEY="value" --app genienews-backend

# Set multiple secrets
flyctl secrets set \
  KEY1="value1" \
  KEY2="value2" \
  --app genienews-backend

# Unset a secret
flyctl secrets unset KEY --app genienews-backend
```

### SSH and Console
```bash
# SSH into app
flyctl ssh console --app genienews-backend

# Run one-off command
flyctl ssh console --app genienews-backend -C "python manage.py migrate"

# Connect to PostgreSQL
flyctl postgres connect -a genienews-db

# Connect to Redis (if using Fly.io Redis)
flyctl redis connect genienews-redis
```

### Scaling
```bash
# Scale memory
flyctl scale memory 512 --app genienews-backend
flyctl scale memory 2048 --app genienews-backend

# Scale instances
flyctl scale count 1 --app genienews-backend
flyctl scale count 2 --app genienews-backend

# Scale specific process
flyctl scale count app=2 worker=1 --app genienews-backend

# View current scale
flyctl scale show --app genienews-backend
```

### Database Management
```bash
# List databases
flyctl postgres list

# Database status
flyctl status --app genienews-db

# Connect to database
flyctl postgres connect -a genienews-db

# Create backup
flyctl postgres backup create --app genienews-db

# List backups
flyctl postgres backup list --app genienews-db
```

### Volume Management
```bash
# List volumes
flyctl volumes list --app genienews-backend

# Create volume
flyctl volumes create genienews_media \
  --size 1 \
  --region sjc \
  --app genienews-backend

# Extend volume
flyctl volumes extend <volume-id> --size 2 --app genienews-backend

# Create snapshot
flyctl volumes snapshots create <volume-id> --app genienews-backend

# List snapshots
flyctl volumes snapshots list <volume-id> --app genienews-backend
```

## 🔍 Monitoring

### Health Checks
```bash
# Backend health
curl https://genienews-backend.fly.dev/health/

# Frontend health
curl https://genienews-frontend.fly.dev/health

# Expected response
{"status": "healthy", "service": "genienews-backend"}
```

### API Testing
```bash
# List articles
curl https://genienews-backend.fly.dev/api/articles/

# Get specific article
curl https://genienews-backend.fly.dev/api/articles/1/

# With authentication (if enabled)
curl -H "Authorization: Token YOUR_TOKEN" \
  https://genienews-backend.fly.dev/api/articles/
```

### Check Celery
```bash
# SSH into backend
flyctl ssh console --app genienews-backend

# Check active tasks
celery -A genienews_backend inspect active

# Check scheduled tasks
celery -A genienews_backend inspect scheduled

# Check registered tasks
celery -A genienews_backend inspect registered

# Exit SSH
exit
```

## 🗄️ Database Operations

### Connect to Database
```bash
# Connect via flyctl
flyctl postgres connect -a genienews-db

# Once connected, useful PostgreSQL commands:
\l                              # List databases
\c genienews                    # Connect to database
\dt                             # List tables
\d news_articleraw              # Describe table
\dx                             # List extensions (verify pgvector)
```

### Common Queries
```sql
-- Count articles
SELECT COUNT(*) FROM news_articleraw;
SELECT COUNT(*) FROM news_articlecurated;

-- View sources
SELECT id, name, active FROM news_source;

-- Recent articles
SELECT id, title, published_at 
FROM news_articleraw 
ORDER BY published_at DESC 
LIMIT 10;

-- Top curated articles
SELECT id, raw_article_id, relevance_score 
FROM news_articlecurated 
ORDER BY relevance_score DESC 
LIMIT 10;
```

## 🔐 Secrets Reference

### Required Secrets
```bash
DJANGO_SECRET_KEY           # Django secret key
DJANGO_DEBUG                # False in production
DJANGO_ALLOWED_HOSTS        # .fly.dev
DATABASE_URL                # Auto-set by postgres attach
REDIS_URL                   # From Upstash or fly.io
OPENAI_API_KEY             # Your OpenAI API key
FRONTEND_URL               # Frontend URL for CORS
```

### Optional Secrets
```bash
AI_MODEL                    # Default: gpt-4
EMBEDDING_MODEL             # Default: text-embedding-3-small
TTS_VOICE                   # Default: nova
TTS_SPEED                   # Default: 1.15
TTS_MODEL                   # Default: tts-1-hd
AI_TEMPERATURE              # Default: 0.3
AI_MAX_TOKENS              # Default: 1000
```

## 🛠️ Django Management Commands

### Via SSH
```bash
# SSH into backend
flyctl ssh console --app genienews-backend

# Then run Django commands:
python manage.py migrate                    # Run migrations
python manage.py createsuperuser           # Create admin user
python manage.py collectstatic --noinput   # Collect static files
python manage.py shell                      # Django shell
python manage.py dbshell                   # Database shell

# Custom commands
python manage.py import_sources            # Import RSS sources
python manage.py update_rss_feeds          # Fetch from feeds
python manage.py test_curation             # Run AI curation

# Exit SSH
exit
```

## 📊 Useful Queries & Scripts

### Check System Status
```bash
# Create a status check script
cat > check_status.sh << 'EOF'
#!/bin/bash
echo "=== Backend Status ==="
flyctl status --app genienews-backend
echo ""
echo "=== Frontend Status ==="
flyctl status --app genienews-frontend
echo ""
echo "=== Database Status ==="
flyctl status --app genienews-db
echo ""
echo "=== Backend Health ==="
curl -s https://genienews-backend.fly.dev/health/ | jq
echo ""
echo "=== Frontend Health ==="
curl -s https://genienews-frontend.fly.dev/health
EOF

chmod +x check_status.sh
./check_status.sh
```

### Trigger Feed Ingestion
```bash
flyctl ssh console --app genienews-backend << 'EOF'
python manage.py update_rss_feeds
EOF
```

### View Article Counts
```bash
flyctl postgres connect -a genienews-db << 'EOF'
\c genienews
SELECT 
  (SELECT COUNT(*) FROM news_source WHERE active=true) as active_sources,
  (SELECT COUNT(*) FROM news_articleraw) as raw_articles,
  (SELECT COUNT(*) FROM news_articlecurated) as curated_articles;
\q
EOF
```

## 🚨 Troubleshooting

### App Won't Start
```bash
# Check logs
flyctl logs --app genienews-backend

# Check secrets are set
flyctl secrets list --app genienews-backend

# Verify build succeeded
flyctl status --app genienews-backend

# Try redeploying
flyctl deploy --app genienews-backend --no-cache
```

### Database Connection Issues
```bash
# Verify DATABASE_URL is set
flyctl secrets list --app genienews-backend | grep DATABASE

# Check database is running
flyctl status --app genienews-db

# Try connecting manually
flyctl postgres connect -a genienews-db
```

### Celery Not Working
```bash
# Check worker logs
flyctl logs --app genienews-backend | grep worker

# Verify Redis connection
flyctl secrets list --app genienews-backend | grep REDIS

# SSH and test Celery
flyctl ssh console --app genienews-backend
celery -A genienews_backend inspect active
```

### Frontend Not Loading
```bash
# Check frontend logs
flyctl logs --app genienews-frontend

# Check CORS settings
flyctl secrets list --app genienews-backend | grep FRONTEND

# Test API directly
curl https://genienews-backend.fly.dev/api/articles/
```

## 📱 Mobile Quick Commands

Save these to your notes app for quick access:

```bash
# Deploy all
cd ~/GenieNews && ./deploy.sh deploy-all

# Check status
cd ~/GenieNews && ./deploy.sh status-all

# View logs
cd ~/GenieNews && ./deploy.sh logs-backend

# SSH
flyctl ssh console --app genienews-backend

# Open apps
cd ~/GenieNews && ./deploy.sh open-all
```

## 🌐 URLs

### Production URLs
- Frontend: https://genienews-frontend.fly.dev
- Backend API: https://genienews-backend.fly.dev/api/
- Admin Panel: https://genienews-backend.fly.dev/admin/
- Backend Health: https://genienews-backend.fly.dev/health/
- Frontend Health: https://genienews-frontend.fly.dev/health

### Fly.io Dashboard
- Overview: https://fly.io/dashboard
- Backend App: https://fly.io/apps/genienews-backend
- Frontend App: https://fly.io/apps/genienews-frontend
- Database: https://fly.io/apps/genienews-db

## 📚 Documentation Quick Links

- [Main README](./README.md) - Project overview
- [Setup Guide](./SETUP.md) - Initial setup instructions
- [Deployment Guide](./DEPLOYMENT.md) - Detailed deployment guide
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- [Migration Summary](./MIGRATION_SUMMARY.md) - Changes made
- [Backend README](./backend/README.md) - Backend docs
- [Frontend README](./frontend/README.md) - Frontend docs

## 🆘 Getting Help

1. Check logs: `flyctl logs --app APP_NAME`
2. Review documentation: See links above
3. Fly.io Docs: https://fly.io/docs/
4. Community: https://community.fly.io/
5. Django Docs: https://docs.djangoproject.com/
6. Celery Docs: https://docs.celeryproject.org/

---

**Keep this reference handy for quick operations!**

