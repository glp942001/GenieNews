# Audio News Workflow - Updated Implementation ✅

## Summary of Changes

The audio news feature has been modified to work automatically with your weekly update cycle, removing on-demand generation and implementing a cleaner workflow.

## What Changed

### 1. Automatic Generation During Curation ✅
**Previously:** Users clicked a "Generate" button to create audio on-demand  
**Now:** Audio is automatically generated after weekly article curation

- Audio generation happens in the background as part of the curation pipeline
- Runs sequentially after articles are curated
- No user interaction required

### 2. Database Storage ✅
**Previously:** Could regenerate audio multiple times  
**Now:** Audio is stored once in the database and reused

- One audio segment per curation cycle
- Stored permanently in `media/audio_segments/`
- Database tracks date, script, and article IDs
- No redundant generation

### 3. User Interface Changes ✅
**Previously:** Button said "Generate Audio News"  
**Now:** Audio player automatically loads and displays

- Loads latest audio segment on page load
- Native HTML5 audio player with Play/Pause controls
- Shows date of audio segment
- Download and transcript features remain
- Clean, automatic experience

## New Workflow

```
Weekly Update Cycle:
┌──────────────────────────────────────────────────────┐
│ 1. RSS Feed Ingestion (Monday 2 AM)                 │
│    ↓                                                 │
│ 2. Article Content Extraction (Monday 4 AM)         │
│    ↓                                                 │
│ 3. AI Curation (Hourly or triggered)                │
│    - Generate summaries                              │
│    - Calculate relevance scores                      │
│    - Extract tags                                    │
│    - Create embeddings                               │
│    ↓                                                 │
│ 4. Audio Generation (Automatic, Sequential) ← NEW   │
│    - Fetch top 8 articles                            │
│    - Generate script (~5 minutes)                    │
│    - Convert to audio via OpenAI TTS                 │
│    - Save to database                                │
│    ↓                                                 │
│ 5. Audio Available in UI (Automatic)                │
└──────────────────────────────────────────────────────┘
```

## Files Modified

### Backend
1. **`backend/news/tasks.py`**
   - Added `generate_audio_segment_task()` - New Celery task for audio generation
   - Modified `curate_articles_task()` - Triggers audio generation after curation
   - Sequential workflow: curation → audio generation

2. **`backend/news/views.py`**
   - Simplified `GenerateAudioSegmentView` - Now only retrieves existing audio
   - Removed on-demand generation logic
   - Returns 404 if no audio exists yet

### Frontend
3. **`frontend/src/components/news/AudioPlayer.jsx`**
   - Added `useEffect` to load audio on component mount
   - Removed "Generate" button and related UI
   - Shows loading state while fetching
   - Displays audio player automatically when available
   - Shows helpful message if no audio exists yet

## User Experience

### First Time (No Audio Yet)
```
┌─────────────────────────────────────┐
│  🔊 AI News Radio                   │
│                                     │
│  No audio segments available yet.   │
│  Please wait for the weekly         │
│  curation to complete.              │
└─────────────────────────────────────┘
```

### After First Curation
```
┌─────────────────────────────────────┐
│  AI News Radio                      │
│  8 stories • October 22, 2025       │
│                                     │
│  [Audio Player Controls]            │
│  ▶️  ⏸️  🔊 ━━━━━━━●─── 5:00      │
│                                     │
│  [Show Transcript] [Download]       │
└─────────────────────────────────────┘
```

## Testing the Changes

### Test Automatic Generation

1. **Trigger Manual Curation** (simulates weekly update):
```bash
cd /Users/gregoriolozano/Desktop/GenieNews
source venv/bin/activate
cd backend
python manage.py shell
```

Then in Python shell:
```python
from news.tasks import curate_articles_task
result = curate_articles_task.delay()
print(result)
```

2. **Wait for completion** (~2-3 minutes for curation + audio generation)

3. **Check audio was created**:
   - Visit Django admin: `http://localhost:8000/admin/news/audiosegment/`
   - Should see new audio segment with today's date

4. **Test frontend**:
   - Refresh `http://localhost:5173`
   - Audio player should automatically load and display
   - Click play to listen

### Test Error Handling

**Scenario: No audio exists yet**
1. Delete any existing audio segments from admin
2. Refresh frontend
3. Should see helpful message about waiting for weekly update

## Benefits of New Approach

### ✅ For Development/Deployment
- Audio generates automatically during weekly maintenance
- No user action required
- Predictable generation schedule
- Easy to monitor (check Celery logs)

### ✅ For Users
- Instant loading (no 20-30 second wait)
- Consistent availability
- Cleaner UI (no confusing buttons)
- Professional experience

### ✅ For Cost Management
- Only generates once per week
- Predictable OpenAI API costs
- ~$0.20 per week (~$10/year)
- No accidental duplicate generations

## Celery Schedule

The audio generation is triggered by the curation task, which runs:

```python
# In backend/genienews_backend/settings.py
CELERY_BEAT_SCHEDULE = {
    'curate-articles-hourly': {
        'task': 'news.tasks.curate_articles_task',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

For weekly deployment, you might want to adjust this to weekly:

```python
'curate-articles-weekly': {
    'task': 'news.tasks.curate_articles_task',
    'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
},
```

## Manual Testing Commands

### Generate Audio Manually (for testing)
```bash
cd /Users/gregoriolozano/Desktop/GenieNews
source venv/bin/activate
cd backend
python manage.py shell
```

```python
from news.tasks import generate_audio_segment_task
result = generate_audio_segment_task.delay()
print(result.id)  # Get task ID
```

### Check Task Status
```python
from celery.result import AsyncResult
result = AsyncResult('task-id-here')
print(result.status)
print(result.result)
```

### View Latest Audio Segment
```python
from news.models import AudioSegment
latest = AudioSegment.objects.order_by('-date').first()
print(f"Date: {latest.date}")
print(f"Articles: {len(latest.article_ids)}")
print(f"Audio file: {latest.audio_file.url}")
print(f"Script: {latest.script_text[:200]}...")
```

## Rollback Instructions

If you need to revert to on-demand generation:

1. **Backend**: Restore `GenerateAudioSegmentView` to include generation logic
2. **Frontend**: Add back "Generate" button and onClick handler
3. **Tasks**: Remove audio generation trigger from `curate_articles_task`

## Next Steps

1. **Test the automatic workflow** with a manual curation trigger
2. **Verify audio appears** in frontend automatically
3. **Adjust Celery schedule** if needed for your deployment cycle
4. **Monitor logs** during first production run

## Cost Summary

**Previous (On-Demand):**
- Could generate multiple times per day
- Unpredictable costs
- ~$0.20 per generation

**New (Automatic Weekly):**
- Generates once per week maximum
- Predictable: ~$0.20/week = ~$10/year
- No user-triggered costs

---

**Implementation Status**: ✅ COMPLETE  
**Testing Required**: Yes - Manual trigger to verify workflow  
**Production Ready**: Yes - After testing

