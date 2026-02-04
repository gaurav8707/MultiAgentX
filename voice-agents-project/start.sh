#!/bin/bash

# Voice Agents - Quick Start Script
# This script starts both backend and frontend servers

set -e

echo "🎙️ Voice Agents - Starting Application..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists in backend
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found in backend directory${NC}"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo -e "${RED}Please edit backend/.env and add your GOOGLE_API_KEY${NC}"
    exit 1
fi

# Check for GOOGLE_API_KEY
if ! grep -q "GOOGLE_API_KEY=." backend/.env; then
    echo -e "${RED}❌ GOOGLE_API_KEY not set in backend/.env${NC}"
    echo "Please add your Google API key to backend/.env"
    exit 1
fi

echo -e "${GREEN}✅ Configuration found${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "🚀 Starting Backend Server..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Start frontend
echo "🚀 Starting Frontend Server..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎙️ Voice Agents is running!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait
