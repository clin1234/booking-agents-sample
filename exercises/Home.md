# Building AI-Powered Search Applications with DocumentDB and OpenAI

**Create an Intelligent Airbnb Search Platform with Vector Search and Multi-Agent AI**

Welcome to this hands-on workshop where you'll build a production-ready AI-powered search application using DocumentDB's vector search capabilities, OpenAI embeddings, and multi-agent orchestration with LangGraph. Through progressive modules, you'll master semantic search, RAG patterns, and agent-based architectures.

---

## Learning Path

The workshop follows a progressive learning path with the following modules:

- [Module 0: Setup & Environment](Module-00.md)
- [Module 1: Vector Search Fundamentals](Module-01.md)
- [Module 2: RAG Pattern Implementation](Module-02.md)
- [Module 3: Multi-Agent System with LangGraph](Module-03.md)

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
- **React** - Frontend with Azure Maps integration

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

### Module 1: Vector Search Fundamentals
- Generate embeddings with OpenAI
- Create and configure DocumentDB vector indexes (IVF algorithm)
- Implement semantic similarity search
- Combine vector search with filters (location, amenities, price)

### Module 2: RAG Pattern Implementation
- Build custom retrievers with LangChain
- Design context-aware prompts
- Implement conversation memory
- Handle multi-turn dialogues with context

### Module 3: Multi-Agent System
- Create specialized agents with distinct roles
- Use LangGraph for agent orchestration
- Implement agent communication patterns
- Build a coordinated multi-agent workflow

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
- **Module 0**: 5-10 minutes
- **Module 1**: 20-25 minutes
- **Module 2**: 20-25 minutes
- **Module 3**: 20-25 minutes
- **Buffer**: 10 minutes for questions/troubleshooting

### 🎯 Success Criteria
By the end, you should be able to:
- ✅ Search for listings using natural language
- ✅ Get contextually relevant recommendations
- ✅ See results on an interactive map
- ✅ Understand how agents collaborate

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

**Ready to begin?** Start with [Module 0: Setup & Environment](Module-00.md)
