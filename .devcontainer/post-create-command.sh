#!/bin/bash
set -e

echo "🚀 Setting up Contoso Bookings development environment..."

# Fix permissions if needed
echo "🔧 Configuring environment..."

# Install MongoDB Shell (mongosh) for DocumentDB extension scrapbooks
echo "📦 Installing MongoDB Shell (mongosh)..."
wget -qO- https://www.mongodb.org/static/pgp/server-7.0.asc | sudo tee /etc/apt/trusted.gpg.d/server-7.0.asc > /dev/null
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq mongodb-mongosh
echo "✅ mongosh installed: $(mongosh --version)"

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
echo "   Setup Complete! 🎉"
echo "✨ ============================================== ✨"
echo ""
echo "📚 Next Steps:"
echo ""
echo "   1. Configure your OPENAI_API_KEY (if not already done)"
echo "   2. Load data using DocumentDB VS Code Extension"
echo "   3. Start the backend: cd src/api && uvicorn main:app --reload --host 0.0.0.0"
echo "   4. Start the frontend: cd src/frontend && npm start"
echo ""
echo "💡 Helpful aliases available (run 'source ~/.bashrc' first):"
echo "   - start-backend  : Start FastAPI backend"
echo "   - start-frontend : Start React frontend"
echo "   - db-connect     : Connect to DocumentDB with mongosh"
echo ""
