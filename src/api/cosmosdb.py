from pymongo import MongoClient, UpdateOne
import os
import bson
from openai import OpenAI


# Connect to DocumentDB
DOCUMENTDB_CONNECTION_STRING = os.getenv("DOCUMENTDB_CONNECTION_STRING")
mongo_client = MongoClient(DOCUMENTDB_CONNECTION_STRING)

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

    # Use DocumentDB's native vector search with cosmosSearch
    # Search for the top 5 closest vectors to the query within a 30 mile radius of user's location
    pipeline = [
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_embedding,
                            "path": "embeddings",
                            "k": 5,  # Top 5 results
                            "filter": {
                                "$and": [
                                    {"amenities": {"$in": amenities}},
                                    # The query converts the distance to radians by dividing by the approximate equatorial radius of the earth, 3963.2 miles
                                    {"location": {"$geoWithin": 
                                                    {"$centerSphere": [user_location, 30/3963.2]}}}
                                ]
                            }
                        }
                    }
                },
                {
                    "$limit": 5  # Limit to top 5 results
                },
                {
                    '$project': {
                        "similarity_score": {'$round': [{'$meta': 'searchScore'}, 2]}, 
                        "location": 1,
                        "description": 1,
                        "price": 1,
                        "name": 1,
                        "amenities": 1,
                        "neighborhood_overview": 1,
                        "beds": 1,
                        "bedrooms": 1,
                        "bathrooms": 1,
                        "bathrooms_text": 1,
                        "property_type": 1,
                        "room_type": 1,
                        "host_about": 1,
                        "_id": {"$toString": "$_id"} 
                    }, 
                }
            ]
        
    results = collection.aggregate(pipeline)
    results = list(results)

    return results
    
