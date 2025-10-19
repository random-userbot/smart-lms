#!/usr/bin/env bash

echo "🚀 Starting Smart LMS..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate || source .venv/Scripts/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Initialize storage if needed
if [ ! -f "storage/users.json" ]; then
    echo "🗄️  Initializing storage..."
    python scripts/init_storage.py
fi

# Run Streamlit app
echo "✅ Launching Smart LMS..."
echo ""
streamlit run app/streamlit_app.py
