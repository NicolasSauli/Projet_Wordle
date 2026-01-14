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

# Start backend server in background
echo "Starting backend server on http://localhost:8000..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start frontend server
echo "Starting frontend server on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "==============================="
echo "  Servers are running!"
echo "==============================="
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo ""

# Trap to kill both processes on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for processes
wait
