#!/bin/bash

echo "🚀 Setting up local development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "📦 Installing backend dependencies..."
cd api
pip3 install -r requirements.txt
cd ..

echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "🚀 To run locally:"
echo "  Backend:  cd api && python3 index.py"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:5000"
