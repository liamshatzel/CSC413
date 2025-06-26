#!/bin/bash

# Smart Studio Startup Script

echo "Starting Smart Studio..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "No .env file found. Copy env.example to .env and configure your settings."
    echo "   cp backend/env.example backend/.env"
    echo "   Then edit backend/.env with your OpenAI API key and Arduino port."
    exit 1
fi

# Start backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:3001/api/health > /dev/null; then
    echo "Backend server is running on http://localhost:3001"
else
    echo "Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend server
echo "Starting frontend server..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo "Frontend server is running on http://localhost:8000"
echo ""
echo "Smart Studio is ready!"
echo "================================"
echo "Frontend: http://localhost:8000"
echo "Backend:  http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT

# Keep script running
wait 