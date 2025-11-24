#!/bin/bash

# FINCoach AI Backend Setup Script

echo "🚀 FINCoach AI Backend Setup"
echo "=============================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create database
echo "🗄️  Creating database..."
createdb -h localhost fincoach_db 2>/dev/null || echo "Database might already exist"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Create initial admin user (optional)
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your settings"
echo "2. Run: python -m uvicorn app.main:app --reload"
echo "3. Visit: http://localhost:8000/docs"
