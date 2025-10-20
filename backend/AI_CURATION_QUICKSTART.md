# AI Curation Quick Start

Get the AI curation system running in 5 minutes!

## Step 1: Environment Setup

Create a `.env` file in the `backend/` directory with your OpenAI API key:

```bash
cd backend

# Create .env file
cat > .env << 'EOF'
# Django Configuration
DJANGO_SECRET_KEY=django-insecure-jml3u_s!1czxm2!w-0+t-3k$aqe_h)ntr$#p-e0pppov*_e^jl
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=genienews
DB_USER=genienews_user
DB_PASSWORD=genienews_password
DB_HOST=localhost
DB_PORT=5432

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Feed Ingestion Configuration
FEED_FETCH_TIMEOUT=30
FEED_USER_AGENT=GenieNewsBot/1.0
CONTENT_FETCH_TIMEOUT=60
MAX_RETRIES=3
ENABLE_PLAYWRIGHT=false
PLAYWRIGHT_HEADLESS=true
RATE_LIMIT_DELAY=3

# OpenAI Configuration - REPLACE WITH YOUR KEY!
OPENAI_API_KEY=sk-your-actual-openai-key-here
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000

# AI Curation Configuration
AI_RELEVANCE_KEYWORDS=artificial intelligence,machine learning,AI,deep learning,neural networks,LLM,GPT,transformers,computer vision,NLP,natural language processing,robotics,AI research,generative AI,large language model,autonomous systems,reinforcement learning
AI_RELEVANCE_THRESHOLD=0.3
AI_BATCH_SIZE=20
EOF
```

**IMPORTANT:** Replace `sk-your-actual-openai-key-here` with your real OpenAI API key from https://platform.openai.com/api-keys

## Step 2: Install Dependencies

```bash
# Activate your virtual environment
source ../venv/bin/activate  # or wherever your venv is

# Install new packages
pip install openai tiktoken
```

## Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 4: Test the System

Test curation on a single article (without saving):

```bash
# First, make sure you have some articles
python manage.py shell
>>> from news.models import ArticleRaw
>>> ArticleRaw.objects.count()
>>> exit()

# If you have articles, test curation
python manage.py test_curation --latest

# If no articles, ingest some first
python manage.py shell
>>> from news.tasks import ingest_single_feed_task
>>> # Create a source first in admin or shell
>>> exit()
```

## Step 5: Run Full Curation

Once test passes, curate all articles:

```bash
python manage.py shell
```

```python
from news.tasks import curate_articles_task

# Curate up to 20 articles
result = curate_articles_task()
print(result)
```

## Step 6: View Results in Admin

1. Start Django server:
   ```bash
   python manage.py runserver
   ```

2. Go to http://localhost:8000/admin/news/articlecurated/

3. You'll see:
   - Color-coded relevance scores
   - AI-generated tags
   - Summary previews
   - Cover images

## Verify Auto-Curation Works

To test automatic curation after feed ingestion:

```bash
python manage.py shell
```

```python
from news.tasks import ingest_single_feed_task
from news.models import Source

# Get a source (or create one first)
source = Source.objects.first()

# Ingest feed (should auto-trigger curation)
result = ingest_single_feed_task(source.id)
print(result)

# Check if curation was triggered
print(f"Curation triggered: {result.get('curation_triggered', False)}")
```

## For Production: Start Celery Workers

For automatic background processing:

```bash
# Terminal 1: Start Celery worker
celery -A genienews_backend worker --loglevel=info

# Terminal 2: Start Celery Beat (for hourly curation)
celery -A genienews_backend beat --loglevel=info

# Terminal 3: Django server
python manage.py runserver
```

## Cost Estimate

Testing with GPT-4:
- Single article: ~$0.03-0.06
- 10 articles: ~$0.30-0.60
- 100 articles: ~$3-6

To save costs during development:
1. Use GPT-3.5-turbo instead (10x cheaper):
   ```bash
   # In .env
   AI_MODEL=gpt-3.5-turbo
   ```

2. Test with `test_curation` command first (doesn't save, just shows output)

## Troubleshooting

### "OpenAI API error: Incorrect API key"
- Double-check your API key in `.env`
- Make sure it starts with `sk-`
- Verify it's active at https://platform.openai.com/api-keys

### "No uncurated articles found"
- Run feed ingestion first to get articles
- Check `ArticleRaw` in admin

### "Rate limit exceeded"
- Your OpenAI account has rate limits
- Wait a minute and try again
- Consider upgrading your OpenAI plan

## Next Steps

1. ✅ Test curation works
2. ✅ View results in admin
3. ✅ Set up automatic curation with Celery
4. 📚 Read full guide: `AI_CURATION_GUIDE.md`
5. 🚀 Integrate with frontend API

## Key Files Reference

- **AI Service**: `news/ai_service.py` - OpenAI integration
- **Curation Task**: `news/tasks.py` - `curate_articles_task()`
- **Admin**: `news/admin.py` - Enhanced UI
- **Test Command**: `news/management/commands/test_curation.py`
- **Settings**: `genienews_backend/settings.py` - AI config
- **Models**: `news/models.py` - `ArticleCurated` model

## Support

If you get stuck:
1. Check the logs for errors
2. Run `python manage.py test_curation --latest` to debug
3. Verify your OpenAI API key is correct
4. Make sure database migrations ran successfully

Happy curating! 🎉

