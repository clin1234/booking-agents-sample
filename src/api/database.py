"""
Database module for DocumentDB connection and operations.
Provides graceful degradation when database is unavailable.
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages DocumentDB connection with graceful degradation.
    Falls back to static data when database is unavailable.
    """
    
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db = None
        self._collection = None
        self._is_connected: bool = False
        self._static_data: Optional[List[Dict]] = None
        self._has_vector_index: bool = False
        
    def connect(self) -> bool:
        """
        Attempt to connect to DocumentDB.
        Returns True if successful, False otherwise.
        """
        try:
            self._client = MongoClient(
                settings.DOCUMENTDB_CONNECTION_STRING,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Ping to verify connection
            self._client.admin.command('ping')
            
            self._db = self._client[settings.DATABASE_NAME]
            self._collection = self._db[settings.COLLECTION_NAME]
            self._is_connected = True
            
            # Check if vector index exists
            self._check_vector_index()
            
            print(f"✅ Connected to DocumentDB: {settings.DATABASE_NAME}.{settings.COLLECTION_NAME}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"⚠️ DocumentDB not available: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            print(f"⚠️ Database connection error: {e}")
            self._is_connected = False
            return False
    
    def _check_vector_index(self) -> bool:
        """Check if the vector search index exists."""
        try:
            indexes = list(self._collection.list_indexes())
            for idx in indexes:
                # Check for cosmosSearch vector index
                if 'cosmosSearchOptions' in idx.get('key', {}):
                    self._has_vector_index = True
                    print("✅ Vector search index found")
                    return True
                # Alternative: check index name
                if 'vector' in idx.get('name', '').lower():
                    self._has_vector_index = True
                    print("✅ Vector search index found")
                    return True
            
            self._has_vector_index = False
            print("⚠️ Vector search index not found - will use text fallback")
            return False
        except Exception as e:
            print(f"⚠️ Could not check indexes: {e}")
            self._has_vector_index = False
            return False
    
    def load_static_data(self) -> bool:
        """Load static data from embedded_data.json as fallback."""
        try:
            # Try multiple paths for the data file
            paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embedded_data.json'),
                os.path.join(os.path.dirname(__file__), 'data', 'embedded_data.json'),
                '/data/embedded_data.json',
                '/workspaces/booking-agents-sample/data/embedded_data.json',
            ]
            
            for path in paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        self._static_data = json.load(f)
                    print(f"✅ Loaded {len(self._static_data)} listings from static data")
                    return True
            
            print("⚠️ Static data file not found")
            return False
            
        except Exception as e:
            print(f"⚠️ Could not load static data: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected
    
    @property
    def has_vector_index(self) -> bool:
        """Check if vector search index is available."""
        return self._has_vector_index
    
    @property
    def has_static_data(self) -> bool:
        """Check if static data is loaded."""
        return self._static_data is not None and len(self._static_data) > 0
    
    @property
    def collection(self):
        """Get the MongoDB collection."""
        return self._collection
    
    def get_collection(self):
        """Get the MongoDB collection (method form for compatibility)."""
        return self._collection
    
    @property
    def static_data(self) -> List[Dict]:
        """Get static data (empty list if not loaded)."""
        return self._static_data or []
    
    def get_document_count(self) -> int:
        """Get count of documents in collection."""
        if self._is_connected and self._collection is not None:
            try:
                return self._collection.count_documents({})
            except Exception:
                return 0
        return len(self._static_data) if self._static_data else 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status for health checks."""
        return {
            "connected": self._is_connected,
            "has_vector_index": self._has_vector_index,
            "has_static_data": self.has_static_data,
            "document_count": self.get_document_count(),
        }


# Singleton database connection
db = DatabaseConnection()


async def initialize_database() -> DatabaseConnection:
    """Initialize database connection on startup (async for FastAPI lifespan)."""
    db.connect()
    if not db.is_connected:
        db.load_static_data()
    return db


def get_database() -> DatabaseConnection:
    """Get the database connection instance."""
    return db


def get_database_status() -> Dict[str, Any]:
    """Get database status for health checks."""
    return db.get_status()


def load_static_data() -> List[Dict]:
    """Load and return static data."""
    if not db.has_static_data:
        db.load_static_data()
    return db.static_data
