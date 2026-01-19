#!/bin/bash
# Contoso Bookings - Quick Start Script
# Run with: ./scripts/quickstart.sh

set -e

echo "🏨 Contoso Bookings - Quick Start"
echo "=================================="
echo ""

# Check if Docker is running
echo "🐳 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Add your OPENAI_API_KEY to .env file"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check for OPENAI_API_KEY
if grep -q "^OPENAI_API_KEY=$" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: OPENAI_API_KEY is not set in .env"
    echo "   The chat feature won't work without it."
    echo ""
fi

# Build and start services
echo ""
echo "🔨 Building Docker containers..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo ""
if docker-compose ps | grep -q "contoso-documentdb.*Up"; then
    echo "✅ DocumentDB is running"
else
    echo "❌ DocumentDB failed to start"
    docker-compose logs documentdb
    exit 1
fi

if docker-compose ps | grep -q "contoso-backend.*Up"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    docker-compose logs backend
    exit 1
fi

if docker-compose ps | grep -q "contoso-frontend.*Up"; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend is not running (optional)"
fi

# Display success message
echo ""
echo "================================================="
echo "🎉 SUCCESS! Contoso Bookings is now running!"
echo "================================================="
echo ""
echo "📍 Access Points:"
echo "   Frontend:      http://localhost:3000"
echo "   Backend API:   http://localhost:8000/docs"
echo "   DocumentDB:    mongodb://admin:password123@localhost:10260"
echo ""
echo "📚 Next Steps:"
echo "   1. Add your OPENAI_API_KEY to .env (if not done)"
echo "   2. Open contoso-booking.ipynb to load sample data"
echo "   3. Start chatting with the AI assistant!"
echo ""
echo "🛠️  Useful Commands:"
echo "   make logs          - View all logs"
echo "   make logs-backend  - View backend logs"
echo "   make down          - Stop all services"
echo "   make clean         - Remove containers and data"
echo ""
