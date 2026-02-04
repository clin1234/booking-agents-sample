"""
Pydantic Models for API Requests and Responses
===============================================

Models match the embedded_data.json schema:
- id: integer (listing ID)
- latitude/longitude: separate float fields  
- descriptionVector: embedding array (not exposed in API)
- amenities: array of strings
- price: float (numeric, not string)
- beds/bedrooms: integer (nullable)
- bathrooms: float (nullable)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# Listing Models
# =============================================================================

class Listing(BaseModel):
    """
    Normalized listing model for API responses.
    
    Matches the embedded_data.json structure used in the workshop.
    """
    id: int = Field(..., description="Unique listing identifier")
    name: str = Field(..., description="Listing name/title")
    description: Optional[str] = Field(None, description="Full description")
    neighborhood_overview: Optional[str] = Field(None, description="Neighborhood info")
    
    # Pricing
    price: float = Field(0, description="Price per night")
    
    # Property details
    property_type: Optional[str] = Field(None, description="e.g., Apartment, House")
    room_type: Optional[str] = Field(None, description="e.g., Entire home/apt")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    beds: Optional[int] = Field(None, description="Number of beds")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    
    # Amenities
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    
    # Location (separate lat/lng as in embedded_data.json)
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    
    # URLs
    listing_url: Optional[str] = Field(None, description="Original listing URL")
    
    # Optional rating (if available)
    rating: Optional[float] = Field(None, description="Average rating")
    
    class Config:
        extra = "ignore"


# =============================================================================
# Search Models
# =============================================================================

class SearchFilters(BaseModel):
    """Filters for search queries."""
    bedrooms: Optional[int] = Field(None, ge=0, description="Minimum bedrooms")
    price_max: Optional[float] = Field(None, ge=0, description="Maximum price")
    property_type: Optional[str] = Field(None, description="Property type filter")
    amenities: Optional[List[str]] = Field(None, description="Required amenities")
    city: Optional[str] = Field(None, description="City/market filter")


class SearchRequest(BaseModel):
    """Request model for /search endpoint."""
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters")


class SearchResult(BaseModel):
    """Single search result with listing and score."""
    listing: Listing
    score: float = Field(default=0.0, ge=0, le=1, description="Similarity score")


class SearchResponse(BaseModel):
    """Response model for /search endpoint."""
    results: List[SearchResult]
    total: int = Field(..., description="Total results returned")
    query: str = Field(..., description="Original query")
    search_type: str = Field(..., description="vector, text, or static")


# =============================================================================
# Chat Models
# =============================================================================

class ChatRequest(BaseModel):
    """Request model for /query_message endpoint."""
    message: str = Field(..., min_length=1, description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for history")
    use_agents: bool = Field(True, description="Use multi-agent system if available")


class ChatResponse(BaseModel):
    """Response model for /query_message endpoint."""
    message: str = Field(..., description="AI response")
    search_results: List[SearchResult] = Field(
        default_factory=list,
        description="Related listings"
    )
    session_id: str = Field(..., description="Session ID")
    agent_path: List[str] = Field(
        default_factory=list,
        description="Agents used (multi-agent mode)"
    )
    multi_agent: bool = Field(False, description="Whether multi-agent was used")


# =============================================================================
# Health Check Models
# =============================================================================

class CapabilityStatus(BaseModel):
    """Status of each capability for health check."""
    database: bool = Field(..., description="DocumentDB connected")
    vector_search: bool = Field(..., description="Vector index available")
    text_search: bool = Field(..., description="Text search available")
    static_data: bool = Field(..., description="Static data fallback available")
    chat: bool = Field(..., description="Chat/RAG available")
    multi_agent: bool = Field(..., description="LangGraph agents available")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(..., description="ok, degraded, or error")
    message: str = Field(..., description="Status message")
    capabilities: CapabilityStatus
    database_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Database connection details"
    )


# =============================================================================
# Utility Functions
# =============================================================================

def normalize_listing(doc: Dict[str, Any]) -> Listing:
    """
    Normalize a raw listing document to the Listing model.
    
    Handles both raw data format and database format from embedded_data.json.
    """
    # Handle ID (could be _id from MongoDB or id from JSON)
    raw_id = doc.get('_id', doc.get('id', 0))
    try:
        listing_id = int(raw_id) if raw_id else 0
    except (ValueError, TypeError):
        listing_id = 0
    
    # Handle price - already numeric in updated embedded_data.json, but handle legacy string format
    price = doc.get('price', 0)
    if isinstance(price, str):
        # Remove $ and commas, handle empty string
        cleaned = price.replace('$', '').replace(',', '').strip()
        try:
            price = float(cleaned) if cleaned else 0
        except ValueError:
            price = 0
    
    # Handle amenities - could be JSON string or array
    amenities = doc.get('amenities', [])
    if isinstance(amenities, str):
        try:
            import json
            amenities = json.loads(amenities)
        except:
            amenities = []
    
    # Helper functions for type conversion
    def to_int(val) -> Optional[int]:
        if val is None:
            return None
        try:
            return int(float(str(val)))
        except (ValueError, TypeError):
            return None
    
    def to_float(val) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(str(val))
        except (ValueError, TypeError):
            return None
    
    # Handle coordinates (embedded_data.json uses separate lat/lng)
    latitude = to_float(doc.get('latitude'))
    longitude = to_float(doc.get('longitude'))
    
    # Also check for GeoJSON format (address.location.coordinates)
    if latitude is None or longitude is None:
        location = doc.get('location')
        if isinstance(location, dict) and 'coordinates' in location:
            coords = location['coordinates']
            if isinstance(coords, list) and len(coords) >= 2:
                longitude = coords[0]
                latitude = coords[1]
        
        # Check address.location format
        address = doc.get('address', {})
        if isinstance(address, dict):
            loc = address.get('location', {})
            if isinstance(loc, dict) and 'coordinates' in loc:
                coords = loc['coordinates']
                if isinstance(coords, list) and len(coords) >= 2:
                    longitude = coords[0]
                    latitude = coords[1]
    
    return Listing(
        id=listing_id,
        name=doc.get('name', 'Unknown'),
        description=doc.get('description'),
        neighborhood_overview=doc.get('neighborhood_overview'),
        price=price if isinstance(price, (int, float)) else 0,
        property_type=doc.get('property_type'),
        room_type=doc.get('room_type'),
        bedrooms=to_int(doc.get('bedrooms')),
        beds=to_int(doc.get('beds')),
        bathrooms=to_float(doc.get('bathrooms')),
        amenities=amenities if isinstance(amenities, list) else [],
        latitude=latitude,
        longitude=longitude,
        listing_url=doc.get('listing_url'),
        rating=to_float(doc.get('rating') or doc.get('review_scores_rating')),
    )
