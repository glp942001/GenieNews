# 🔧 Console Errors Fix Guide

## The Problem

You're seeing these console errors because the **backend server isn't running**:

```
Failed to load resource: net::ERR_CONNECTION_REFUSED
Error fetching articles: TypeError: Failed to fetch
```

The frontend is trying to connect to `http://localhost:8000` but there's no server running there.

## ✅ Quick Fix (2 minutes)

### Option 1: Use the Startup Script (Easiest)

```bash
# From the GenieNews project root
./start-backend.sh
```

### Option 2: Manual Start

```bash
# 1. Open terminal in project root
cd /Users/gregoriolozano/Desktop/GenieNews

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start backend server
cd backend
python manage.py runserver
```

### Option 3: If You Don't Have Data Yet

```bash
# 1. Start backend
cd backend
source ../venv/bin/activate
python manage.py runserver

# 2. In a NEW terminal, run data ingestion
cd backend
source ../venv/bin/activate
python manage.py import_sources
python manage.py shell -c "from news.tasks import ingest_all_feeds_task, curate_articles_task; ingest_all_feeds_task(); curate_articles_task()"
```

## 🎯 What Should Happen

After starting the backend:

1. **Backend running**: http://localhost:8000
2. **API working**: http://localhost:8000/api/news/articles/
3. **Frontend loads**: No more console errors
4. **Articles appear**: You'll see news articles in the UI

## 🔍 Debugging Steps

### Check if Backend is Running

Visit these URLs in your browser:

- ✅ **Backend health**: http://localhost:8000/admin/
- ✅ **API test**: http://localhost:8000/api/news/articles/
- ❌ **If these fail**: Backend isn't running

### Check Console Logs

The frontend now shows helpful error messages:

- **"Backend Server Not Running"** = Start the Django server
- **"No Articles Available"** = Run data ingestion
- **"Error Loading Articles"** = Check backend logs

### Check API Configuration

Open browser console and look for:

```javascript
API Configuration: {
  VITE_API_URL: undefined,  // This is normal for local dev
  API_BASE_URL: "http://localhost:8000/api",
  NODE_ENV: "development"
}
```

## 🚀 For Production Deployment

When you deploy to production:

1. **Frontend** goes to Vercel
2. **Backend** goes to Fly.io  
3. **Environment variable** `VITE_API_URL` points to your deployed backend
4. **No more localhost errors!**

## 📋 Common Issues

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r backend/requirements.txt
```

### "Database doesn't exist" errors
```bash
cd backend
python manage.py migrate
```

### "No articles" after backend starts
```bash
# Run data ingestion
cd backend
python manage.py import_sources
python manage.py shell -c "from news.tasks import ingest_all_feeds_task, curate_articles_task; ingest_all_feeds_task(); curate_articles_task()"
```

## ✅ Success Indicators

You'll know it's working when:

- ✅ No red errors in console
- ✅ Backend responds at http://localhost:8000
- ✅ Articles load in the frontend
- ✅ AI chat works
- ✅ Audio player loads

---

**The console errors are just telling you the backend needs to be started - that's it!** 🎉
