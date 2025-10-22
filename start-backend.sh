#!/bin/bash

# GenieNews Backend Startup Script
echo "🚀 Starting GenieNews Backend Server..."
echo ""

# Check if we're in the right directory
if [ ! -f "backend/manage.py" ]; then
    echo "❌ Error: Please run this script from the GenieNews project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /path/to/GenieNews"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Error: Virtual environment not found at ../venv"
    echo "   Please run: python -m venv venv"
    echo "   Then: source venv/bin/activate"
    echo "   Then: pip install -r backend/requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../venv/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Error: Django not found in virtual environment"
    echo "   Please run: pip install -r requirements.txt"
    exit 1
fi

# Check if database is set up
if [ ! -f "db.sqlite3" ] && [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: No database found. Running migrations..."
    python manage.py migrate
fi

# Start the server
echo "🌐 Starting Django development server..."
echo "   Backend will be available at: http://localhost:8000"
echo "   Admin panel: http://localhost:8000/admin/"
echo "   API endpoint: http://localhost:8000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
