# How to Run GenieNews

Your GenieNews application is **fully set up and running**! 🎉

## 🚀 Current Status

**Backend**: Running on http://localhost:8000
**Frontend**: Running on http://localhost:3000

Both servers are currently active and serving content.

## 📱 Access Your Application

Open your browser and go to:
```
http://localhost:3000
```

You'll see your GenieNews homepage with:
- 8 AI-ranked news articles
- Articles displayed in an attractive grid layout
- Click any article card to open the original source in a new tab

## 🔄 If Servers Are Not Running

If you need to restart the servers later, use these commands:

### Start Backend (Terminal 1)
```bash
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
python manage.py runserver
```

### Start Frontend (Terminal 2)
```bash
cd /Users/gregoriolozano/Desktop/GenieNews/frontend
npm run dev
```

## 📊 What's Working

✅ **Article Ingestion**: 10 articles from RSS feeds
✅ **AI Curation**: All articles ranked with GPT-3.5-turbo
✅ **Backend API**: Serving articles at `/api/articles/`
✅ **Frontend Display**: Shows top 8 ranked articles
✅ **Clickable Articles**: Opens original source in new tab
✅ **AI-Generated**: Summaries, tags, and relevance scores

## 🎯 Features

1. **AI-Ranked News**: Articles sorted by relevance score (0-1)
2. **Smart Summaries**: GPT-3.5-turbo generated summaries
3. **Tag System**: AI-extracted tags for each article
4. **Source Attribution**: Each article shows its source and time
5. **Direct Links**: Click any article to read the full story at the original source
6. **Real-time Loading**: Fetches latest curated articles from API

## 🔧 Managing Your Application

### View Backend Admin
```
http://localhost:8000/admin/
Username: admin
Password: admin
```

From admin you can:
- View all curated articles with color-coded relevance scores
- Manage RSS feed sources (26 sources imported)
- See article details, tags, and summaries

### Check API Directly
```bash
# Get top 8 articles
curl http://localhost:8000/api/articles/?ordering=-relevance_score&page_size=8

# Get all articles
curl http://localhost:8000/api/articles/
```

## 📈 Add More Articles

To ingest more articles and curate them:

```bash
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
python manage.py shell
```

```python
from news.tasks import ingest_single_feed_task, curate_articles_task
from news.models import Source

# Ingest from a specific source
source = Source.objects.get(name="Tech-Crunch")  # or any source
ingest_single_feed_task(source.id)

# Curate new articles
curate_articles_task()

# Refresh your browser to see new articles
```

## 🎨 Customize

### Adjust Number of Articles
Edit `/Users/gregoriolozano/Desktop/GenieNews/frontend/src/services/api.js`:
```javascript
// Change from 8 to any number
export async function fetchTopArticles(limit = 8) {
```

### Change Relevance Threshold
Edit `/Users/gregoriolozano/Desktop/GenieNews/backend/.env`:
```bash
AI_RELEVANCE_THRESHOLD=0.3  # Increase to be more selective
```

### Switch to GPT-4
For higher quality (but more expensive):
Edit `/Users/gregoriolozano/Desktop/GenieNews/backend/.env`:
```bash
AI_MODEL=gpt-4  # Better quality, ~$0.05/article
```

## 💰 Cost Tracking

Current configuration (GPT-3.5-turbo):
- Per article: ~$0.003
- 100 articles: ~$0.30
- 1000 articles: ~$3.00

## 🛠️ Troubleshooting

### Frontend shows "Error Loading Articles"
- Check backend is running: `curl http://localhost:8000/api/articles/`
- Restart backend if needed

### No articles showing
- Run article ingestion and curation (see "Add More Articles" above)

### Port already in use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or port 3000 for frontend
lsof -ti:3000 | xargs kill -9
```

## 📝 Notes

- **RSS Feeds**: Many URLs in sources.txt are web pages, not RSS feeds. You'll need to update them in Django admin with actual RSS feed URLs for better ingestion.
- **Images**: Articles don't have cover images yet. They're displayed with placeholder icons.
- **Auto-Refresh**: Frontend doesn't auto-refresh. Refresh browser manually to see new articles.

## 🎉 You're All Set!

Your GenieNews application is fully operational with:
- Real AI-powered article ranking
- Beautiful React frontend
- Django REST API backend
- PostgreSQL database with pgvector
- Redis for task queuing
- Celery for background processing

Enjoy your AI-curated news experience! 📰✨

