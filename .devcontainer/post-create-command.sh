#!/bin/bash
set -e

echo "🚀 Setting up Contoso Bookings development environment..."

# Fix permissions if needed
echo "🔧 Configuring environment..."

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

# If OPENAI_API_KEY is set as environment variable, update .env file
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY is configured (from environment)"
    # Update .env file with the secret
    sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
else
    echo "⚠️  WARNING: OPENAI_API_KEY is not set!"
    echo "   Set it as a Codespaces secret or in your .env file"
fi

# Wait for DocumentDB to be ready (started via docker run)
echo "🐳 Starting DocumentDB container..."
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest || echo "⚠️  Image pull failed, may already exist"
docker rm -f documentdb-container 2>/dev/null || true
docker run -dt -p 10260:10260 --name documentdb-container \
    ghcr.io/documentdb/documentdb/documentdb-local:latest \
    --username admin --password password123

echo "⏳ Waiting for DocumentDB to be ready..."
max_attempts=30
attempt=0
until docker exec documentdb-container mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ DocumentDB failed to start after $max_attempts attempts"
        echo "   You can start it manually later with:"
        echo "   docker run -dt -p 10260:10260 --name documentdb-container ghcr.io/documentdb/documentdb/documentdb-local:latest --username admin --password password123"
        break
    fi
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -lt $max_attempts ]; then
    echo "✅ DocumentDB is ready!"
fi

# Create helpful aliases
echo "📝 Creating helpful bash aliases..."
cat >> ~/.bashrc << 'EOF'

# Contoso Bookings aliases
alias workspace='cd /workspaces/contoso-bookings'
alias start-backend='cd /workspaces/contoso-bookings/src/api && uvicorn main:app --reload --host 0.0.0.0'
alias start-frontend='cd /workspaces/contoso-bookings/src/frontend && npm start'
alias start-all='start-backend & start-frontend'
alias db-connect='docker exec -it documentdb-container mongosh'
alias db-start='docker start documentdb-container || docker run -dt -p 10260:10260 --name documentdb-container ghcr.io/documentdb/documentdb/documentdb-local:latest --username admin --password password123'
alias db-stop='docker stop documentdb-container'

EOF

echo ""
echo "✨ ============================================== ✨"
echo "   Contoso Bookings Setup Complete! 🎉"
echo "✨ ============================================== ✨"
echo ""
echo "📚 Next Steps:"
echo ""
echo "   1. Configure your OPENAI_API_KEY (if not already done)"
echo "   2. Open contoso-booking.ipynb to load data and create indexes"
echo "   3. Start the backend: cd src/api && uvicorn main:app --reload --host 0.0.0.0"
echo "   4. Start the frontend: cd src/frontend && npm start"
echo ""
echo "💡 Helpful aliases available (run 'source ~/.bashrc' first):"
echo "   - start-backend  : Start FastAPI backend"
echo "   - start-frontend : Start React frontend"
echo "   - db-connect     : Connect to DocumentDB with mongosh"
echo ""
