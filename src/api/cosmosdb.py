from pymongo import MongoClient, UpdateOne
import os
import bson
import numpy as np
from openai import OpenAI


# Connect to DocumentDB
MONGO_CONNECTION_STRING = os.getenv("DOCUMENTDB_CONNECTION_STRING")
mongo_client = MongoClient(MONGO_CONNECTION_STRING)

db = mongo_client['contoso_bookings']

# Create collection if it doesn't exist
COLLECTION_NAME = "listings"

collection = db[COLLECTION_NAME]

if COLLECTION_NAME not in db.list_collection_names():
    db.create_collection(COLLECTION_NAME)
    print("Created collection '{}'.\n".format(COLLECTION_NAME))
else:
    print("Using collection: '{}'.\n".format(COLLECTION_NAME))

# Initialize OpenAI client for embeddings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def get_embedding(text):
    """Generate embedding for text using OpenAI"""
    response = openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def search_listings(query, amenity, user_location):

    amenities = ["WiFi"]
    
    if type(amenity) == list:
        amenities.extend(amenity)
    else:
        amenities.append(amenity)

    # Generate embedding for the query
    query_embedding = get_embedding(query)

    # First, filter by location and amenities
    # The query converts the distance to radians by dividing by the approximate equatorial radius of the earth, 3963.2 miles
    filter_query = {
        "$and": [
            {"amenities": {"$in": amenities}},
            {"location": {"$geoWithin": {"$centerSphere": [user_location, 30/3963.2]}}},
            {"embeddings": {"$exists": True}}
        ]
    }
    
    # Get filtered documents
    candidates = list(collection.find(filter_query))
    
    # Calculate similarity scores for each candidate
    scored_results = []
    for doc in candidates:
        if 'embeddings' in doc and doc['embeddings']:
            similarity = cosine_similarity(query_embedding, doc['embeddings'])
            doc['similarity_score'] = round(similarity, 2)
            doc['_id'] = str(doc['_id'])
            scored_results.append(doc)
    
    # Sort by similarity and return top 5
    scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
    results = scored_results[:5]

    return results
    
