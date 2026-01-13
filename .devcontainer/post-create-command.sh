#!/bin/bash
set -e

echo "🚀 Setting up Contoso Bookings development environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd src/frontend
npm install
cd ../..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    
    echo ""
    echo "⚠️  IMPORTANT: Configure your environment variables!"
    echo "   1. Edit .env file and add your OPENAI_API_KEY"
    echo "   2. Or set OPENAI_API_KEY as a Codespaces secret:"
    echo "      https://github.com/settings/codespaces"
    echo ""
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY is not set!"
    echo "   Set it as a Codespaces secret or in your .env file"
else
    echo "✅ OPENAI_API_KEY is configured"
fi

# Wait for DocumentDB to be ready
echo "⏳ Waiting for DocumentDB to be ready..."
max_attempts=30
attempt=0
until mongosh "mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true" --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ DocumentDB failed to start after $max_attempts attempts"
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

echo "✅ DocumentDB is ready!"
echo ""
echo "🎉 Setup complete! Next steps:"
echo "   1. Configure your OPENAI_API_KEY (if not already done)"
echo "   2. Open contoso-booking.ipynb to load data and create indexes"
echo "   3. Start the backend: cd src/api && uvicorn main:app --reload"
echo "   4. Start the frontend: cd src/frontend && npm start"
echo ""
