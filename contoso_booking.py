"""
Rental Listings RAG System with Azure DocumentDB and OpenAI
This script sets up a vector search system for rental listings using embeddings.
"""

from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne
from typing import List
from bson import ObjectId
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

# Load environment variables
load_dotenv(override=True)

# Configuration
DOCUMENTDB_CONNECTION_STRING = os.getenv("DOCUMENTDB_CONNECTION_STRING")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "listings")
DATABASE_NAME = os.getenv("DATABASE_NAME", "contoso_bookings")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")

# User's location (longitude, latitude)
USER_LOCATION = [-105.0020980834961, 39.766414642333984]

# Initialize clients
print(f"OpenAI API Key: {OPENAI_API_KEY}")
mongo_client = MongoClient(DOCUMENTDB_CONNECTION_STRING)
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def setup_collection():
    """Create collection if it doesn't exist"""
    if COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(COLLECTION_NAME)
        print(f"Created collection '{COLLECTION_NAME}'.\n")
    else:
        print(f"Using collection: '{COLLECTION_NAME}'.\n")


def create_indexes():
    """Create vector search and geospatial indexes"""
    # Vector search index using DocumentDB's cosmosSearch
    db.command({
        'createIndexes': 'listings',
        'indexes': [
            {
                'name': 'vector_search_index',
                'key': {
                    "embeddings": "cosmosSearch"
                },
                'cosmosSearchOptions': {
                    'kind': 'vector-ivf',
                    'numLists': 100,
                    'similarity': 'COS',
                    'dimensions': 1536
                }
            }
        ]
    })

    # Geospatial index for location-based queries
    db.command({
        'createIndexes': 'listings',
        'indexes': [
            {
                'name': 'location_2dsphere',
                'key': {
                    "location": "2dsphere"
                }
            }
        ]
    })

    # Index on amenities for faster filtering
    collection.create_index('amenities')
    
    print("Indexes created successfully")


def load_data(file_path):
    """Load JSON data from file"""
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"Loaded {len(data)} records")
    print(f"First record: {data[0]}")
    return data


def generate_embedding(text):
    """Generate embedding for text using OpenAI"""
    response = openai_client.embeddings.create(
        input=text,
        model=OPENAI_EMBEDDING_MODEL
    )
    return response.data[0].embedding


def update_embeddings(batch_size=15):
    """Update embeddings for all records in batches"""
    total_updated = 0
    iteration = 0

    while True:
        iteration += 1

        # Find records to update
        records_to_update = collection.find({
            '$and': [
                {'embeddings': {'$exists': False}},
                {'description': {'$exists': True}}
            ]
        }).limit(batch_size)

        records_to_update = list(records_to_update)

        if not records_to_update:
            print(f"All rows have been updated. Total updated rows: {total_updated}")
            break

        total_updated += len(records_to_update)
        print(f"Iteration: {iteration}, has handled {total_updated} rows")

        # Prepare bulk operations
        bulk_ops = []
        for record in records_to_update:
            # Combine text fields for embedding
            text_to_embed = ' '.join(filter(None, [
                record.get('name', ''),
                record.get('description', ''),
                record.get('neighborhood_overview', '')
            ]))
            
            # Generate embedding
            embedding = generate_embedding(text_to_embed)
            
            # Create update operation
            bulk_ops.append(
                UpdateOne(
                    {'_id': record['_id']},
                    {'$set': {'embeddings': embedding}}
                )
            )

        if bulk_ops:
            result = collection.bulk_write(bulk_ops)
            print(f"Bulk write result: Modified {result.modified_count} documents")

        time.sleep(0.5)  # Sleep to avoid rate limits


def search_listings(query, amenities=["WiFi", "Dishwasher", "Gym"], limit=5):
    """
    Search for listings using DocumentDB's native vector search (cosmosSearch)
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query)
    
    # Use DocumentDB's cosmosSearch for efficient vector similarity search
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "embeddings",
                    "k": limit,
                    "filter": {
                        "$and": [
                            {"amenities": {"$in": amenities}},
                            {"location": {"$geoWithin": {"$centerSphere": [USER_LOCATION, 30/3963.2]}}}
                        ]
                    }
                }
            }
        },
        {
            "$limit": limit
        },
        {
            '$project': {
                "similarityScore": {'$round': [{'$meta': 'searchScore'}, 2]}, 
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
                "_id": 1
            }
        }
    ]
    
    # Execute the aggregation pipeline
    results = collection.aggregate(pipeline)
    
    # Print and format results
    results_dict = []
    for doc in results:
        print(f"Similarity Score: {doc.get('similarityScore', 'N/A')}")  
        print(f"id: {doc['_id']}")
        print(f"Name: {doc.get('name', 'N/A')}")  
        print(f"Location: {doc.get('location', 'N/A')}")  
        print(f"Description: {doc.get('description', 'N/A')}")  
        print(f"Neighborhood Overview: {doc.get('neighborhood_overview', 'N/A')}")
        print(f"Price per day: {doc.get('price', 'N/A')}") 
        print(f"Amenities: {doc.get('amenities', 'N/A')}")
        print(f"Listing Url: {doc.get('listing_url', 'N/A')}\n") 
    
        result = {
            "similarityScore": doc.get('similarityScore', 0),
            "id": str(doc['_id']),
            "name": doc.get('name', 'N/A'),
            "location": doc.get('location', 'N/A'),
            "description": doc.get('description', 'N/A'),
            "neighborhood_overview": doc.get('neighborhood_overview', 'N/A'),
            "price": doc.get('price', 'N/A'),
            "amenities": doc.get('amenities', 'N/A'),
            "listing_url": doc.get('listing_url', 'N/A')
        }
        results_dict.append(result)
    
    return results_dict


class CustomRetriever(BaseRetriever):
    """Custom retriever for rental listings"""
    
    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        search_results = search_listings(query)
    
        documents = []
        for result in search_results:
            document = Document(
                id={result['id']},
                page_content=result['name'],
                metadata=result
            )
            documents.append(document)
        return documents


def setup_rag_chains():
    """Setup RAG prompt templates and chains"""
    # Initialize OpenAI chat model
    openai_chat = ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.7,
    )

    # Define prompt templates
    REPHRASE_PROMPT = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone Question:"""

    CONTEXT_PROMPT = """\
You are a chatbot, tasked with answering any question about \
rental listings from the context. You can also answer questions about the particular areas, and provide suggestions for things to do.\
You may ask a follow up question about things the user likes to do while on vacation or if there's a particular point of interest.

Generate a response of 100 words or less for the \
given question based solely on the provided search results. \
You must only use information from the provided search results. Use an unbiased and \
fun tone. Do not repeat text. Your response must be solely based on the provided context.

If there is nothing in the context is relevant to the question at hand, just say \
"I'm not sure." Don't try to make up an answer.

Anything between the following `context` html blocks is retrieved from a knowledge \
bank, not part of the conversation with the user. 

<context>
    {context} 
<context/>

REMEMBER: If there is no relevant information within the context, just say "I'm \
not sure." Don't try to make up an answer. Anything between the preceding 'context' \
html blocks is retrieved from a knowledge bank, not part of the conversation with the \
user.\

User Question: {input}

Chatbot Response:"""

    rephrase_prompt_template = ChatPromptTemplate.from_template(REPHRASE_PROMPT)
    context_prompt_template = ChatPromptTemplate.from_template(CONTEXT_PROMPT)

    # Create chains
    rephrase_chain = rephrase_prompt_template | openai_chat
    context_chain = context_prompt_template | openai_chat

    return rephrase_chain, context_chain, openai_chat


def chat_conversation(rephrase_chain, context_chain, retriever):
    """Run a sample chat conversation"""
    messages = [{"content": "Do you have any houses in quiet neighborhoods?", "role": "user"}]

    # First question
    rephrased_question = rephrase_chain.invoke({"chat_history": messages[:-1], "question": messages[-1]})
    print(f"Rephrased Question: {rephrased_question.content}")
    
    # Get context and generate response
    context = retriever.invoke(str(rephrased_question.content))
    response = context_chain.invoke({"context": context, "input": rephrased_question.content})
    print(f"LLM Response: {response.content}\n")
    
    messages.append({"content": response.content, "role": "assistant"})
    
    # Follow-up question
    messages.append({"content": "Which rental listings are quiet?", "role": "user"})
    
    rephrased_question = rephrase_chain.invoke({"chat_history": messages[:-1], "question": messages[-1]})
    context = retriever.invoke(str(rephrased_question.content))
    response = context_chain.invoke({"context": context, "input": rephrased_question.content})
    
    print(f"Rephrased Question: {rephrased_question.content}")
    print(f"LLM Response: {response.content}")


def main():
    """Main execution function"""
    # Setup
    setup_collection()
    create_indexes()
    
    # Load data (uncomment if needed)
    # data = load_data("data/datasets without embeddings/small_for_testing.json")
    
    # Update embeddings (uncomment if needed)
    # update_embeddings(batch_size=15)
    
    # Test search
    print("\n=== Testing Search ===")
    query = "quiet home with hot tub"
    search_listings(query)
    
    # Setup RAG system
    print("\n=== Setting up RAG System ===")
    rephrase_chain, context_chain, openai_chat = setup_rag_chains()
    
    # Test chat
    test_response = openai_chat.invoke("Tell me a joke")
    print(f"Chat test: {test_response.content}\n")
    
    # Create retriever
    retriever = CustomRetriever()
    
    # Run conversation
    print("\nRunning Chat Conversation")
    chat_conversation(rephrase_chain, context_chain, retriever)


if __name__ == "__main__":
    main()