# Building AI-Powered Search Applications with DocumentDB and OpenAI

**Create an Intelligent Airbnb Search Platform with Vector Search and Multi-Agent AI**

Welcome to this hands-on workshop where you'll build a production-ready AI-powered search application using DocumentDB's vector search capabilities, OpenAI embeddings, and multi-agent orchestration with LangGraph. Through progressive modules, you'll master semantic search, RAG patterns, and agent-based architectures.

---

## Learning Path

The workshop follows a progressive learning path. Each module builds on the previous one:

### 📚 Module Overview

| Module | Title | Duration | Level | Key Topics |
|--------|-------|----------|-------|------------|
| [**0**](Module-00.md) | Setup & Environment | 5-10 min | Beginner | Environment verification, API keys, project structure |
| [**1**](Module-01.md) | Vector Search Fundamentals | 20-25 min | Intermediate | Embeddings, vector indexes, semantic search |
| [**2**](Module-02.md) | RAG Pattern Implementation | 20-25 min | Intermediate | LangChain, retrievers, conversation memory |
| [**3**](Module-03.md) | Multi-Agent System with LangGraph | 25-30 min | Advanced | Agent orchestration, state management, workflows |

### 🎯 Recommended Path

```
┌─────────────┐
│  Module 0   │ ← Start here: Verify setup
│   Setup     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Module 1   │ ← Learn: Vector search & embeddings
│   Vector    │
│   Search    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Module 2   │ ← Build: RAG conversational AI
│    RAG      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Module 3   │ ← Master: Multi-agent systems
│ Multi-Agent │
└──────┬──────┘
       │
       ▼
   🎉 Complete!
```

---

## What You'll Build

By the end of this workshop, you'll have created:

- **Intelligent Search System** using DocumentDB's native vector search (cosmosSearch)
- **Semantic Search with OpenAI** embeddings for natural language queries
- **RAG (Retrieval-Augmented Generation)** pipeline with context-aware responses
- **Multi-Agent Platform** with specialized agents using LangGraph:
  - Search Agent for finding listings
  - Filter Agent for applying criteria
  - Recommendation Agent for suggesting best options
- **Working Application** with React frontend and FastAPI backend

---

## Technologies Covered

- **DocumentDB** - MongoDB-compatible database with vector search (IVF/HNSW)
- **OpenAI** - Embeddings (text-embedding-3-small) and Chat (GPT-3.5/4)
- **LangChain** - RAG patterns and prompt engineering
- **LangGraph** - Multi-agent orchestration and workflows
- **FastAPI** - Modern Python web framework
- **React** - Frontend with Leaflet/OpenStreetMap integration

---

## Workshop Format

**Duration**: 1-1.5 hours  
**Format**: Hybrid (instructor-led with self-paced elements)  
**Style**: Hands-on coding with guided TODOs

### How It Works

1. **Workshop Branch**: Contains scaffolding with TODOs for you to complete
2. **Completed Branch**: Reference solution for comparison
3. **Progressive Modules**: Each builds on the previous
4. **Challenges**: Simple extensions at the end of each module
5. **Bonus Challenge**: Open-ended enhancement (optional)

---

## Prerequisites

### Technical Skills
- **Programming**: Intermediate Python knowledge
- **Concepts**: Basic understanding of REST APIs and databases
- **Optional**: Familiarity with async/await patterns

### Required Setup
✅ **GitHub Codespaces** (pre-configured, includes DocumentDB)  
✅ **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))  
✅ **Data**: Already included in the `data/` folder

### Pre-installed in Codespaces
- Python 3.11 + dependencies
- Node.js 18 + frontend dependencies
- DocumentDB running on port 10260
- DocumentDB VS Code extension
- All required libraries (FastAPI, LangChain, OpenAI, etc.)

---

## Dataset

The workshop uses real Airbnb listing data from 5 US cities:
- **Colorado** (CO) - Mountain destinations
- **Illinois** (IL) - Urban listings
- **Massachusetts** (MA) - Historic locations
- **Ohio** (OH) - Mixed urban/suburban
- **Texas** (TX) - Diverse markets

Each listing includes:
- Description and neighborhood overview
- Amenities and property details
- Geospatial coordinates
- Pricing and availability
- Host information

**Total Records**: ~35,000 listings  
**Format**: JSON and CSV available

---

## What You'll Learn

### 🔧 Module 0: Setup & Environment (5-10 minutes)

**Objective**: Verify your development environment and understand the project structure

**Topics**:
- ✅ Environment verification (Python, Node.js, DocumentDB)
- ✅ API key configuration (OpenAI)
- ✅ Project structure walkthrough
- ✅ DocumentDB connection testing
- ✅ Dataset overview and exploration

**Deliverable**: Fully configured environment ready for development

---

### 🔍 Module 1: Vector Search Fundamentals (20-25 minutes)

**Objective**: Build semantic search capabilities using vector embeddings

**Topics**:
- 📊 Understanding vector embeddings and similarity
- 🤖 Generate embeddings with OpenAI text-embedding-3-small
- 🗄️ Create DocumentDB vector indexes (IVF algorithm)
- 🔎 Implement semantic search with cosmosSearch operator
- 🎯 Combine vector search with filters (price, location, amenities)
- 📈 Understand similarity scoring and ranking

**Challenges**:
1. Add price range filters (Easy)
2. Implement property type filtering (Easy)
3. Add geospatial radius search (Advanced)
4. Create hybrid scoring (semantic + price) (Advanced)

**Deliverable**: Working semantic search that finds listings based on natural language queries

---

### 💬 Module 2: RAG Pattern Implementation (20-25 minutes)

**Objective**: Build conversational AI with Retrieval-Augmented Generation

**Topics**:
- 🧩 Understanding the RAG pattern
- 🔗 Build custom LangChain retrievers for DocumentDB
- ✍️ Design context-aware prompts with ChatPromptTemplate
- 💭 Implement conversation memory for multi-turn dialogues
- 🔄 Query rephrasing for better retrieval
- 📦 Structure responses for frontend integration

**Challenges**:
1. Add sentiment analysis for tone adjustment (Medium)
2. Extract filters automatically from queries (Hard)
3. Include source citations in responses (Medium)
4. Implement multi-turn clarification (Advanced)

**Deliverable**: Conversational AI that provides context-aware recommendations

---

### 🤖 Module 3: Multi-Agent System with LangGraph (25-30 minutes)

**Objective**: Create a sophisticated multi-agent system with specialized agents

**Topics**:
- 🏗️ Multi-agent architecture design
- 🎭 Build specialized agents (Filter, Search, Recommendation, Supervisor)
- 🔀 Agent orchestration with LangGraph StateGraph
- 📝 Shared state management across agents
- 🧭 Intelligent task routing with conditional workflows
- 🔄 Conversation continuity with MemorySaver
- ⚠️ Error handling and clarification patterns

**Challenges**:
1. Add a Booking Agent for reservations (Medium)
2. Create Price Negotiation Agent for alternatives (Advanced)
3. Build Analytics Agent for market insights (Hard)
4. Implement Multi-Modal Agent with image analysis (Very Advanced)

**Deliverable**: Production-ready multi-agent chat system with coordinated workflows

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│              (Map View + Chat Interface)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│            (REST API + Agent Orchestration)             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌──────────────┐
   │ Search  │  │ Filter  │  │Recommendation│
   │ Agent   │  │ Agent   │  │   Agent      │
   └────┬────┘  └────┬────┘  └──────┬───────┘
        │            │               │
        └────────────┼───────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   DocumentDB                            │
│  • Vector Search (cosmosSearch with IVF)               │
│  • Geospatial Indexes (2dsphere)                       │
│  • Full-text Search                                     │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  OpenAI API                             │
│  • Embeddings (text-embedding-3-small)                 │
│  • Chat Completions (GPT-3.5-turbo)                    │
└─────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Option 1: GitHub Codespaces (Recommended)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/patty-chow/contoso-bookings?quickstart=1)

1. Click the badge above or create a new Codespace
2. Wait for the environment to build (~2-3 minutes)
3. Set your OpenAI API key:
   - **Recommended**: Add as [Codespaces Secret](https://github.com/settings/codespaces)
   - **Or**: Create `.env` file and add `OPENAI_API_KEY=your-key`
4. Switch to the **workshop** branch: `git checkout workshop`
5. Start with [Module 0: Setup & Environment](Module-00.md)

### Option 2: Local Development

See the main [README.md](../README.md) for local setup instructions.

---

## Workshop Tips

### 💡 Best Practices
- Read each module completely before starting
- Test your code frequently
- Use the completed branch as reference (but try on your own first!)
- Ask questions during instructor-led sessions

### 🐛 Debugging
- Check the terminal for error messages
- Use `print()` statements liberally
- Review the DocumentDB extension in VS Code
- Verify your OpenAI API key is set correctly

### ⚡ Time Management

**Total Workshop Time**: 1-1.5 hours

| Activity | Time | Notes |
|----------|------|-------|
| Module 0 (Setup) | 5-10 min | Can be done pre-workshop |
| Module 1 (Vector Search) | 20-25 min | Includes hands-on coding |
| Module 2 (RAG) | 20-25 min | Includes hands-on coding |
| Module 3 (Multi-Agent) | 25-30 min | Advanced concepts |
| Q&A / Troubleshooting | 10-15 min | Throughout workshop |

**Pacing Tips**:
- Complete Module 0 before the workshop starts
- Focus on understanding concepts, not rushing
- Challenges are optional (do them after if time is tight)
- Use the completed branch as reference, not a crutch

### 🎯 Success Criteria

By the end of this workshop, you should be able to:

**Technical Skills**:
- ✅ Generate and use vector embeddings for semantic search
- ✅ Create and query DocumentDB vector indexes
- ✅ Build RAG pipelines with LangChain
- ✅ Design and orchestrate multi-agent systems with LangGraph
- ✅ Manage conversation state and memory

**Practical Abilities**:
- ✅ Search for listings using natural language queries
- ✅ Get contextually relevant, personalized recommendations
- ✅ Handle multi-turn conversations with context awareness
- ✅ Understand how specialized agents collaborate

**Conceptual Understanding**:
- ✅ Know when to use vector search vs traditional search
- ✅ Understand RAG pattern benefits and limitations
- ✅ Design multi-agent architectures for complex workflows
- ✅ Apply these patterns to your own projects

---

## Clean Up

If you're done with the workshop, you can clean up resources:

```bash
# Stop the Codespace (automatically happens after inactivity)
# Or delete it from: https://github.com/codespaces

# For local development:
docker stop documentdb-container
docker rm documentdb-container
docker rmi documentdb
```

---

## Resources

- [DocumentDB Documentation](https://documentdb.io/docs)
- [DocumentDB Vector Search](https://github.com/documentdb/documentdb)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## Support

- **During Workshop**: Ask your instructor
- **Issues**: [GitHub Issues](https://github.com/patty-chow/contoso-bookings/issues)
- **Community**: [DocumentDB Discord](https://discord.gg/vH7bYu524D)

---

## Quick Navigation

### 📖 Start Learning
- **New to the workshop?** → [Module 0: Setup & Environment](Module-00.md)
- **Environment ready?** → [Module 1: Vector Search Fundamentals](Module-01.md)
- **Know vector search?** → [Module 2: RAG Pattern Implementation](Module-02.md)
- **Experienced with RAG?** → [Module 3: Multi-Agent System with LangGraph](Module-03.md)

### 🔗 Quick Links
- [Main README](../README.md) - Project overview
- [Requirements](../requirements.txt) - Python dependencies
- [Devcontainer Config](../.devcontainer/devcontainer.json) - Codespaces setup
- [GitHub Repository](https://github.com/patty-chow/contoso-bookings)

---

**🚀 Ready to begin?** Start with [Module 0: Setup & Environment](Module-00.md)
