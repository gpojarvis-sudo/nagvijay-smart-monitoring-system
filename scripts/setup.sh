#!/bin/bash
set -e

echo "=== NagVijay NSMS Setup ==="

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "Python3 not found - install Python 3.13"
  exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
  echo "Node not found - install Node 20"
  exit 1
fi

echo "Creating .env from .env.example if not exists..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created - please fill values"
else
  echo ".env already exists"
fi

echo "Setting up backend..."
cd backend
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Backend deps installed"
cd ..

echo "Setting up frontend..."
cd frontend
npm install
echo "Frontend deps installed"
cd ..

echo "Setup complete!"
echo "Next steps:"
echo "1. Fill .env"
echo "2. cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "3. cd frontend && npm run dev"
