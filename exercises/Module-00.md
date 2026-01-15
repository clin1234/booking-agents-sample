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

## 🚀 Step 1: Verify Your Codespace

Your Codespace should have automatically:
1. ✅ Built the dev container (Python 3.11 + Node.js 18)
2. ✅ Installed Python dependencies (`requirements.txt`)
3. ✅ Installed Node.js dependencies (`src/frontend/package.json`)
4. ✅ Started DocumentDB on port 10260
5. ✅ Installed VS Code extensions (Python, Jupyter, DocumentDB)

### Check the Setup Log

Look for this message in your terminal:
```
✅ DocumentDB is ready!

🎉 Setup complete! Next steps:
   1. Configure your OPENAI_API_KEY (if not already done)
   2. Open contoso-booking.ipynb to load data and create indexes
   3. Start the backend: cd src/api && uvicorn main:app --reload
   4. Start the frontend: cd src/frontend && npm start
```

If you see errors, ask your instructor for help.

---

## 🔑 Step 2: Configure OpenAI API Key

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

## 📁 Step 3: Understand the Project Structure

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
│       │   └── Map.tsx          # Azure Maps integration
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

## 🗄️ Step 4: Verify DocumentDB Connection

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

## 📊 Step 5: Explore the Dataset

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

## 🏗️ Step 6: Architecture Overview

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

## ✅ Step 7: Verification Checklist

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
