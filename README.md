# Real-Time AirBnB Property Search with Location and Text-based Filters

Use a dataset of Airbnb listings with associated descriptions and geospatial metadata (longitude/ latitude). Combine spatial filtering (find properties in a specific area) with semantic search (e.g., "garden", "3 bedrooms") using OpenAI embeddings and DocumentDB's native vector search.
 
Dataset link: https://insideairbnb.com/get-the-data/

## Features

- **Vector Search**: DocumentDB's native `cosmosSearch` with IVF (Inverted File Index) for efficient similarity search
- **Geospatial Queries**: Find properties within a radius using MongoDB-compatible 2dsphere indexes
- **Semantic Search**: OpenAI embeddings for natural language understanding
- **Hybrid Search**: Combine vector similarity with filters (amenities, location, price)

## Quick Start

### Option 1: GitHub Codespaces (Recommended)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/patty-chow/contoso-bookings?quickstart=1)

1. Click the badge above or create a new Codespace from this repository
2. **Set your OpenAI API key** (choose one method):
   - **Codespaces Secret** (recommended):
     - Go to [GitHub Settings → Codespaces](https://github.com/settings/codespaces)
     - Add secret: `OPENAI_API_KEY` = `your-key-here`
   - **Or edit `.env` file** in the Codespace
3. Wait for the devcontainer to build (DocumentDB will start automatically)
4. Open `contoso-booking.ipynb` and run cells to load data
5. Start the backend: `cd src/api && uvicorn main:app --reload`
6. Start the frontend: `cd src/frontend && npm start`

The Codespace includes:
- ✅ DocumentDB running on port 10260
- ✅ Python 3.11 + Node.js 18
- ✅ All dependencies pre-installed
- ✅ DocumentDB VS Code extension
- ✅ Ports auto-forwarded (3000, 8000, 10260)

### Option 2: Local Development

## Prerequisites

- Python 3.8+
- Node.js 16+
- Docker (for DocumentDB)
- OpenAI API Key from https://platform.openai.com/

## How to run locally

### 1. Set up DocumentDB

Pull and run the DocumentDB Docker image:

```bash
# Pull the latest DocumentDB image
docker pull ghcr.io/documentdb/documentdb/documentdb-local:latest

# Tag for convenience
docker tag ghcr.io/documentdb/documentdb/documentdb-local:latest documentdb

# Run the container
docker run -dt -p 10260:10260 --name documentdb-container documentdb \
  --username admin --password password123
```

**Note**: Replace `admin` and `password123` with your desired credentials. You must set these when creating the container for authentication to work.

### 2. Set Environment variables:

Copy the `.env.example` file and rename it to `.env`:
```bash
cp .env.example .env
```

Update the `.env` file with your values:
```env
DOCUMENTDB_CONNECTION_STRING=mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-3.5-turbo
REACT_APP_CONTOSO_BOOKINGS_AZURE_MAPS_KEY=your-azure-maps-key
```

### 3. Load the data:

Open and run the `contoso-booking.ipynb` notebook to:
1. Connect to DocumentDB
2. Create vector search index using `cosmosSearch` (IVF algorithm)
3. Create geospatial and amenity indexes
4. Load the Airbnb listing data
5. Generate OpenAI embeddings for each listing

The notebook will create:
- **Vector Index**: `vector-ivf` with cosine similarity for semantic search
- **Geospatial Index**: `2dsphere` for location-based queries
- **Amenity Index**: For fast filtering by amenities

### 4. Install dependencies:

```bash
cd src/api && pip install -r ../../requirements.txt
cd ../frontend && npm install
```

### 5. Run the app:

Terminal 1 (Backend):
```bash 
cd src/api && uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
cd src/frontend && npm run start
```

The application will be available at `http://localhost:3000`

## Architecture

- **Backend**: FastAPI with OpenAI for embeddings and chat completions
- **Database**: DocumentDB with native vector search support
  - **Vector Search**: `cosmosSearch` operator with IVF indexing
  - **Geospatial**: MongoDB 2dsphere indexes
  - **Filters**: Compound queries combining vector similarity, location, and amenities
- **Frontend**: React with Azure Maps integration
- **Search Flow**:
  1. User query → OpenAI embedding generation
  2. DocumentDB `cosmosSearch` finds similar listings
  3. Filters applied (location radius, amenities)
  4. Results ranked by similarity score

## DocumentDB Vector Search

DocumentDB supports MongoDB-compatible vector search through the `cosmosSearch` operator:

- **Index Types**: 
  - `vector-ivf`: Inverted File Index (used in this project)
  - `vector-hnsw`: Hierarchical Navigable Small World
- **Similarity Metrics**: Cosine (COS), L2 distance, Inner Product (IP)
- **Dimensions**: Supports up to 2000+ dimensions
- **Performance**: Optimized for large-scale vector similarity search
