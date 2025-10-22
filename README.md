# GenieNews

AI-powered news aggregation and curation platform with daily audio briefings.

## Overview

GenieNews is a full-stack application that aggregates news from various RSS feeds, uses AI to curate and summarize articles, and generates daily audio briefings.

### Features

- 🤖 **AI-Powered Curation**: Automatically ranks and filters articles based on relevance
- 📰 **Multi-Source Aggregation**: Collects news from multiple RSS feeds
- 🎙️ **Daily Audio Briefings**: AI-generated audio summaries of top stories
- 💬 **AI Chat Assistant**: Interactive chat to discuss articles and news topics
- 🔍 **Semantic Search**: Vector-based similarity search using pgvector
- ⚡ **Real-time Updates**: Automated feed ingestion with Celery

## Tech Stack

### Backend
- **Framework**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL with pgvector extension
- **Cache/Queue**: Redis
- **Task Queue**: Celery with Celery Beat
- **AI**: OpenAI GPT-4 and TTS
- **Server**: Gunicorn

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router

### Infrastructure
- **Hosting**: Sevalla (unified deployment)
- **Database**: PostgreSQL with pgvector
- **Cache**: Redis for Celery
- **Storage**: Persistent storage for media files

## Quick Start

### Local Development

See detailed setup instructions:
- [Backend Setup](./backend/README.md)
- [Frontend Setup](./frontend/README.md)

### Production Deployment

See the [Sevalla Deployment Guide](./SEVALLA_DEPLOYMENT.md) for complete instructions on deploying to Sevalla.

**Quick Summary:**
- Push your code to GitHub/GitLab
- Connect repository to Sevalla
- Add PostgreSQL and Redis
- Configure environment variables
- Deploy!

## Project Structure

```
GenieNews/
├── backend/              # Django REST API
│   ├── genienews_backend/   # Project settings
│   ├── news/                # Main Django app
│   ├── media/               # Uploaded/generated files
│   ├── Dockerfile           # Backend container
│   └── fly.toml             # Fly.io configuration
├── frontend/             # React SPA
│   ├── src/                 # React components
│   ├── Dockerfile           # Frontend container
│   └── fly.toml             # Fly.io configuration
├── DEPLOYMENT.md         # Deployment guide
└── README.md            # This file
```

## Key Components

### Backend Architecture

- **Models**: Source, ArticleRaw, ArticleCurated, MediaAsset, UserInteraction, AudioSegment
- **Tasks**: Feed ingestion, content extraction, AI curation, audio generation
- **API Endpoints**: Articles, chat, audio segments, interactions

### Frontend Features

- **Home**: Latest AI-curated news articles
- **AI Chat**: Interactive news assistant
- **Audio Player**: Daily news briefings
- **Responsive Design**: Mobile-friendly interface

## Development

### Backend Development

```bash
cd backend
source ../venv/bin/activate
python manage.py runserver
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Celery Worker (Optional for development)

```bash
cd backend
celery -A genienews_backend worker -l info
celery -A genienews_backend beat -l info
```

## Deployment

The application is deployed on Sevalla as a unified app:

- **Combined App**: Django serves both API and React frontend
- **Processes**: Web server, Celery worker, Celery beat
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis for Celery tasks

For detailed deployment instructions, see [SEVALLA_DEPLOYMENT.md](./SEVALLA_DEPLOYMENT.md).

## Environment Variables

See [ENV_VARIABLES_SEVALLA.md](./ENV_VARIABLES_SEVALLA.md) for complete list of environment variables.

**Required for Sevalla:**
- `DJANGO_SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection (auto-provided by Sevalla)
- `REDIS_URL` - Redis connection (auto-provided by Sevalla)
- `OPENAI_API_KEY` - OpenAI API key
- `DJANGO_DEBUG` - Set to `False` in production
- `DJANGO_ALLOWED_HOSTS` - Set to `.sevalla.com,.sevalla.app`

**Local Development:**
- Copy `backend/.env.example` to `backend/.env`
- Update with your local database credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the [Deployment Guide](./DEPLOYMENT.md) for common problems
- Review the backend and frontend README files

---

Built with ❤️ using Django, React, and OpenAI
