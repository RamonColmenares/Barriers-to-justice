#!/bin/bash

# Local development setup script
set -e

echo "🔧 Setting up local development environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup Python environment
echo -e "${YELLOW}🐍 Setting up Python environment...${NC}"

# Check if Python 3.11+ is available
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements-lambda.txt

# Setup frontend
echo -e "${YELLOW}🌐 Setting up frontend...${NC}"
cd frontend
npm install
cd ..

echo -e "${GREEN}✅ Local development environment ready!${NC}"
echo ""
echo "To start development:"
echo "1. Backend: source venv/bin/activate && python lambda_handler.py"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "To deploy to AWS: ./deploy-aws.sh"
