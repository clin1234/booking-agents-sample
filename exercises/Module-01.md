# Module 1: Vector Search Fundamentals

### 📓 Jupyter Notebooks:
- **[generate-embeddings.ipynb](../notebooks/generate-embeddings.ipynb)** - Learn how embeddings work (Steps 1-5, optional)
- **[vector-search.ipynb](../notebooks/vector-search.ipynb)** - Implement vector search (Steps 6+, start here if short on time)

## 📋 Learning Objectives

By the end of this module, you will:
- Understand what vector embeddings are and how they enable semantic search
- Load and prepare data for vector search
- Generate embeddings using OpenAI's text-embedding model
- Create vector search indexes in DocumentDB
- Implement semantic search with similarity scoring
- Apply filters to refine search results

## 🎯 What You'll Build

You'll implement a semantic search system that allows users to search for Airbnb listings using natural language. Instead of exact keyword matching, your search will understand the meaning and context of queries.

### Examples of Semantic Search:
- "cozy place near downtown with parking" → finds listings matching the vibe, not just keywords
- "family-friendly home with backyard" → understands intent and returns relevant results
- "quiet retreat for remote work" → captures context and lifestyle needs

## 📚 Concept: Vector Embeddings

**What are embeddings?**
- Numerical representations of text that capture semantic meaning
- Each embedding is a list of numbers (vector) - typically 1536 dimensions for OpenAI's text-embedding-3-small
- Similar concepts have similar vectors, even if they use different words

**Example:**
```
"beach house" → [0.23, -0.45, 0.12, ..., 0.67]  (1536 numbers)
"oceanfront property" → [0.21, -0.43, 0.15, ..., 0.69]  (similar vector!)
"mountain cabin" → [-0.45, 0.67, -0.23, ..., 0.12]  (different vector)
```

**How Vector Search Works:**
1. Convert text (listings, queries) into embeddings
2. Store embeddings in a database with vector search capabilities
3. When searching, convert the query to an embedding
4. Find the most similar vectors using cosine similarity or other distance metrics
5. Return the corresponding listings

## 🏗️ Architecture for This Module

```
┌─────────────────────────────────────────────────────────────────┐
│                         Module 1 Flow                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Load Data          2. Generate         3. Store & Index    │
│  ┌─────────┐           ┌──────────┐        ┌────────────────┐  │
│  │ JSON    │           │ OpenAI   │        │  DocumentDB    │  │
│  │ File    │─────────▶│ Embedding│───────▶│  + Vector      │  │
│  │         │           │ API      │        │    Index       │  │
│  │         │           │(1536-dim)│        │  (cosmosSearch)│  │
│  └─────────┘           └──────────┘        └────────────────┘  │
│                                                     │           │
│                                                     │           │
│  4. Search Query                                    ▼           │
│  ┌─────────────┐          ┌──────────┐     ┌────────────────┐ │
│  │ "cozy place"│─────────▶│ Convert  │────▶│ Vector Search  │ │
│  │ "near beach"│          │ to Vector│     │ (cosmosSearch) │ │
│  └─────────────┘          └──────────┘     └────────────────┘ │
│                                                     │           │
│                                                     ▼           │
│                                            ┌────────────────┐  │
│                                            │ Top Similar    │  │
│                                            │ Listings       │  │
│                                            └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Steps 1-5: Understanding Embeddings (Demonstration)

> **⏭️ Skip Ahead?** Steps 1-5 are a **learning demonstration** to help you understand how embeddings work. They do **not** modify the application or database. If you're short on time, you can **[skip to Step 6](#step-6-create-vector-index-using-the-documentdb-for-vs-code-extension)** to start working with the pre-embedded data.

---

> **📍 Note:** Steps 1-5 are **optional** and require an OpenAI API key to run, since they call the OpenAI Embedding API to generate vectors. If you don't have an API key, don't worry — the pre-embedded data in `data/embedded_data.json` already contains all the vectors you need. You can read through Steps 1-5 to understand the concepts, then **[skip to Step 6](#step-6-create-vector-index-using-the-documentdb-for-vs-code-extension)** to start building with the pre-embedded data.


## 🛠️ Step 1: Understanding the Data

Let's first explore the dataset structure in the **[Jupyter Notebook](../notebooks/generate-embeddings.ipynb)**.

### Dataset Overview

Our dataset contains Airbnb listings with the following key fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | number | Unique identifier | `360` |
| `listing_url` | string | URL to the listing | `"https://www.airbnb.com/rooms/360"` |
| `name` | string | Property title | `"Chickadee Cottage in LoHi"` |
| `description` | string | Full description | Text used for embeddings |
| `neighborhood_overview` | string | Area information | `"Located in Lower Highlands..."` |
| `amenities` | array | List of amenities | `["Wifi", "Kitchen", "TV", ...]` |
| `property_type` | string | Type of property | `"Entire guesthouse"`, `"Apartment"`, etc. |
| `room_type` | string | Room configuration | `"Entire home/apt"` |
| `bedrooms` | number | Number of bedrooms | `1`, `2`, `3`, etc. |
| `beds` | number | Number of beds | `1`, `2`, `3`, etc. |
| `price` | number | Nightly price | `161.0` |
| `latitude` | number | Latitude coordinate | `39.766414` |
| `longitude` | number | Longitude coordinate | `-105.002098` |

**💡 Key Insight:** The `description` field is what we'll convert into vector embeddings for semantic search.

### Pre-embedded Data

For this workshop, we provide **pre-embedded data** in `data/embedded_data.json` that already contains the `descriptionVector` field. This saves time and API costs during the workshop.

Understanding how embeddings are generated is essential! The next steps demonstrate embedding 50 sample documents **in the notebook** as a learning exercise.

## 🛠️ Step 2: Load and Examine Sample Data

Run the cells in **[generate-embeddings.ipynb](../notebooks/generate-embeddings.ipynb)** to load and explore the raw data:

```python
# Load raw data (without embeddings)
with open('../data/raw_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📊 Loaded {len(data)} listings from raw_data.json")

# Examine the first listing
sample = data[0]
print(f"\n📄 Sample Listing:")
print(f"   ID: {sample['id']}")
print(f"   Name: {sample['name']}")
print(f"   Property Type: {sample['property_type']}")
print(f"   Bedrooms: {sample.get('bedrooms', 'N/A')}")
print(f"   Price: ${sample.get('price', 'N/A')}")
print(f"   Amenities: {', '.join(sample.get('amenities', [])[:5])}...")
print(f"\n📝 Description Preview:")
print(f"   {sample.get('description', '')[:200]}...")
```

## 🛠️ Step 3: Create Embedding Generation Function

We'll use OpenAI's `text-embedding-3-small` model to generate 1536-dimension vectors that capture semantic meaning.

### 💡 Understanding the Embedding

Each number in the 1536-dimension vector represents a learned feature. The model has discovered that certain combinations of these numbers correspond to semantic concepts like "cozy", "parking", "downtown", etc.

The notebook contains the `generate_embedding()` function:

```python
def generate_embedding(text):
    """
    Generate a vector embedding for the given text using OpenAI.
    
    Args:
        text (str): The text to embed
        
    Returns:
        list: A 1536-dimension vector representing the text
    """
    if not text or not isinstance(text, str):
        return None
    
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


# Test the function with a sample query
test_text = "Cozy apartment near downtown with free parking"
test_embedding = generate_embedding(test_text)

print(f"\n🧪 Testing Embedding Generation:")
print(f"   Input: '{test_text}'")
print(f"   ✅ Generated embedding")
print(f"   📏 Dimensions: {len(test_embedding)}")
print(f"   📊 First 5 values: {test_embedding[:5]}")
```

## 🛠️ Step 4: Generate Embeddings for 50 Documents

Now let's embed 50 documents from `raw_data.json` to understand the full process. **Note:** This is a learning exercise - we won't write to the database since pre-embedded data is already available.

The notebook contains the `embed_documents()` function:

```python
def embed_documents(documents, limit=50):
    """
    Generate embeddings for a list of documents.
    
    Args:
        documents (list): List of listing documents
        limit (int): Maximum number of documents to process
        
    Returns:
        list: Documents with descriptionVector added
    """
    docs_to_process = documents[:limit]
    embedded_docs = []
    
    print(f"\n🔄 Generating embeddings for {len(docs_to_process)} documents...")
    
    for idx, doc in enumerate(docs_to_process):
        description = doc.get('description', '')
        embedding = generate_embedding(description)
        
        if embedding:
            doc_copy = doc.copy()
            doc_copy['descriptionVector'] = embedding
            embedded_docs.append(doc_copy)
        
        # Progress update every 10 documents
        if (idx + 1) % 10 == 0:
            print(f"   ✅ Processed {idx + 1}/{len(docs_to_process)} documents...")
    
    print(f"\n✅ Generated embeddings for {len(embedded_docs)} documents")
    return embedded_docs


# Run the embedding process
embedded_documents = embed_documents(data, limit=50)

# Show results
print(f"\n📊 Results Summary:")
print(f"   Documents processed: {len(embedded_documents)}")
print(f"   Embedding dimensions: {len(embedded_documents[0]['descriptionVector'])}")

# Show a sample embedded document
sample_embedded = embedded_documents[0]
print(f"\n📄 Sample Embedded Document:")
print(f"   Name: {sample_embedded['name']}")
print(f"   Has embedding: {'descriptionVector' in sample_embedded}")
print(f"   Vector preview: {sample_embedded['descriptionVector'][:3]}...")
```

## 🛠️ Step 5: Verify Results

Run the embedding cells in the notebook and verify the output:

**Expected Output:**
```
✅ Libraries imported and environment loaded
📊 Loaded 1000 listings from raw_data.json

📄 Sample Listing:
   ID: 360
   Name: Sit in the Peaceful Garden of the Chickadee Cottage in LoHi
   ...

🔄 Generating embeddings for 50 documents...
   ✅ Processed 10/50 documents...
   ✅ Processed 20/50 documents...
   ...
✅ Generated embeddings for 50 documents

📊 Results Summary:
   Documents processed: 50
   Embedding dimensions: 1536
```

**💡 Note:** The full dataset is already embedded in `data/embedded_data.json`. This exercise demonstrates the embedding process without the cost of re-embedding all 1,000 listings.

---

## 🛠️ Step 6: Create Vector Index Using the DocumentDB for VS Code Extension

> **📍 Start Here** if you skipped the embedding demonstration (Steps 1-5).

Now that your data with embeddings is loaded in DocumentDB, you need to create a **vector search index** to enable fast similarity searches.

### Instructions:

1. **Open the DocumentDB Extension** in VS Code (click the database icon in the sidebar)

2. **Navigate to your Scrapbook**:
   - Right-click on your collection `listings`
   - Select **"New Scrapbook"**

3. **Run the following commands** in your scrapbook (select each block and press `Ctrl+Enter` or click "Run"):

```javascript
// Create vector search index on the descriptionVector field
db.runCommand({
    createIndexes: "listings",
    indexes: [{
        key: { "descriptionVector": "cosmosSearch" },
        name: "vectorSearchIndex",
        cosmosSearchOptions: {
            kind: "vector-ivf",
            numLists: 100,
            similarity: "COS",
            dimensions: 1536
        }
    }]
})

// Check all indexes on the collection
db.listings.getIndexes()
```

**Expected Output:**
```json
[
  { "name": "_id_", "key": { "_id": 1 } },
  { "name": "vectorSearchIndex", "key": { "descriptionVector": "cosmosSearch" } },
]
```

### 💡 Understanding Index Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `kind` | `"vector-ivf"` | Uses Inverted File Index for fast approximate search |
| `numLists` | `100` | Number of clusters (higher = more accurate but slower) |
| `similarity` | `"COS"` | Cosine similarity (range: 0 to 1, where 1 = identical) |
| `dimensions` | `1536` | Must match your embedding size (OpenAI text-embedding-3-small) |

DocumentDB supports native vector search with two index types:

1. **IVF (Inverted File Index)**: Fast, approximate search suitable for large datasets
2. **HNSW (Hierarchical Navigable Small World)**: More accurate but uses more memory

For this workshop, we'll use **IVF** for better performance with our dataset.

## 🛠️ Step 7: Implement Semantic Search

📓 **Follow along in [vector-search.ipynb](../notebooks/vector-search.ipynb)** - Step 4

### Basic Vector Search

```python
def search_listings(query, limit=5):
    """
    Search for listings using semantic similarity.
    
    Args:
        query (str): Natural language search query
        limit (int): Maximum number of results to return
        
    Returns:
        list: Matching listings with similarity scores
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query)
    
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return []
    
    # Perform vector search using cosmosSearch
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "descriptionVector",
                    "k": limit  # Number of nearest neighbors
                },
                "returnStoredSource": True
            }
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "property_type": 1,
                "bedrooms": 1,
                "beds": 1,
                "price": 1,
                "neighborhood_overview": 1,
                "amenities": 1,
                "searchScore": {"$meta": "searchScore"}
            }
        }
    ]
    
    results = list(collection.aggregate(pipeline))
    return results

# Test the search
query = "cozy apartment with parking near downtown"
results = search_listings(query, limit=5)

print(f"\n🔍 Search Query: '{query}'")
print(f"📊 Found {len(results)} results\n")

for idx, result in enumerate(results, 1):
    print(f"{idx}. {result['name']}")
    print(f"   Property Type: {result.get('property_type', 'N/A')}")
    print(f"   Neighborhood: {result.get('neighborhood_overview', 'N/A')[:80]}")
    print(f"   Bedrooms: {result.get('bedrooms', 'N/A')} | Price: ${result.get('price', 'N/A')}")
    print(f"   Similarity Score: {result.get('searchScore', 0):.4f}")
    print(f"   Preview: {result.get('description', '')[:100]}...")
    print()
```

**Expected Output:**
```
🔍 Search Query: 'cozy apartment with parking near downtown'
📊 Found 5 results

1. Downtown Studio with Parking
   Property Type: Apartment
   Neighborhood: Located in a vibrant area near downtown Denver...
   Bedrooms: 1 | Price: $95.0
   Similarity Score: 0.8523
   Preview: Cozy studio apartment in the heart of downtown. Free parking included. Walking distance to...

2. City Center Apartment
   Property Type: Apartment
   Neighborhood: This quiet neighborhood is close to restaurants, shops, and parks...
   Bedrooms: 1 | Price: $120.0
   Similarity Score: 0.8201
   Preview: Modern apartment with dedicated parking spot. Located near downtown shopping and dining...
```

### 💡 Understanding Search Scores

- Scores range from 0 to 1 (with cosine similarity)
- Higher scores = more similar to the query
- Scores above 0.75 typically indicate strong semantic relevance
- Scores between 0.5-0.75 are moderately relevant
- Scores below 0.5 may be weak matches

## 🛠️ Step 8: Add Filters to Refine Search

📓 **Follow along in [vector-search.ipynb](../notebooks/vector-search.ipynb)** - Step 5

### Search with Filters

```python
def search_listings_with_filters(query, filters=None, limit=5):
    """
    Search for listings with semantic similarity and additional filters.
    
    Args:
        query (str): Natural language search query
        filters (dict): Optional filters (bedrooms, price_max, neighborhood, amenities)
        limit (int): Maximum number of results to return
        
    Returns:
        list: Matching listings with similarity scores
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query)
    
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return []
    
    # Build match stage for filters
    match_conditions = {}
    
    if filters:
        if 'bedrooms' in filters:
            match_conditions['bedrooms'] = {"$gte": filters['bedrooms']}
        
        if 'price_max' in filters:
            match_conditions['price'] = {"$lte": filters['price_max']}
        
        if 'neighborhood' in filters:
            match_conditions['neighborhood_overview'] = {
                "$regex": filters['neighborhood'],
                "$options": "i"
            }
        
        if 'amenities' in filters:
            # Amenities is a list, so we check if all required amenities are present
            match_conditions['amenities'] = {"$all": filters['amenities']}
    
    # Build aggregation pipeline
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "descriptionVector",
                    "k": limit * 10  # Fetch more to account for filtering
                },
                "returnStoredSource": True
            }
        }
    ]
    
    # Add filter stage if we have conditions
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Add projection and limit
    pipeline.extend([
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "property_type": 1,
                "bedrooms": 1,
                "beds": 1,
                "price": 1,
                "neighborhood_overview": 1,
                "amenities": 1,
                "searchScore": {"$meta": "searchScore"}
            }
        },
        {"$limit": limit}
    ])
    
    results = list(collection.aggregate(pipeline))
    return results

# Test with filters
query = "family-friendly home with outdoor space"
filters = {
    "bedrooms": 3,
    "price_max": 200,
    "amenities": ["Wifi", "Kitchen"]
}

results = search_listings_with_filters(query, filters, limit=5)

print(f"\n🔍 Search Query: '{query}'")
print(f"🎯 Filters:")
print(f"   - Bedrooms: {filters['bedrooms']}+")
print(f"   - Max Price: ${filters['price_max']}")
print(f"   - Amenities: {', '.join(filters['amenities'])}")
print(f"\n📊 Found {len(results)} results\n")

for idx, result in enumerate(results, 1):
    print(f"{idx}. {result['name']}")
    print(f"   Property Type: {result.get('property_type', 'N/A')}")
    print(f"   Neighborhood: {result.get('neighborhood_overview', 'N/A')[:80]}")
    print(f"   Bedrooms: {result.get('bedrooms', 'N/A')} | Price: ${result.get('price', 'N/A')}")
    print(f"   Similarity Score: {result.get('searchScore', 0):.4f}")
    amenities_preview = ', '.join(result.get('amenities', [])[:5])
    print(f"   Amenities: {amenities_preview}...")
    print()
```

## 🛠️ Step 9: Experiment with Different Queries

📓 **Follow along in [vector-search.ipynb](../notebooks/vector-search.ipynb)** - Step 6

Try these queries to see how semantic search works:

```python
# Test various semantic queries
test_queries = [
    "romantic getaway for couples",
    "pet-friendly place near parks",
    "business travel with home office",
    "beachfront property for surfing",
    "quiet retreat for meditation and yoga"
]

print("🧪 Testing Semantic Search Capabilities\n")
print("=" * 80)

for query in test_queries:
    results = search_listings(query, limit=3)
    
    print(f"\n🔍 Query: '{query}'")
    print(f"📊 Top 3 Results:")
    
    for idx, result in enumerate(results, 1):
        print(f"\n   {idx}. {result['name']}")
        print(f"      Score: {result.get('searchScore', 0):.4f}")
        print(f"      {result.get('property_type', 'N/A')} | "
              f"{result.get('bedrooms', 'N/A')} bed | "
              f"${result.get('price', 'N/A')}/night")
    
    print("\n" + "-" * 80)
```

**💡 Observations:**
- Notice how the search understands context (e.g., "romantic getaway" finds properties with ambiance descriptions)
- "Pet-friendly" matches listings that mention pets, animals, or outdoor areas
- "Business travel" finds properties with workspaces, desks, and good wifi
- The semantic understanding goes beyond exact keyword matching

## Step 10: Launch Frontend and Backend

Now let's start the application to see it in action!

### Launch the Backend (Terminal 1)

The backend is a FastAPI application that provides the search and chat APIs.

```bash
pip install -r src/api/requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
✅ Connected to DocumentDB: db.listings
```

> 💡 **Tip:** In Codespaces, click the "Open in Browser" button when prompted, or go to the Ports tab and click the globe icon for port 8000 to access the API docs at `/docs`.

### Launch the Frontend (Terminal 2)

Open a **new terminal** (Terminal → New Terminal) and run:

```bash
cd src/frontend
npm install
npm start
```

You should see:
```
Compiled successfully!
You can now view the app in the browser.
  Local:            http://localhost:3000
```

> 💡 **Tip:** In Codespaces, click the "Open in Browser" button when prompted for port 3000 to view the application.

### Verify Everything Works

1. **Check the Backend Health**:
   - Open: `http://localhost:8000/health` (or the Codespaces URL)
   - You should see a JSON response with `"status": "ok"` or `"status": "degraded"`

2. **Check the Frontend**:
   - Open: `http://localhost:3000` (or the Codespaces URL)
   - You should see the booking search interface with a map

3. **Test the Connection**:
   - The frontend header shows a connection indicator
   - Green = connected to backend
   - Yellow = demo mode (backend not connected yet)

## 🎓 What You've Learned

✅ **Vector Embeddings**: How to convert text into numerical representations  
✅ **OpenAI Embeddings API**: Using text-embedding-3-small for semantic encoding  
✅ **DocumentDB Vector Indexes**: Creating IVF indexes for efficient similarity search  
✅ **Semantic Search**: Implementing cosine similarity search with cosmosSearch  
✅ **Search Filters**: Combining vector search with traditional filters  
✅ **Query Understanding**: How embeddings capture meaning and context  

## 🚀 Challenge: Enhance the Search Function

Now it's your turn! Enhance the `search_listings_with_filters` function with these features:

### Challenge 1: Price Range Filter (Easy)
Instead of just `price_max`, support both `price_min` and `price_max`.

**Requirements:**
- Accept `price_min` and `price_max` in the filters dict
- Add proper MongoDB query conditions
- Test with: `{"price_min": 50, "price_max": 150}`

<details>
<summary>💡 Hint</summary>

```python
if 'price_min' in filters or 'price_max' in filters:
    price_condition = {}
    if 'price_min' in filters:
        price_condition['$gte'] = filters['price_min']
    if 'price_max' in filters:
        price_condition['$lte'] = filters['price_max']
    match_conditions['price'] = price_condition
```
</details>

### Challenge 2: Property Type Filter (Easy)
Add support for filtering by property type (e.g., "House", "Apartment", "Condominium").

**Requirements:**
- Accept `property_type` in the filters dict
- Can be a single string or a list of types
- Test with: `{"property_type": "House"}` and `{"property_type": ["House", "Apartment"]}`

<details>
<summary>💡 Hint</summary>

```python
if 'property_type' in filters:
    if isinstance(filters['property_type'], list):
        match_conditions['property_type'] = {"$in": filters['property_type']}
    else:
        match_conditions['property_type'] = filters['property_type']
```
</details>

### Challenge 3: Geospatial Search (Advanced)
Add support for searching within a radius of a given location.

**Requirements:**
- Accept `location` (coordinates as `[lng, lat]`) and `radius_km` in filters
- Note: Our data uses separate `latitude`/`longitude` fields, so use a bounding-box approach
- Test with Denver coordinates: `{"location": [-104.9903, 39.7392], "radius_km": 10}`

<details>
<summary>💡 Hint</summary>

Since our data has separate `latitude`/`longitude` fields (not GeoJSON), use a bounding box approach:

```python
import math

if 'location' in filters and 'radius_km' in filters:
    lng, lat = filters['location']
    # Approximate degrees per km at this latitude
    lat_delta = filters['radius_km'] / 111.0
    lng_delta = filters['radius_km'] / (111.0 * abs(math.cos(math.radians(lat))))
    match_conditions['latitude'] = {"$gte": lat - lat_delta, "$lte": lat + lat_delta}
    match_conditions['longitude'] = {"$gte": lng - lng_delta, "$lte": lng + lng_delta}
```
</details>

### Challenge 4: Hybrid Scoring (Advanced)
Combine semantic similarity with price preference (favor cheaper listings).

**Requirements:**
- Calculate a hybrid score: `final_score = semantic_score * 0.7 + price_score * 0.3`
- Price score: normalize price to 0-1 range (lower price = higher score)
- Resort results by hybrid score

<details>
<summary>💡 Hint</summary>

```python
# After getting results, calculate hybrid scores
for result in results:
    semantic_score = result.get('searchScore', 0)
    price = result.get('price', 100)
    
    # Normalize price (assuming max price is 500)
    price_score = 1 - (min(price, 500) / 500)
    
    # Calculate hybrid score
    result['hybridScore'] = semantic_score * 0.7 + price_score * 0.3

# Sort by hybrid score
results.sort(key=lambda x: x.get('hybridScore', 0), reverse=True)
```
</details>

## 🎯 Bonus Challenge: Load the Full Dataset

Once you're comfortable with the search functionality, try loading the full dataset:

```python
# Load all 35K listings (this will take several minutes)
full_documents = load_data_with_embeddings(
    'data/datasets without embeddings/large_35K.json',
    limit=None  # Process all documents
)

# Insert into DocumentDB
insert_documents(full_documents)

# Recreate indexes
create_vector_index()

# Test search on full dataset
results = search_listings("luxury penthouse with city views", limit=10)
```

**⚠️ Note:** Generating embeddings for 35K listings will:
- Take approximately 10-15 minutes
- Cost around $0.05-0.10 in OpenAI API usage
- Require proper rate limit handling (already built into our function)

## 📖 Additional Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [DocumentDB Vector Search Documentation](https://documentdb.io/docs/latest/vector-search/)
- [Understanding Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)

## ✅ Checkpoint

Before moving to Module 2, ensure you have:

- [ ] Successfully connected to DocumentDB
- [ ] Generated embeddings using OpenAI's API
- [ ] Created a vector search index (IVF)
- [ ] Implemented basic semantic search
- [ ] Added filters to refine search results
- [ ] Tested with various natural language queries
- [ ] Completed at least one challenge exercise

## 🎉 What's Next?

In **Module 2: RAG Pattern Implementation**, you'll learn how to:
- Build a conversational AI that uses your vector search
- Implement Retrieval-Augmented Generation (RAG) with LangChain
- Create context-aware responses using retrieved listings
- Handle conversation memory and follow-up questions
- Optimize prompts for better AI responses

---

**💬 Questions or Issues?**  
If you're stuck, check the troubleshooting section in Module 0, or ask your instructor for help!
