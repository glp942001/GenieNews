# Sevalla Environment Variables

Copy these environment variables to your Sevalla project dashboard under "Environment" or "Settings" → "Environment Variables".

## Required Variables

### Django Configuration

```bash
DJANGO_SECRET_KEY=<generate-random-50-char-string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.sevalla.com,.sevalla.app
ENVIRONMENT=production
```

**How to generate DJANGO_SECRET_KEY:**
```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

### Database (Auto-provided by Sevalla)

```bash
DATABASE_URL=<auto-provided-when-you-attach-postgresql-database>
```

### Redis (Auto-provided by Sevalla)

```bash
REDIS_URL=<auto-provided-when-you-attach-redis>
```

### OpenAI API

```bash
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

Get your key from: https://platform.openai.com/api-keys

---

## Optional Variables (Uses defaults if not set)

### AI Model Configuration

```bash
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000
```

### Text-to-Speech Configuration

```bash
TTS_VOICE=nova
TTS_SPEED=1.15
TTS_MODEL=tts-1-hd
```

### Feed Ingestion Configuration

```bash
FEED_FETCH_TIMEOUT=30
FEED_USER_AGENT=GenieNewsBot/1.0
CONTENT_FETCH_TIMEOUT=60
MAX_RETRIES=3
ENABLE_PLAYWRIGHT=false
PLAYWRIGHT_HEADLESS=true
RATE_LIMIT_DELAY=3
```

### AI Curation Configuration

```bash
AI_RELEVANCE_KEYWORDS=artificial intelligence,machine learning,AI,deep learning,neural networks,LLM,GPT,transformers,computer vision,NLP,natural language processing,robotics,AI research,generative AI,large language model,autonomous systems,reinforcement learning
AI_RELEVANCE_THRESHOLD=0.3
AI_BATCH_SIZE=20
```

---

## Setting Variables in Sevalla

1. Login to Sevalla dashboard
2. Go to your project
3. Click "Environment" or "Settings"
4. Add each variable one by one
5. Click "Save" or "Deploy" to apply changes

---

## Notes

- **DATABASE_URL** and **REDIS_URL** are automatically set when you attach those services to your project in Sevalla
- All optional variables have sensible defaults in `settings.py`
- Only set optional variables if you want to override the defaults
- Never commit actual API keys or secrets to your repository

