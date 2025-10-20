# AI Curation System Guide

## Overview

The AI Curation System automatically processes raw RSS feed articles to generate AI-powered summaries, relevance scores, tags, and embeddings. This enables intelligent content filtering, semantic search, and personalized recommendations focused on AI and technology news.

## Architecture

### Components

1. **AI Service** (`news/ai_service.py`)
   - OpenAI integration for GPT-4 and embeddings
   - Summary generation (short and detailed)
   - Relevance scoring for AI/tech content
   - Tag extraction
   - Vector embeddings (1536 dimensions)

2. **Curation Task** (`news/tasks.py`)
   - Celery task for batch processing articles
   - Automatic triggering after feed ingestion
   - Hourly scheduled task for missed articles
   - Error handling and fallback mechanisms

3. **Admin Interface** (`news/admin.py`)
   - Visual indicators for curation status
   - Manual curation triggers
   - Rich display of AI-generated content
   - Color-coded relevance scores

4. **Testing Command** (`news/management/commands/test_curation.py`)
   - Test curation on single articles
   - Preview AI outputs without saving
   - Validate API configuration

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New packages added:
- `openai>=1.0.0` - OpenAI API client
- `tiktoken>=0.5.0` - Token counting for OpenAI models

### 2. Configure Environment Variables

Create or update your `.env` file in the `backend/` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-actual-openai-api-key-here
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000

# AI Curation Configuration
AI_RELEVANCE_KEYWORDS=artificial intelligence,machine learning,AI,deep learning,neural networks,LLM,GPT,transformers,computer vision,NLP,natural language processing,robotics,AI research,generative AI,large language model,autonomous systems,reinforcement learning
AI_RELEVANCE_THRESHOLD=0.3
AI_BATCH_SIZE=20
```

**Important:** Replace `sk-mock-key-replace-later` with your actual OpenAI API key from https://platform.openai.com/api-keys

### 3. Run Database Migrations

The system requires a new field in ArticleRaw:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Usage

### Automatic Curation (Recommended)

Articles are automatically curated after feed ingestion:

1. **After Feed Ingestion**: When `ingest_single_feed_task` creates new articles, it automatically triggers `curate_articles_task`

2. **Hourly Schedule**: A Celery Beat task runs every hour to catch any missed articles

No manual intervention required!

### Manual Curation

#### Via Django Admin

1. Go to `/admin/news/articleraw/`
2. Select articles you want to curate
3. Choose "Curate selected articles with AI" from the Actions dropdown
4. Click "Go"

#### Via Django Shell

```python
from news.tasks import curate_articles_task

# Curate up to 20 articles
result = curate_articles_task()
print(result)

# Curate specific batch size
result = curate_articles_task(batch_size=10)
print(result)
```

#### Via Celery (Async)

```python
from news.tasks import curate_articles_task

# Queue task
task = curate_articles_task.delay(batch_size=20)

# Check status
print(task.status)

# Get result (blocks until complete)
result = task.get()
print(result)
```

### Testing Curation

Test the AI curation system on a single article without saving:

```bash
# Test on a specific article ID
python manage.py test_curation 123

# Test on the latest uncurated article
python manage.py test_curation --latest

# Show the article text being processed
python manage.py test_curation --latest --show-text
```

This command shows:
- Article information
- Generated summaries (short and detailed)
- Relevance score with color-coded assessment
- Extracted tags
- Embedding generation details
- Available media assets

Perfect for:
- Validating your OpenAI API key
- Testing prompt changes
- Understanding AI outputs
- Debugging issues

## How It Works

### 1. Article Selection

The system queries for `ArticleRaw` objects that don't have an associated `ArticleCurated` record:

```python
uncurated_articles = ArticleRaw.objects.filter(
    curated__isnull=True
).select_related('source').prefetch_related('media_assets')[:batch_size]
```

### 2. Content Preparation

Combines available content for best AI analysis:

```python
article_text = article.summary_feed
if article.raw_html:
    article_text = article.raw_html[:10000] + " " + article.summary_feed
```

### 3. AI Processing

For each article:

1. **Summaries**: Calls GPT-4 to generate:
   - Short summary (1-2 sentences) for feed cards
   - Detailed summary (3-4 paragraphs) with key insights

2. **Relevance Score** (0-1): Combines:
   - Keyword matching (30% weight)
   - AI semantic analysis (70% weight)
   - Focuses on AI/tech relevance

3. **Tags**: GPT-4 extracts specific technical tags:
   - Example: `["GPT-4", "natural-language-processing", "OpenAI"]`
   - Not generic terms like "technology"

4. **Embeddings**: Generates 1536-dimensional vector from detailed summary
   - Enables semantic search
   - Powers recommendation systems
   - Stored in pgvector database

5. **Cover Media**: Selects first image from article's media assets

### 4. Error Handling

Each AI operation has fallbacks:
- Failed summaries → Use original title/summary
- Failed relevance → Default to 0.5
- Failed tags → Extract from title or use `['ai', 'technology']`
- Failed embeddings → Zero vector `[0.0] * 1536`

Processing continues even if individual operations fail.

## Cost Considerations

### OpenAI API Costs (Approximate)

Per article (assuming 2000 tokens input):
- **GPT-4**: $0.03 - $0.06 per article (summaries + tags + relevance)
- **Embeddings**: $0.0001 per article

For 100 articles: ~$3-6

### Cost Optimization Tips

1. **Use GPT-3.5-Turbo**: Change `AI_MODEL=gpt-3.5-turbo` in `.env`
   - 10x cheaper than GPT-4
   - Still produces good summaries
   - Cost: ~$0.003 per article

2. **Adjust Batch Size**: Lower `AI_BATCH_SIZE` to process fewer articles per run

3. **Filter by Keyword Score**: The system already skips AI calls for articles with keyword score < 0.1

4. **Cache Results**: ArticleCurated records are permanent; no re-processing

## Monitoring

### Via Celery Logs

```bash
# Watch Celery worker logs
celery -A genienews_backend worker --loglevel=info
```

Look for:
- `"Starting AI curation task"`
- `"Successfully curated article X: relevance=0.85, tags=5"`
- `"Curation task completed: 18/20 articles curated in 45.2s"`

### Via Django Admin

1. **ArticleRaw Admin**: Shows "✓ Curated" or "⧗ Pending" status
2. **ArticleCurated Admin**: 
   - Color-coded relevance scores
   - Tag badges
   - Summary previews
   - Embedding information

### Via Task Results

```python
from news.tasks import curate_articles_task

result = curate_articles_task()
print(result)
# {
#   "status": "completed",
#   "articles_processed": 20,
#   "articles_created": 18,
#   "errors_count": 2,
#   "errors": [...],
#   "execution_time_seconds": 45.23
# }
```

## Relevance Scoring

### Scoring Criteria

Articles are scored 0-1 based on AI/tech relevance:

- **0.7-1.0 (High)**: Core AI/ML content
  - AI research papers and breakthroughs
  - New AI model releases (GPT, Claude, etc.)
  - Major AI company news
  - ML technique innovations

- **0.4-0.7 (Medium)**: AI-adjacent content
  - Tech news with AI angle
  - AI applications in other fields
  - AI policy and ethics discussions
  - Emerging tech related to AI

- **0.0-0.4 (Low)**: Tangential or unrelated
  - General tech news
  - Minimal AI connection
  - Non-tech content

### Keywords Monitored

Default keywords (configurable in `.env`):
- artificial intelligence, machine learning, AI
- deep learning, neural networks
- LLM, GPT, transformers
- computer vision, NLP, natural language processing
- robotics, autonomous systems
- reinforcement learning
- generative AI, large language model

### Future: Fine-Tuning

The relevance scoring can be enhanced with:
- User feedback (like/dislike on articles)
- Click-through rates
- Time spent reading
- Custom topic preferences

## Celery Beat Schedule

Configured in `settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'ingest-feeds-weekly': {
        'task': 'news.tasks.ingest_all_feeds_task',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Monday 2 AM
    },
    'curate-articles-hourly': {
        'task': 'news.tasks.curate_articles_task',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

Start Celery Beat:

```bash
celery -A genienews_backend beat --loglevel=info
```

## Troubleshooting

### "OpenAI API error: Incorrect API key provided"

- Check your `OPENAI_API_KEY` in `.env`
- Ensure it starts with `sk-`
- Verify key is active at https://platform.openai.com/api-keys

### "Rate limit exceeded"

- OpenAI has rate limits on API calls
- The system automatically retries with exponential backoff
- Consider reducing `AI_BATCH_SIZE`
- Upgrade OpenAI plan for higher limits

### "No uncurated articles found"

- All articles have been curated
- Create new articles via feed ingestion first
- Check ArticleRaw in admin to verify

### Articles not being curated automatically

1. Verify Celery worker is running:
   ```bash
   celery -A genienews_backend worker --loglevel=info
   ```

2. Check Celery Beat is running for hourly tasks:
   ```bash
   celery -A genienews_backend beat --loglevel=info
   ```

3. Check logs for errors:
   ```bash
   tail -f celery.log
   ```

### Embeddings not stored correctly

- Ensure pgvector extension is installed in PostgreSQL
- Verify `DATABASES` configuration in `settings.py`
- Check that migration was run: `python manage.py migrate news`

## API Integration

### Using Curated Articles in API

Curated articles are already exposed via the REST API:

```bash
# List curated articles
GET /api/news/articles/

# Get specific article
GET /api/news/articles/{id}/

# Filter by relevance
GET /api/news/articles/?relevance_score__gte=0.7

# Order by relevance
GET /api/news/articles/?ordering=-relevance_score
```

### Response Format

```json
{
  "id": 123,
  "title": "OpenAI Releases GPT-5",
  "summary_short": "OpenAI announces GPT-5 with 10T parameters...",
  "summary_detailed": "In a major announcement today...",
  "relevance_score": 0.95,
  "ai_tags": ["GPT-5", "OpenAI", "large-language-models", "AI-research"],
  "cover_media": {
    "url": "https://example.com/image.jpg",
    "type": "image"
  },
  "source": {
    "name": "TechCrunch",
    "url": "https://techcrunch.com"
  },
  "published_at": "2025-10-17T12:00:00Z"
}
```

## Future Enhancements

### Planned Features

1. **Semantic Search**: Use embeddings for vector similarity search
2. **Personalization**: User-specific relevance scoring
3. **Topic Clustering**: Group articles by semantic similarity
4. **Sentiment Analysis**: Track sentiment trends in AI news
5. **Multi-language Support**: Process non-English articles
6. **Custom Models**: Fine-tune relevance scoring with user feedback

### Extending the System

Add custom AI processing in `ai_service.py`:

```python
def custom_analysis(self, article_text: str) -> Dict:
    """Add your custom AI analysis here."""
    # Example: Extract companies mentioned
    # Example: Classify article type
    # Example: Generate key takeaways
    pass
```

Update `curate_articles_task` to use custom analysis:

```python
custom_data = ai_service.custom_analysis(article_text)
curated_article.custom_field = custom_data
```

## Support

For issues or questions:
1. Check logs: `celery.log` and Django logs
2. Test with management command: `python manage.py test_curation --latest`
3. Verify OpenAI API key and quota
4. Review error messages in `ArticleCurated` creation

## Summary

The AI Curation System transforms raw RSS feeds into intelligent, curated content:
- ✅ Automatic processing after ingestion
- ✅ High-quality AI summaries
- ✅ Relevance scoring for AI/tech focus
- ✅ Technical tag extraction
- ✅ Vector embeddings for semantic search
- ✅ Robust error handling
- ✅ Easy testing and monitoring
- ✅ Cost-effective with configurable models

Get started by setting your OpenAI API key and running your first test!

