#!/bin/bash

echo "🚀 Starting local development servers..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping servers..."
    jobs -p | xargs -r kill
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start backend
echo "🐍 Starting backend on http://localhost:5000..."
cd api
python3 index.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are running!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔌 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for background processes
wait
