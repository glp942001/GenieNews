# Audio News Feature - Quick Start Guide 🎙️

## What Changed

✅ **Audio now generates automatically** during weekly article curation  
✅ **Stored in database** - no regeneration needed  
✅ **UI shows "Play"** instead of "Generate" button  

## Test It Right Now

### Option 1: Quick Test (Recommended)

```bash
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
python test_audio_generation.py
```

This will:
- Generate an audio segment from your top 8 articles
- Take 20-30 seconds
- Save to database
- Ready to play in UI!

### Option 2: Full Workflow Test

```bash
cd /Users/gregoriolozano/Desktop/GenieNews/backend
source ../venv/bin/activate
python manage.py shell
```

Then:
```python
from news.tasks import curate_articles_task, generate_audio_segment_task

# Run curation (triggers audio automatically)
curate_articles_task()

# Or run audio generation directly
generate_audio_segment_task()
```

## View Results

### Backend (Django Admin)
1. Go to: `http://localhost:8000/admin/news/audiosegment/`
2. See your generated audio segment
3. Play it directly in admin!

### Frontend (User View)
1. Go to: `http://localhost:5173`
2. Audio player loads automatically at top
3. Click play button to listen
4. Download or view transcript

## How It Works Now

```
BEFORE (Old Way):
User clicks "Generate" → Wait 30s → Audio plays

AFTER (New Way):
Weekly curation runs → Audio auto-generates → User clicks "Play" instantly ✨
```

## Key Points

1. **Automatic**: Audio generates after article curation
2. **Once per cycle**: No duplicate generations
3. **Instant playback**: Loads immediately from database
4. **Cost-effective**: ~$0.20/week instead of $0.20/click

## Production Schedule

Currently set to:
- **Article ingestion**: Monday 2 AM
- **Content extraction**: Monday 4 AM  
- **Curation + Audio**: Hourly (or adjust to weekly)

To change to weekly:
```python
# In backend/genienews_backend/settings.py
'curate-articles-weekly': {
    'task': 'news.tasks.curate_articles_task',
    'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
},
```

## Files Modified

**Backend:**
- `news/tasks.py` - Added automatic audio generation
- `news/views.py` - Simplified to retrieve only

**Frontend:**
- `components/news/AudioPlayer.jsx` - Auto-load audio, removed generate button

## Troubleshooting

**No audio showing?**
```bash
python backend/test_audio_generation.py
```

**Want to regenerate?**
```bash
# Delete old audio in Django admin, then run test script again
```

**Check logs:**
```bash
# Backend logs will show audio generation progress
```

That's it! 🎉

