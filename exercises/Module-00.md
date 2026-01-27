# Module 0: Setup & Environment

## 🎯 Learning Objectives

By the end of this module, you will:
- ✅ Have a working Codespaces environment
- ✅ Understand the project structure and architecture
- ✅ Configure your OpenAI API key
- ✅ Verify DocumentDB connection
- ✅ Understand the dataset you'll be working with

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] GitHub account
- [ ] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- [ ] Codespace created from this repository

---

## Step 1: Configure Workshop Environment

This workshop is designed to run entirely in **GitHub Codespaces**, providing a consistent, pre-configured development environment for all participants.

> 💡 **Why Codespaces?** No local setup required, consistent environment for everyone, and automatic dependency installation.

### Launch Your Codespace

1. **Navigate to the repository**:
   - Go to: `https://github.com/documentdb/booking-agents-sample`

2. **Open in GitHub Codespaces**:
   - Click the green **"Code"** button
   - Select the **"Codespaces"** tab
   - Click **"Create codespace on completed"**
   
   Alternatively, click this badge:
   
   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/documentdb/booking-agents-sample/tree/completed)

3. **Wait for the environment to build** (first launch takes 2-3 minutes):
   - Python 3.11 environment
   - Node.js 20
   - Docker-in-Docker
   - VS Code extensions (DocumentDB, Python, Docker)
   - All dependencies automatically installed

4. **Verify Codespace is ready**:
   - You should see VS Code in your browser
   - Extensions should be installed (check the sidebar)
   - Terminal should be available at the bottom

5. **Open a terminal** (Terminal → New Terminal) and proceed to Activity 2

---

## Step 2: Set Up DocumentDB Container

Now that your environment is ready, let's deploy DocumentDB locally using Docker.

### Deploy DocumentDB Container

1. **Pull the DocumentDB Docker image**:
   ```bash
   docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest
   ```

2. **Tag the image for convenience**:
   ```bash
   docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb
   ```

3. **Run the DocumentDB container**:
   ```bash
   docker run -dt -p 10260:10260 --name documentdb-container documentdb --username admin --password password123
   ```

4. **Verify the container is running**:
   ```bash
   docker ps
   ```
   
   You should see `documentdb-container` running on port 10260.
   
   Expected output:
   ```
   CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                      NAMES
   abc123def456   documentdb   "./entrypoint.sh --u…"   10 seconds ago  Up 9 seconds   0.0.0.0:10260->10260/tcp   documentdb-container
   ```

### Connect to DocumentDB with VS Code Extension

Download the 'DocumentDB for VS Code' extension on your codespace using the VS Code Marketplace. Afterwards, follow these steps to connect your DocumentDB container to the extension:

1. **Open the DocumentDB extension**:
   - Click the DocumentDB icon in the left sidebar (database icon)
   - Or press `Ctrl+Shift+P` and type "DocumentDB"

2. **Add a new connection**:
   - Click the DocumentDB icon in the VS Code sidebar
   - Click "Add New Connection"
   - Select "Connection String"
   - Paste the connection string:
     ```
     mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256
     ```

4. **Verify the connection** - You should see your connection in the DocumentDB explorer

---

## Activity 3: Load Sample Data into DocumentDB

Now that DocumentDB is running and connected, let's load sample data to work with throughout the workshop. You'll use the DocumentDB VS Code extension to import JSON files directly into your database.

### Understanding the Sample Data

The workshop includes a JSON file with sample data that already contains vector embeddings:

- `data/embedded_data.json` - Combined Airbnb listings with pre-generated embeddings

### Load Data Using DocumentDB Extension

1. **Open the DocumentDB extension**:
   - Click the DocumentDB icon in the left sidebar
   - Expand your connection to see databases

2. **Create the database and collections**:
   - Right-click on your connection
   - Select **"Create Database"**
   - Enter database name: `db`
   - Press Enter

3. **Create the customers collection**:
   - Expand the `db` database
   - Right-click on the database
   - Select **"Create Collection"**
   - Enter collection name: `listings`
   - Press Enter

4. **Import customer data**:
   - Right-click on the `listings` collection
   - Select **"Import Documents"**
   - Navigate to: `data/embedded_data.json`
   - Click **"Open"**
   - Wait for the import confirmation message

> 💡 **Note:** This file contains pre-generated vector embeddings, so you can steps 1-5 in Module 1!


---

## 🔑 Step 3: Configure OpenAI API Key

You need an OpenAI API key to generate embeddings and use chat completions.

### Option A: Codespaces Secret (Recommended)

1. Go to [GitHub Settings → Codespaces](https://github.com/settings/codespaces)
2. Click "New secret"
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key (starts with `sk-`)
5. Repository access: Select this repository
6. Click "Add secret"
7. **Rebuild your Codespace** (Codespaces menu → Rebuild Container)

### Option B: Local .env File

1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your key:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. Save the file

### Verify Your API Key

Run this Python snippet to test:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API key configured' if os.getenv('OPENAI_API_KEY') else '❌ API key missing')"
```

---

## ✅ Verification Checklist

Before moving to Module 1, verify:

- [ ] ✅ Codespace is running without errors
- [ ] ✅ OpenAI API key is configured
- [ ] ✅ DocumentDB connection works
- [ ] ✅ You understand the project structure
- [ ] ✅ You've explored the dataset
- [ ] ✅ You understand the architecture

---

## 🎓 Concepts to Remember

### Vector Search
- Converts text to numerical vectors (embeddings)
- Finds similar items by comparing vector distances
- Enables semantic search ("find me something cozy" vs exact keyword match)

### DocumentDB cosmosSearch
- Native vector search operator
- Supports IVF (Inverted File Index) and HNSW algorithms
- Allows combining vector similarity with other filters

### RAG (Retrieval-Augmented Generation)
- Retrieves relevant documents from a database
- Augments LLM prompts with retrieved context
- Generates accurate, grounded responses

### Multi-Agent Systems
- Multiple specialized AI agents working together
- Each agent has a specific role/expertise
- Agents coordinate to solve complex tasks

---

## 🐛 Troubleshooting

### Codespace won't start
- Wait a few minutes (initial build takes 2-3 min)
- Check GitHub status page
- Try rebuilding: Codespaces menu → Rebuild Container

### DocumentDB not connecting
```bash
# Check if DocumentDB container is running
docker ps | grep documentdb

# Check logs
docker logs documentdb
```

### OpenAI API errors
- Verify your API key is correct
- Check you have credits in your OpenAI account
- Make sure the key has permission to use embeddings and chat APIs

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Additional Resources

- [DocumentDB Vector Search Guide](https://github.com/documentdb/documentdb)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [LangChain Quickstart](https://python.langchain.com/docs/get_started/quickstart)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

---

## 🚀 Next Steps

You're all set! Time to build your first vector search implementation.

**Continue to**: [Module 1: Vector Search Fundamentals](Module-01.md)

---

**Questions?** Ask your instructor or check the [troubleshooting guide](Home.md#debugging).
