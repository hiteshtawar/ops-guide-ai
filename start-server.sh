#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "📥 Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
    
    # Check if pydantic is installed
    if ! python -c "import pydantic" 2>/dev/null; then
        echo "📥 Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
fi

# Check if port 8093 is already in use
if lsof -Pi :8093 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8093 is already in use"
    echo "🛑 Stopping existing server..."
    lsof -ti:8093 | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ Port cleared"
fi

# Start the server
echo "🚀 Starting OpsGuide Backend Server..."
echo "📍 Server will be available at http://localhost:8093"
echo ""
python server.py

