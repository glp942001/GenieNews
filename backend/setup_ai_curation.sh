#!/bin/bash

# AI Curation Setup Script
# This script helps you set up the AI curation system

echo "=========================================="
echo "  GenieNews AI Curation Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    echo "Do you want to:"
    echo "  1) Keep existing .env and just add OpenAI key"
    echo "  2) Backup and create new .env"
    echo "  3) Exit"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo ""
            read -p "Enter your OpenAI API key: " api_key
            if grep -q "OPENAI_API_KEY=" .env; then
                # Replace existing key
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" .env
                else
                    sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$api_key/" .env
                fi
                echo "✅ Updated OPENAI_API_KEY in .env"
            else
                # Add key
                echo "" >> .env
                echo "# OpenAI Configuration" >> .env
                echo "OPENAI_API_KEY=$api_key" >> .env
                echo "AI_MODEL=gpt-4" >> .env
                echo "EMBEDDING_MODEL=text-embedding-3-small" >> .env
                echo "✅ Added OpenAI configuration to .env"
            fi
            ;;
        2)
            cp .env .env.backup
            echo "✅ Backed up existing .env to .env.backup"
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
else
    echo "Creating new .env file..."
    read -p "Enter your OpenAI API key (or press Enter to use mock key): " api_key
    
    if [ -z "$api_key" ]; then
        api_key="sk-mock-key-replace-later"
        echo "⚠️  Using mock API key - you'll need to update it later!"
    fi
    
    cat > .env << EOF
# Django Configuration
DJANGO_SECRET_KEY=django-insecure-jml3u_s!1czxm2!w-0+t-3k\$aqe_h)ntr\$#p-e0pppov*_e^jl
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

# OpenAI Configuration
OPENAI_API_KEY=$api_key
AI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=1000

# AI Curation Configuration
AI_RELEVANCE_KEYWORDS=artificial intelligence,machine learning,AI,deep learning,neural networks,LLM,GPT,transformers,computer vision,NLP,natural language processing,robotics,AI research,generative AI,large language model,autonomous systems,reinforcement learning
AI_RELEVANCE_THRESHOLD=0.3
AI_BATCH_SIZE=20
EOF
    
    echo "✅ Created .env file"
fi

echo ""
echo "=========================================="
echo "  Installing Python Dependencies"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected!"
    echo "Activate your virtual environment first:"
    echo "  source ../venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n): " continue_install
    if [ "$continue_install" != "y" ]; then
        exit 0
    fi
fi

echo "Installing openai and tiktoken..."
pip install openai tiktoken

echo ""
echo "=========================================="
echo "  Running Database Migrations"
echo "=========================================="
echo ""

python manage.py makemigrations
python manage.py migrate

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "✅ Environment configured"
echo "✅ Dependencies installed"
echo "✅ Database migrations applied"
echo ""
echo "Next steps:"
echo "  1. Test the system:"
echo "     python manage.py test_curation --latest"
echo ""
echo "  2. Curate articles:"
echo "     python manage.py shell"
echo "     >>> from news.tasks import curate_articles_task"
echo "     >>> curate_articles_task()"
echo ""
echo "  3. View in admin:"
echo "     python manage.py runserver"
echo "     http://localhost:8000/admin/news/articlecurated/"
echo ""
echo "📚 Full documentation: AI_CURATION_GUIDE.md"
echo "🚀 Quick start: AI_CURATION_QUICKSTART.md"
echo ""

