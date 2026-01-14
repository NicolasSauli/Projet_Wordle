#!/bin/bash

# Wordle Multiplayer - Startup Script

echo "==============================="
echo "   WORDLE MULTIPLAYER"
echo "==============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r backend/requirements.txt --quiet

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Start server
echo ""
echo "Starting server on port 8000..."
echo ""
echo "==============================="
echo "  Server is running!"
echo "==============================="
echo ""
echo "  Local:   http://localhost:8000"
echo "  Network: http://$LOCAL_IP:8000"
echo ""
echo "  Share the Network URL with friends!"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
