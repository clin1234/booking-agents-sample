# Module 0: Setup & Environment

**Duration**: 5-10 minutes  
**Objective**: Verify your development environment and get familiar with the project structure

---

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
- [ ] Switched to the `workshop` branch

---

## Step 1: Configure Workshop Environment

This workshop is designed to run entirely in **GitHub Codespaces**, providing a consistent, pre-configured development environment for all participants.

> 💡 **Why Codespaces?** No local setup required, consistent environment for everyone, and automatic dependency installation.

### Prerequisites

- **GitHub account** - [Sign up for free](https://github.com/signup) if you don't have one
- **Web browser** - Chrome, Firefox, Safari, or Edge (latest version recommended)

That's it! Everything else is handled by Codespaces.

### Launch Your Codespace

1. **Navigate to the repository**:
   - Go to: `https://github.com/documentdb/booking-agents-sample`

2. **Open in GitHub Codespaces**:
   - Click the green **"Code"** button
   - Select the **"Codespaces"** tab
   - Click **"Create codespace on workshop"**
   
   Alternatively, click this badge:
   
   [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/documentdb/fast-api-sample/tree/workshop)

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

The workshop includes a JSON file with sample data:

- `data/json/combined_listings.json` - Combined Airbnb listings from multiple states

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
   - Navigate to: `data/json/combined_listings.json`
   - Click **"Open"**
   - Wait for the import confirmation message

### Verify the Data

1. **View the imported data**:
   - Expand the collection
   - Click on a collection to view documents
   - You should see the imported documents listed

2. **Explore a document**:
   - Click on any document to view its contents
   - Notice the structure matches the Beanie models
   - Each document has an automatically generated `_id` field

3. **Check document counts**:
   - Right-click on each collection
   - Select **"View Collection Statistics"** (if available)
   - Or simply count the visible documents


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

## 📁 Step 4: Understand the Project Structure

Let's explore the codebase:

```
contoso-bookings/
├── .devcontainer/               # Codespaces configuration
│   ├── devcontainer.json        # Container settings
│   ├── docker-compose.yml       # DocumentDB service
│   └── post-create-command.sh   # Setup script
├── data/                        # Airbnb listing datasets
│   ├── csv/                     # Raw CSV files by state
│   ├── datasets without embeddings/  # JSON datasets
│   └── json/                    # Processed data
├── exercises/                   # Workshop modules (you are here!)
│   ├── Home.md                  # Workshop introduction
│   └── Module-00.md             # This file
├── src/
│   ├── api/                     # FastAPI backend
│   │   ├── main.py              # API endpoints
│   │   ├── chat.py              # RAG implementation
│   │   ├── cosmosdb.py          # Database operations
│   │   └── geolocation.py       # Location services
│   └── frontend/                # React application
│       ├── src/
│       │   ├── App.tsx          # Main app component
│       │   ├── Chat.tsx         # Chat interface
│       │   └── Map.tsx          # Leaflet map integration
│       └── package.json
├── contoso-booking.ipynb        # Jupyter notebook for data setup
├── contoso_booking.py           # Standalone script version
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

### Key Files You'll Modify

During the workshop, you'll work primarily with:
- **Module 1**: `contoso_booking.py` - Data loading and vector search
- **Module 2**: `src/api/chat.py` - RAG implementation
- **Module 3**: Create new files for multi-agent system

---

## 🗄️ Step 5: Verify DocumentDB Connection

DocumentDB is running in a separate container. Let's verify the connection.

### Test Connection with mongosh

```bash
mongosh "mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true" --eval "db.adminCommand('ping')"
```

You should see:
```json
{ "ok": 1 }
```

### Test with Python

Create a test file or run in terminal:

```python
from pymongo import MongoClient

client = MongoClient('mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true')
print(f"Connected! Databases: {client.list_database_names()}")
```

### Use the DocumentDB Extension

1. Open VS Code Extensions sidebar (Ctrl+Shift+X)
2. Find "DocumentDB" extension (should be pre-installed)
3. Click the DocumentDB icon in the activity bar
4. Add connection: `mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true`
5. Browse databases and collections

---

## 📊 Step 6: Explore the Dataset

Let's look at the data you'll be working with.

### Dataset Overview

The `data/` folder contains Airbnb listings from 5 US states:

| State | City Focus | Records |
|-------|-----------|---------|
| CO | Denver, Boulder (Mountain) | ~7,000 |
| IL | Chicago (Urban) | ~7,000 |
| MA | Boston (Historic) | ~7,000 |
| OH | Cleveland, Columbus (Mixed) | ~7,000 |
| TX | Austin, Dallas, Houston (Diverse) | ~7,000 |

**Total**: ~35,000 listings

### Sample Record Structure

Open `data/datasets without embeddings/small_for_testing.json` to see a sample:

```json
{
  "_id": "123456",
  "name": "Cozy Mountain Cabin near Downtown",
  "description": "Peaceful retreat with mountain views...",
  "neighborhood_overview": "Quiet area close to hiking trails...",
  "location": {
    "type": "Point",
    "coordinates": [-105.0021, 39.7664]  // [longitude, latitude]
  },
  "amenities": ["WiFi", "Hot tub", "Kitchen", "Fireplace"],
  "price": 150,
  "beds": 2,
  "bedrooms": 1,
  "bathrooms": 1,
  "property_type": "Entire cabin",
  "room_type": "Entire home/apt",
  "host_about": "Outdoor enthusiast and local guide..."
}
```

### Data Files

- **small_for_testing.json**: 100 records for quick testing
- **large_35K.json**: Full dataset (35K records)
- **CSV files**: Original raw data by state

---

## 🏗️ Step 7: Architecture Overview

Here's how the components work together:

```
User Query: "Find a quiet cabin with a hot tub near Denver"
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Frontend (React)                                   │
│  • Chat interface captures query                   │
│  • Map displays results                            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP POST /query_message
                       ▼
┌─────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                  │
│  • Receives query and user location               │
│  • Coordinates agent workflow                      │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌──────────────┐
   │ Search  │   │ Filter  │   │Recommendation│
   │ Agent   │   │ Agent   │   │   Agent      │
   └────┬────┘   └────┬────┘   └──────┬───────┘
        │ 1. Generate │ 2. Apply │ 3. Rank &
        │ embedding   │ filters  │ recommend
        └─────────────┼──────────┴───────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│  DocumentDB                                         │
│  • Vector search (cosmosSearch) finds similar items│
│  • Geospatial filter (within radius)               │
│  • Amenity filter (has hot tub)                    │
└──────────────────────┬──────────────────────────────┘
                       │ Returns top 5 matches
                       ▼
┌─────────────────────────────────────────────────────┐
│  OpenAI API                                         │
│  • Creates embeddings for semantic search          │
│  • Generates natural language responses            │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Step 8: Verification Checklist

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
