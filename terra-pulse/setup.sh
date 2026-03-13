#!/bin/bash
set -e

echo "Setting up Terra Pulse..."

# Backend
echo "Installing backend dependencies..."
cd backend
pip install uv
uv venv .venv
source .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null
uv pip install -e .
cd ..

# Frontend
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Download GeoJSON
echo "Downloading GeoJSON..."
cd frontend/public
curl -fsSL "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson" -o ne_110m_countries.json
echo "GeoJSON downloaded"
cd ../..

# Copy env file
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env -- add your WORLDNEWS_API_KEY"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start with Docker:"
echo "  docker compose up --build"
echo ""
echo "To start locally:"
echo "  cd backend && uvicorn app.main:app --reload"
echo "  cd frontend && npm run dev"
