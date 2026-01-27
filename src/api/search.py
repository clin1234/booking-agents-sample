"""
Search Module - Vector Search with Fallbacks
=============================================

Implements the search functionality matching the workshop exercises:
- Module 1: Vector search using cosmosSearch with descriptionVector
- Fallback: Text-based search when vector index isn't available
- Fallback: Static data search when database isn't connected

Field mappings match embedded_data.json:
- descriptionVector: 1536-dim OpenAI embeddings
- latitude/longitude: Separate coordinate fields
- amenities: Array of strings
"""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from .config import settings
from .database import db, load_static_data
from .models import Listing, SearchResult, SearchFilters, normalize_listing

logger = logging.getLogger(__name__)


# =============================================================================
# OpenAI Embeddings
# =============================================================================

_openai_client: Optional[OpenAI] = None


def get_openai_client() -> Optional[OpenAI]:
    """Get or create OpenAI client."""
    global _openai_client
    
    if _openai_client is None and settings.has_openai_key:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    return _openai_client


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding vector for text using OpenAI.
    
    This matches the generate_embedding function in Module 1 exercises.
    Returns 1536-dimension vector for text-embedding-3-small.
    """
    if not text or not isinstance(text, str):
        return None
    
    client = get_openai_client()
    if not client:
        logger.warning("OpenAI client not available - no API key configured")
        return None
    
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return None


# =============================================================================
# Vector Search (Module 1+)
# =============================================================================

def vector_search(
    query: str,
    limit: int = 5,
    filters: Optional[SearchFilters] = None
) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search using DocumentDB's cosmosSearch.
    
    This matches the search_listings and search_listings_with_filters
    functions from Module 1 exercises.
    
    Uses:
    - descriptionVector field for similarity search
    - $match stage for post-filtering (as shown in exercises)
    
    Args:
        query: Natural language search query
        limit: Maximum number of results (k in cosmosSearch)
        filters: Optional filters (bedrooms, price_max, property_type, amenities)
    
    Returns:
        List of matching documents with searchScore
    """
    collection = db.get_collection()
    
    if collection is None:
        logger.warning("No database collection available for vector search")
        return []
    
    # Generate query embedding
    query_embedding = generate_embedding(query)
    if not query_embedding:
        logger.warning("Could not generate embedding for query")
        return []
    
    # Build aggregation pipeline (matching Module 1 exercises)
    pipeline = [
        # Vector search stage
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "descriptionVector",  # Matches embedded_data.json
                    "k": limit * 3  # Fetch more to account for filtering
                },
                "returnStoredSource": True
            }
        }
    ]
    
    # Add filter stage if filters provided (matches Module 1 Step 8)
    if filters:
        match_conditions = {}
        
        if filters.bedrooms is not None:
            match_conditions['bedrooms'] = {"$gte": filters.bedrooms}
        
        if filters.price_max is not None:
            match_conditions['price'] = {"$lte": filters.price_max}
        
        if filters.property_type:
            match_conditions['property_type'] = {
                "$regex": filters.property_type,
                "$options": "i"
            }
        
        if filters.amenities and len(filters.amenities) > 0:
            # Check if all required amenities are present
            match_conditions['amenities'] = {"$all": filters.amenities}
        
        if match_conditions:
            pipeline.append({"$match": match_conditions})
    
    # Projection and limit (matching Module 1 exercises)
    pipeline.extend([
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "id": 1,
                "name": 1,
                "description": 1,
                "neighborhood_overview": 1,
                "property_type": 1,
                "room_type": 1,
                "bedrooms": 1,
                "beds": 1,
                "bathrooms": 1,
                "price": 1,
                "amenities": 1,
                "latitude": 1,
                "longitude": 1,
                "listing_url": 1,
                "searchScore": {"$meta": "searchScore"}  # Similarity score
            }
        },
        {"$limit": limit}
    ])
    
    try:
        results = list(collection.aggregate(pipeline))
        logger.info(f"Vector search returned {len(results)} results for: {query[:50]}...")
        return results
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []


# =============================================================================
# Text Search Fallback
# =============================================================================

def text_search(
    query: str,
    limit: int = 5,
    filters: Optional[SearchFilters] = None,
    data: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Perform text-based search as fallback when vector search isn't available.
    
    Works with either database documents or static data.
    Uses simple keyword matching with scoring.
    
    Args:
        query: Search query text
        limit: Maximum results to return
        filters: Optional filters
        data: Optional data source (uses static data if not provided)
    
    Returns:
        List of matching documents with similarity_score
    """
    # Get data source
    if data is None:
        collection = db.get_collection()
        if collection is not None:
            try:
                data = list(collection.find().limit(500))
            except Exception as e:
                logger.warning(f"Database query failed: {e}")
                data = load_static_data()
        else:
            data = load_static_data()
    
    if not data:
        return []
    
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    def score_document(doc: Dict) -> float:
        """Calculate match score for a document."""
        searchable_text = ' '.join([
            str(doc.get('name', '')),
            str(doc.get('description', '')),
            str(doc.get('neighborhood_overview', '')),
            str(doc.get('property_type', '')),
            str(doc.get('room_type', '')),
        ]).lower()
        
        # Count matching terms
        matches = sum(1 for term in query_terms if term in searchable_text)
        if matches == 0:
            return 0.0
        
        # Score based on match ratio (normalize to 0-1 range like vector search)
        return round(matches / len(query_terms), 4)
    
    def matches_filters(doc: Dict) -> bool:
        """Check if document passes all filters."""
        if not filters:
            return True
        
        if filters.bedrooms is not None:
            if doc.get('bedrooms', 0) < filters.bedrooms:
                return False
        
        if filters.price_max is not None:
            if doc.get('price', float('inf')) > filters.price_max:
                return False
        
        if filters.property_type:
            if filters.property_type.lower() not in str(doc.get('property_type', '')).lower():
                return False
        
        if filters.amenities:
            doc_amenities = doc.get('amenities', [])
            if isinstance(doc_amenities, str):
                import json
                try:
                    doc_amenities = json.loads(doc_amenities)
                except:
                    doc_amenities = []
            
            doc_amenities_lower = [a.lower() for a in doc_amenities]
            if not all(a.lower() in doc_amenities_lower for a in filters.amenities):
                return False
        
        return True
    
    # Score and filter documents
    results = []
    for doc in data:
        if not matches_filters(doc):
            continue
        
        score = score_document(doc)
        if score > 0:
            doc_copy = doc.copy()
            doc_copy['searchScore'] = score
            results.append(doc_copy)
    
    # Sort by score and limit
    results.sort(key=lambda x: x.get('searchScore', 0), reverse=True)
    return results[:limit]


# =============================================================================
# Unified Search Interface
# =============================================================================

def search_listings(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]:
    """
    Search for listings using the best available method.
    
    Progressive behavior:
    1. Vector search (requires Module 1 completion + OpenAI key)
    2. Text search on database (requires Module 0 completion)
    3. Text search on static data (always works)
    
    Args:
        query: Search query string
        limit: Maximum results (default: 10)
        filters: Optional filter dictionary
    
    Returns:
        List of SearchResult objects with listing and score
    """
    # Parse filters if provided
    search_filters = None
    if filters:
        search_filters = SearchFilters(
            bedrooms=filters.get('bedrooms'),
            price_max=filters.get('price_max') or filters.get('max_price'),
            property_type=filters.get('property_type') or filters.get('category'),
            amenities=filters.get('amenities'),
            city=filters.get('city')
        )
    
    results = []
    search_type = "static"
    
    # Try vector search first
    if db.is_connected and db.has_vector_index and settings.has_openai_key:
        raw_results = vector_search(query, limit, search_filters)
        if raw_results:
            search_type = "vector"
            results = raw_results
    
    # Fall back to text search on database
    if not results and db.is_connected:
        raw_results = text_search(query, limit, search_filters)
        if raw_results:
            search_type = "text"
            results = raw_results
    
    # Fall back to static data
    if not results:
        static_data = load_static_data()
        if static_data:
            raw_results = text_search(query, limit, search_filters, static_data)
            if raw_results:
                search_type = "static"
                results = raw_results
    
    # Convert to SearchResult objects
    search_results = []
    for doc in results:
        try:
            listing = normalize_listing(doc)
            score = doc.get('searchScore', doc.get('similarity_score', 0.5))
            search_results.append(SearchResult(listing=listing, score=score))
        except Exception as e:
            logger.warning(f"Failed to normalize listing: {e}")
            continue
    
    logger.info(f"Search '{query[:30]}...' returned {len(search_results)} results via {search_type}")
    return search_results


def get_search_capabilities() -> Dict[str, bool]:
    """
    Get current search capabilities for health check.
    
    Returns:
        Dictionary with capability flags
    """
    return {
        "vector_search": db.is_connected and db.has_vector_index and settings.has_openai_key,
        "text_search": db.is_connected,
        "static_fallback": bool(load_static_data()),
        "openai_configured": settings.has_openai_key,
    }


# =============================================================================
# Helper Functions for Exercises
# =============================================================================

def get_sample_listings(limit: int = 5) -> List[Listing]:
    """
    Get sample listings without search.
    Useful for initial display or testing.
    """
    collection = db.get_collection()
    
    if collection is not None:
        try:
            docs = list(collection.find().limit(limit))
            return [normalize_listing(doc) for doc in docs]
        except Exception as e:
            logger.warning(f"Sample query failed: {e}")
    
    # Fall back to static data
    static_data = load_static_data()
    if static_data:
        return [normalize_listing(doc) for doc in static_data[:limit]]
    
    return []
