#!/bin/bash

# Smart Studio Startup Script

echo "Starting Smart Studio..."
echo "================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if backend dependencies are installed
if [ ! -d "backend/node_modules" ]; then
    echo "Installing backend dependencies..."
    cd backend
    npm install
    cd ..
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "No .env file found. Copy env.example to .env and set it up."
    echo "   cp backend/env.example backend/.env"
    echo "   Then edit backend/.env with your OpenAI API key and Arduino port."
    exit 1
fi

# Start backend server
echo "Starting backend server..."
cd backend
npm start &
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