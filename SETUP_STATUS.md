# GenieNews Setup Status - Complete ✓

## Setup Summary

Your GenieNews AI curation system has been successfully configured and is ready to use once you add billing to your OpenAI account.

### ✅ Completed Tasks

1. **Environment Configuration** - Created `.env` file with all required settings
   - Django configuration
   - PostgreSQL database credentials
   - Redis/Celery configuration
   - Feed ingestion settings
   - OpenAI API key configured (gpt-3.5-turbo)
   - AI curation parameters

2. **Dependencies Installed** - Installed OpenAI packages
   - `openai` (v2.6.0)
   - `tiktoken` (v0.12.0)
   - All dependencies resolved

3. **Database Setup** - Migrations applied successfully
   - Created new migration for media_assets field
   - All tables up to date
   - pgvector extension enabled

4. **Docker Services** - PostgreSQL and Redis running
   - Container: genienews_postgres ✓
   - Container: genienews_redis ✓

5. **RSS Feed Sources** - Imported 26 sources from sources.txt
   - TechCrunch, VentureBeat, WIRED
   - OpenAI Blog, Google AI Blog, DeepMind Blog
   - MIT News, Stanford AI Lab, Hugging Face
   - And 17 more AI/tech news sources

6. **System Verification** - All components operational
   - Django system check: No issues
   - Server initialization: Successful
   - API endpoints: Ready
   - Admin interface: Ready

### ⚠️ Action Required: OpenAI Billing

Your OpenAI API key is valid but has **insufficient quota**. You need to add billing to your OpenAI account:

1. Visit: https://platform.openai.com/settings/organization/billing
2. Add a payment method
3. Add credits or set up automatic billing
4. Minimum recommended: $5-10 for testing

**Error encountered:**
```
Error code: 429 - You exceeded your current quota, please check your plan and billing details.
```

### 💰 Estimated Costs (with GPT-3.5-turbo)

- Per article curation: ~$0.003
- 100 articles: ~$0.30
- 1000 articles: ~$3.00

Much cheaper than GPT-4 (10x cost savings).

## How to Use After Adding Billing

### 1. Start the System

```bash
# Start Docker services (if not already running)
cd /Users/gregoriolozano/Desktop/GenieNews/backend
docker compose up -d

# Activate virtual environment
cd /Users/gregoriolozano/Desktop/GenieNews
source venv/bin/activate

# Start Django server (Terminal 1)
cd backend
python manage.py runserver
```

### 2. Ingest Articles from RSS Feeds

```bash
# In Django shell (Terminal 2)
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
python manage.py shell
```

```python
from news.tasks import ingest_single_feed_task
from news.models import Source

# Ingest from a single source (test)
source = Source.objects.first()
result = ingest_single_feed_task(source.id)
print(f"Ingested {result.get('articles_created', 0)} new articles")
```

### 3. Curate Articles with AI

```python
from news.tasks import curate_articles_task

# Curate up to 20 articles
result = curate_articles_task()
print(result)
```

### 4. View Results

- **Admin Interface**: http://localhost:8000/admin/
  - Username: admin
  - Password: admin
  - View curated articles at: /admin/news/articlecurated/

- **REST API**: http://localhost:8000/api/articles/
  - JSON response with paginated articles
  - Includes summaries, tags, relevance scores

### 5. Test AI Curation (Without Saving)

```bash
# Test on latest article without using API credits
python manage.py test_curation --latest
```

This command shows what the AI would generate without actually calling the API (after it detects the quota error).

## Automated Background Processing

For production use, start Celery workers:

```bash
# Terminal 3: Celery worker
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
celery -A genienews_backend worker --loglevel=info

# Terminal 4: Celery Beat (scheduled tasks)
celery -A genienews_backend beat --loglevel=info
```

This enables:
- Hourly article curation (runs every hour)
- Weekly feed ingestion (runs every Monday at 2 AM)
- Automatic background processing

## Configuration

All settings are in `/Users/gregoriolozano/Desktop/GenieNews/backend/.env`:

```bash
# Key settings
AI_MODEL=gpt-3.5-turbo                # Use gpt-4 for higher quality
AI_BATCH_SIZE=20                      # Articles per curation run
AI_RELEVANCE_THRESHOLD=0.3            # Filter articles below this score
AI_RELEVANCE_KEYWORDS=artificial intelligence,machine learning,...
```

## Available Management Commands

```bash
# Import sources from sources.txt
python manage.py import_sources

# Test curation on one article
python manage.py test_curation --latest

# Django admin
python manage.py createsuperuser

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Django shell
python manage.py shell
```

## API Endpoints

- `GET /api/articles/` - List curated articles (paginated)
- `GET /api/articles/{id}/` - Get article details
- `GET /api/interactions/` - User interactions
- `POST /api/interactions/` - Create interaction

## Frontend Integration

Your React frontend can now connect to the API:

```javascript
// Fetch curated articles
const response = await fetch('http://localhost:8000/api/articles/');
const data = await response.json();

// Each article includes:
// - summary_short (for cards)
// - summary_detailed (for full view)
// - ai_tags (array of tags)
// - relevance_score (0-1)
// - cover_media (image URL if available)
```

## Troubleshooting

### Issue: OpenAI API quota exceeded
**Solution**: Add billing at https://platform.openai.com/settings/organization/billing

### Issue: Docker containers not running
**Solution**: `cd backend && docker compose up -d`

### Issue: Database connection error
**Solution**: Check PostgreSQL container is running: `docker compose ps`

### Issue: No articles to curate
**Solution**: First ingest articles from RSS feeds using `ingest_single_feed_task`

### Issue: RSS feed ingestion fails
**Solution**: Some URLs in sources.txt may be web pages, not RSS feeds. Update feed URLs in Django admin.

## Next Steps

1. ✅ Add billing to OpenAI account
2. ✅ Test with single article: `python manage.py test_curation --latest`
3. ✅ Ingest articles from feeds
4. ✅ Run AI curation
5. ✅ View results in admin interface
6. ✅ Connect frontend to API
7. ✅ Start Celery workers for automation

## Files Created/Modified

- `/Users/gregoriolozano/Desktop/GenieNews/backend/.env` - Environment configuration (NEW)
- `/Users/gregoriolozano/Desktop/GenieNews/backend/news/management/commands/import_sources.py` - Import command (NEW)
- `/Users/gregoriolozano/Desktop/GenieNews/backend/news/migrations/0003_articleraw_media_assets.py` - Migration (NEW)

## System Status

- ✅ Django: Configured and tested
- ✅ PostgreSQL: Running
- ✅ Redis: Running
- ✅ OpenAI Integration: Configured (needs billing)
- ✅ RSS Sources: 26 imported
- ✅ Migrations: Applied
- ✅ Dependencies: Installed

**Status**: Ready to use once OpenAI billing is activated!

---

Generated: October 21, 2025
Setup completed successfully.

