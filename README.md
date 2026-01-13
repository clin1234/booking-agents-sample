# Real-Time AirBnB Property Search with Location and Text-based Filters

Use a dataset of Airbnb listings with associated descriptions and geospatial metadata (longitude/ latitude). Combine spatial filtering (find properties in a specific area) with semantic search (e.g., "garden", "3 bedrooms") using OpenAI embeddings and DocumentDB.
 
Dataset link: https://insideairbnb.com/get-the-data/

## Prerequisites

- Python 3.8+
- Node.js 16+
- DocumentDB (MongoDB-compatible database)
  - Docker: `docker run -p 27017:27017 mongo:latest` (for local development)
  - Or use DocumentDB from: https://github.com/documentdb/documentdb
- OpenAI API Key from https://platform.openai.com/

## How to run locally

### 1. Set up DocumentDB

For local development, you can use MongoDB in Docker:
```bash
docker run -d -p 27017:27017 --name documentdb mongo:latest
```

Or follow the instructions at https://github.com/documentdb/documentdb to set up DocumentDB.

### 2. Set Environment variables:

Copy the `.env.example` file and rename it to `.env`:
```bash
cp .env.example .env
```

Update the `.env` file with your values:
- `DOCUMENTDB_CONNECTION_STRING`: Your DocumentDB/MongoDB connection string (e.g., `mongodb://localhost:27017`)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_EMBEDDING_MODEL`: (Optional) Default is `text-embedding-3-small`
- `OPENAI_CHAT_MODEL`: (Optional) Default is `gpt-3.5-turbo`
- `REACT_APP_CONTOSO_BOOKINGS_AZURE_MAPS_KEY`: Your Azure Maps API key for the map visualization

### 3. Load the data:

Open and run the `contoso-booking.ipynb` notebook to:
1. Connect to DocumentDB
2. Create necessary indexes (geospatial and amenities)
3. Load the Airbnb listing data
4. Generate OpenAI embeddings for each listing

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

- **Backend**: FastAPI with OpenAI for embeddings and chat
- **Database**: DocumentDB (MongoDB-compatible) with vector similarity search
- **Frontend**: React with Azure Maps integration
- **Search**: Geospatial queries + semantic search using cosine similarity
