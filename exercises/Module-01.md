# Module 1: Vector Search Fundamentals


### 📓 **[Open the Jupyter Notebook](../module-01.ipynb)** to follow along with the code exercises.


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

## 🛠️ Step 1: Understanding the Data

Let's first explore the dataset structure.

### Dataset Overview

Our dataset contains Airbnb listings with the following key fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `_id` | string | Unique identifier | `"10006546"` |
| `listing_url` | string | URL to the listing | `"https://www.airbnb.com/rooms/10006546"` |
| `name` | string | Property title | `"Ribeira Charming Duplex"` |
| `summary` | string | Brief description | `"Fantastic duplex apartment..."` |
| `space` | string | Details about the space | `"Privileged views of the river..."` |
| `description` | string | Full description (combined) | Concatenated text for embeddings |
| `neighborhood_overview` | string | Area information | `"In the neighborhood of the river..."` |
| `notes` | string | Additional notes | Important guest information |
| `amenities` | array | List of amenities | `["Wifi", "Kitchen", "TV", ...]` |
| `property_type` | string | Type of property | `"House"`, `"Apartment"`, etc. |
| `room_type` | string | Room configuration | `"Entire home/apt"` |
| `bedrooms` | number | Number of bedrooms | `1`, `2`, `3`, etc. |
| `beds` | number | Number of beds | `1`, `2`, `3`, etc. |
| `price` | number | Nightly price | `80.00` |
| `address` | object | Location details | See below |
| `address.location` | object | Coordinates | `{type: "Point", coordinates: [lng, lat]}` |
| `address.country` | string | Country code | `"United States"` |
| `address.market` | string | City/Market | `"Chicago"` |

### Import required libraries

```python
import os
import json
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print("✅ Libraries imported and environment loaded")
```

**💡 Key Insight:** The `description` field is what we'll convert into vector embeddings for semantic search.

## 🛠️ Step 2: Set Up Environment & Connect to DocumentDB

```python
# Connect to DocumentDB
DOCUMENTDB_CONNECTION_STRING = os.getenv('DOCUMENTDB_CONNECTION_STRING')
client = MongoClient(DOCUMENTDB_CONNECTION_STRING)
db = client['db']
collection = db['listings']

print("✅ Connected to DocumentDB")
print(f"📊 Current document count: {collection.count_documents({})}")
```

### Verify Connection

```python
# Test the connection by fetching one document
test_doc = collection.find_one()
if test_doc:
    print(f"✅ Successfully retrieved document: {test_doc.get('name', 'Unknown')}")
else:
    print("⚠️ No documents found. We'll load data next.")
```

## 🛠️ Step 3: Load and Examine Sample Data

### Create an Embedding Function

```python
# Load a small sample to examine
with open('data/raw_data.json', 'r') as f:
    data = json.load(f)

# Look at the first listing
sample = data[0]
print(f"Listing ID: {sample['id']}")
print(f"Name: {sample['name']}")
print(f"Property Type: {sample['property_type']}")
print(f"Bedrooms: {sample.get('bedrooms', 'N/A')}")
print(f"Price: ${sample.get('price', 'N/A')}")
print(f"Amenities: {', '.join(sample.get('amenities', [])[:5])}...")
print(f"\nDescription Preview:")
print(sample.get('description', '')[:200] + "...")
```

## 🛠️ Step 4: Create Embedding Generation Function

We'll use OpenAI's `text-embedding-3-small` model to generate 1536-dimension vectors that capture semantic meaning.

### 💡 Understanding the Embedding

Each number in the 1536-dimension vector represents a learned feature. The model has discovered that certain combinations of these numbers correspond to semantic concepts like "cozy", "parking", "downtown", etc.

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

# Test the function
test_text = "Cozy apartment near downtown with free parking"
test_embedding = generate_embedding(test_text)

print(f"✅ Generated embedding")
print(f"📏 Dimensions: {len(test_embedding)}")
print(f"📊 First 5 values: {test_embedding[:5]}")
print(f"📊 Data type: {type(test_embedding[0])}")
```

## 🛠️ Step 5: Load Data with Embeddings

We'll use OpenAI's `text-embedding-3-small` model to generate 1536-dimension vectors that capture semantic meaning.

```python
def load_data_with_embeddings(file_path, limit=None):
    """
    Load data from JSON file and generate embeddings for each listing.
    
    Args:
        file_path (str): Path to the JSON data file
        limit (int, optional): Maximum number of documents to process
        
    Returns:
        list: Documents with embeddings added
    """
    print(f"📖 Loading data from {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if limit:
        data = data[:limit]
    
    print(f"📊 Loaded {len(data)} documents")
    print("🔄 Generating embeddings...")
    
    documents_with_embeddings = []
    
    for idx, doc in enumerate(data):
        # Create a rich description for embedding
        description_text = doc.get('description', '')
        
        # Generate embedding
        embedding = generate_embedding(description_text)
        
        if embedding:
            doc['descriptionVector'] = embedding
            documents_with_embeddings.append(doc)
            
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(data)} documents...")
    
    print(f"✅ Generated embeddings for {len(documents_with_embeddings)} documents")
    return documents_with_embeddings
```
```python
# Start with a small dataset for testing (50 documents)
documents = load_data_with_embeddings(
    'data/raw_data.json',
    limit=50
)
```
```python
# Show one document from the documents list
print(f"📄 Sample document with new embeddings:\n")
sample_doc = documents[0]
print(f"ID: {sample_doc.get('id')}")
print(f"Name: {sample_doc.get('name')}")
print(f"Property Type: {sample_doc.get('property_type')}")
print(f"Bedrooms: {sample_doc.get('bedrooms', 'N/A')}")
print(f"Price: ${sample_doc.get('price', 'N/A')}")
print(f"Has embedding: {'descriptionVector' in sample_doc}")
print(f"Embedding dimensions: {len(sample_doc.get('descriptionVector', []))}")
```

## 🛠️ Step 6: Create Vector Index Using the DocumentDB for VS Code Extension

Now that your data with embeddings is loaded in DocumentDB, you need to create a **vector search index** to enable fast similarity searches.

### Instructions:

1. **Open the DocumentDB Extension** in VS Code (click the database icon in the sidebar)

2. **Navigate to your Scrapbook**:
   - Right-click on your connection
   - Select **"New Scrapbook"** (or open an existing `.mongodb` scrapbook file)

3. **Run the following commands** in your scrapbook (select each block and press `Ctrl+Enter` or click "Run"):

```javascript
// Create vector search index on the descriptionVector field
db.listings.createIndex(
    { "descriptionVector": "cosmosSearch" },
    {
        name: "vectorSearchIndex",
        cosmosSearchOptions: {
            kind: "vector-ivf",
            numLists: 100,
            similarity: "COS",
            dimensions: 1536
        }
    }
)
```

4. **Create filter indexes** for better query performance:

```javascript
// Create filter indexes
db.listings.createIndex({ "address.market": 1 })
db.listings.createIndex({ "property_type": 1 })
db.listings.createIndex({ "bedrooms": 1 })
db.listings.createIndex({ "price": 1 })
```

5. **Verify the indexes were created**:

```javascript
// Check all indexes on the collection
db.listings.getIndexes()
```

**Expected Output:**
```json
[
  { "name": "_id_", "key": { "_id": 1 } },
  { "name": "vectorSearchIndex", "key": { "descriptionVector": "cosmosSearch" } },
  { "name": "address.market_1", "key": { "address.market": 1 } },
  { "name": "property_type_1", "key": { "property_type": 1 } },
  { "name": "bedrooms_1", "key": { "bedrooms": 1 } },
  { "name": "price_1", "key": { "price": 1 } }
]
```

### 💡 Understanding Index Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `kind` | `"vector-ivf"` | Uses Inverted File Index for fast approximate search |
| `numLists` | `100` | Number of clusters (higher = more accurate but slower) |
| `similarity` | `"COS"` | Cosine similarity (range: 0 to 1, where 1 = identical) |
| `dimensions` | `1536` | Must match your embedding size (OpenAI text-embedding-3-small) |

## 🛠️ Step 7: Create Vector Search Index

### Understanding DocumentDB Vector Indexes

DocumentDB supports native vector search with two index types:

1. **IVF (Inverted File Index)**: Fast, approximate search suitable for large datasets
2. **HNSW (Hierarchical Navigable Small World)**: More accurate but uses more memory

For this workshop, we'll use **IVF** for better performance with our dataset.

### Create the Vector Index

```python
def create_vector_index():
    """
    Create a vector search index on the descriptionVector field.
    Uses IVF (Inverted File Index) for efficient approximate search.
    """
    try:
        # Drop existing vector index if it exists
        try:
            collection.drop_index("vectorSearchIndex")
            print("🗑️ Dropped existing vector index")
        except:
            pass  # Index doesn't exist yet
        
        # Create vector search index
        collection.create_index(
            [("descriptionVector", "cosmosSearch")],
            name="vectorSearchIndex",
            cosmosSearchOptions={
                "kind": "vector-ivf",
                "numLists": 100,  # Number of clusters for IVF
                "similarity": "COS",  # Cosine similarity
                "dimensions": 1536  # Must match embedding dimensions
            }
        )
        print("✅ Created vector search index (IVF)")
        
        # Also create indexes for filtering
        collection.create_index([("address.market", 1)])
        collection.create_index([("property_type", 1)])
        collection.create_index([("bedrooms", 1)])
        collection.create_index([("price", 1)])
        print("✅ Created filter indexes")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        raise

# Create the indexes
create_vector_index()

# Verify indexes
indexes = list(collection.list_indexes())
print(f"\n📋 Current indexes:")
for idx in indexes:
    print(f"  - {idx['name']}: {idx['key']}")
```

**Expected Output:**
```
✅ Created vector search index (IVF)
✅ Created filter indexes

📋 Current indexes:
  - _id_: [('_id', 1)]
  - vectorSearchIndex: [('descriptionVector', 'cosmosSearch')]
  - address.market_1: [('address.market', 1)]
  - property_type_1: [('property_type', 1)]
  - bedrooms_1: [('bedrooms', 1)]
  - price_1: [('price', 1)]
```

### 💡 Understanding Index Parameters

- **kind**: `"vector-ivf"` uses Inverted File Index for speed
- **numLists**: Controls the speed/accuracy tradeoff (higher = more accurate, slower)
- **similarity**: `"COS"` for cosine similarity (range: -1 to 1, where 1 = identical)
- **dimensions**: Must match the embedding size (1536 for text-embedding-3-small)

## 🛠️ Step 8: Implement Semantic Search

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
                "address.market": 1,
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
    print(f"   Location: {result.get('address', {}).get('market', 'N/A')}")
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
   Location: Chicago
   Bedrooms: 1 | Price: $95.0
   Similarity Score: 0.8523
   Preview: Cozy studio apartment in the heart of downtown. Free parking included. Walking distance to...

2. City Center Apartment
   Property Type: Apartment
   Location: Denver
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

## 🛠️ Step 9: Add Filters to Refine Search

### Search with Filters

```python
def search_listings_with_filters(query, filters=None, limit=5):
    """
    Search for listings with semantic similarity and additional filters.
    
    Args:
        query (str): Natural language search query
        filters (dict): Optional filters (bedrooms, price_max, market, amenities)
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
        
        if 'market' in filters:
            match_conditions['address.market'] = filters['market']
        
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
                "address.market": 1,
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
    print(f"   Location: {result.get('address', {}).get('market', 'N/A')}")
    print(f"   Bedrooms: {result.get('bedrooms', 'N/A')} | Price: ${result.get('price', 'N/A')}")
    print(f"   Similarity Score: {result.get('searchScore', 0):.4f}")
    amenities_preview = ', '.join(result.get('amenities', [])[:5])
    print(f"   Amenities: {amenities_preview}...")
    print()
```

## 🛠️ Step 10: Experiment with Different Queries

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
- Accept `location` (coordinates) and `radius_km` in filters
- Use MongoDB's `$geoWithin` operator with `$centerSphere`
- Test with Chicago coordinates: `{"location": [-87.6298, 41.8781], "radius_km": 10}`

<details>
<summary>💡 Hint</summary>

```python
if 'location' in filters and 'radius_km' in filters:
    # MongoDB uses radians: radius_in_radians = radius_km / 6378.1 (Earth's radius in km)
    radius_radians = filters['radius_km'] / 6378.1
    match_conditions['address.location'] = {
        "$geoWithin": {
            "$centerSphere": [filters['location'], radius_radians]
        }
    }
```

Note: You'll need to create a geospatial index first:
```python
collection.create_index([("address.location", "2dsphere")])
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
- [DocumentDB Vector Search Documentation](https://learn.microsoft.com/azure/cosmos-db/mongodb/vcore/vector-search)
- [Understanding Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- [IVF vs HNSW Indexes](https://learn.microsoft.com/azure/cosmos-db/mongodb/vcore/vector-search#vector-index-types)

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
