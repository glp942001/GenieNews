# GenieNews - Quick Start for Sevalla

Get your GenieNews app deployed on Sevalla in minutes!

## Prerequisites

- ✅ Sevalla account (sign up at https://sevalla.com)
- ✅ Git repository with your code (GitHub/GitLab)
- ✅ OpenAI API key (get from https://platform.openai.com/api-keys)

## 5-Minute Deployment

### 1. Push Your Code

```bash
git add .
git commit -m "Ready for Sevalla deployment"
git push origin main
```

### 2. Create Sevalla Project

1. Login to https://sevalla.com/dashboard
2. Click **"Create New Project"**
3. Choose **"Import from Git"**
4. Select your repository
5. Branch: `main`

### 3. Add Services

**PostgreSQL:**
1. Dashboard → **"Databases"** → **"Add Database"**
2. Type: **PostgreSQL 16**
3. Name: `genienews-db`
4. Click **"Create"**
5. Once created, open SQL console and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

**Redis:**
1. Dashboard → **"Databases"** or **"Redis"**
2. Click **"Add Redis"**
3. Name: `genienews-redis`
4. Click **"Create"**

### 4. Set Environment Variables

Go to Project → **"Environment"** and add:

```bash
# Required
DJANGO_SECRET_KEY=<generate-this>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.sevalla.com,.sevalla.app
ENVIRONMENT=production
OPENAI_API_KEY=sk-your-key-here

# Auto-provided (check these exist)
DATABASE_URL=<should-be-set-automatically>
REDIS_URL=<should-be-set-automatically>
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

### 5. Enable Multi-Process

Dashboard → **"Processes"** → Enable:
- ✅ **web** (1 instance)
- ✅ **worker** (1 instance) 
- ✅ **beat** (1 instance)

### 6. Deploy!

Click **"Deploy"** button.

Wait for build to complete (2-5 minutes).

### 7. Create Admin User

Dashboard → **"Console"**:
```bash
cd backend && python manage.py createsuperuser
```

### 8. Add News Sources

1. Visit: `https://your-project.sevalla.app/admin/`
2. Login with admin credentials
3. Add Sources (RSS feeds)

### 9. Trigger Initial Data

Console:
```bash
cd backend && python manage.py update_rss_feeds
cd backend && python manage.py test_curation
```

### 10. Visit Your App!

🎉 **Done!** Visit: `https://your-project.sevalla.app`

---

## Troubleshooting

**Build fails?**
- Check build logs
- Verify `nixpacks.toml` exists
- Ensure `Procfile` exists

**App won't start?**
- Verify environment variables are set
- Check DATABASE_URL and REDIS_URL exist
- View application logs

**Frontend not loading?**
- Verify frontend built successfully (check build logs)
- Ensure `frontend/dist` directory exists after build

**Need help?**
- See full guide: [SEVALLA_DEPLOYMENT.md](./SEVALLA_DEPLOYMENT.md)
- Check Sevalla docs: https://sevalla.com/docs

---

## What Sevalla Does Automatically

✅ Installs Python and Node dependencies  
✅ Builds React frontend  
✅ Collects Django static files  
✅ Runs database migrations  
✅ Starts all processes (web, worker, beat)  
✅ Provides SSL certificate (HTTPS)  
✅ Auto-deploys on git push  

---

## Next Steps

1. **Add more news sources** in admin panel
2. **Monitor logs** in Sevalla dashboard
3. **Scale processes** if needed
4. **Add custom domain** (optional)

---

**That's it! Your unified Django + React app is live on Sevalla! 🚀**

