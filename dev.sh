#!/bin/bash

echo "=== JUVENILE IMMIGRATION PROJECT - LOCAL DEVELOPMENT ==="
echo "Starting backend and frontend for local development"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    # Kill all background jobs
    jobs -p | xargs -r kill
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not installed."
    exit 1
fi

echo "✅ Dependencies check passed"
echo ""

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."

# Check if .venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "� Installing Python dependencies..."
cd api
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in api directory"
    exit 1
fi

pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Python dependencies installed"

# Go back to root
cd ..

# Install Node.js dependencies if needed
echo "📦 Checking Node.js dependencies..."
cd frontend
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

# Install Node dependencies
npm install > /dev/null 2>&1
echo "✅ Node.js dependencies installed"

# Go back to root
cd ..

echo ""
echo "🚀 Starting development servers..."
echo ""

# Start backend server
echo "🐍 Starting Python backend server on http://localhost:5000..."
export PYTHONPATH="$(pwd)"
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server with local API configuration
echo "⚛️  Starting frontend dev server on http://localhost:5173..."
cd frontend
export PUBLIC_API_URL=http://localhost:5000/api
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development servers started!"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:5000/api"
echo "🩺 Health check: http://localhost:5000/api/health"
echo "🐍 Python venv: .venv (activated)"
echo ""
echo "📖 Available pages:"
echo "   • Home: http://localhost:5173/"
echo "   • Data: http://localhost:5173/data"
echo "   • Findings: http://localhost:5173/findings"
echo "   • About: http://localhost:5173/about"
echo "   • Team: http://localhost:5173/team"
echo ""
echo "🔍 To test the API directly:"
echo "   curl http://localhost:5000/api/health"
echo "   curl http://localhost:5000/api/overview"
echo ""
echo "🐍 To activate Python venv manually:"
echo "   source .venv/bin/activate"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
