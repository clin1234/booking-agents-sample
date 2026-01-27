"""
Configuration module for the Booking Search API.
Handles environment variables with sensible defaults for Codespaces.
"""

import os
import re
from functools import lru_cache
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class Settings:
    """Application settings loaded from environment variables."""
    
    # DocumentDB Configuration
    DOCUMENTDB_CONNECTION_STRING: str = os.getenv(
        "DOCUMENTDB_CONNECTION_STRING",
        "mongodb://admin:password123@localhost:10260/?tls=true&tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256"
    )
    DOCUMENTDB_HOST: str = os.getenv("DOCUMENTDB_HOST", "localhost")
    DOCUMENTDB_PORT: int = int(os.getenv("DOCUMENTDB_PORT", "10260"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "listings")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
    
    # Azure OpenAI Configuration (optional)
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-35-turbo")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS - Base origins
    _BASE_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Vector search configuration
    VECTOR_DIMENSIONS: int = 1536  # OpenAI text-embedding-3-small dimensions
    VECTOR_INDEX_NAME: str = "vectorSearchIndex"
    
    # Search defaults
    DEFAULT_SEARCH_LIMIT: int = 10
    DEFAULT_SEARCH_RADIUS_MILES: float = 30.0
    EARTH_RADIUS_MILES: float = 3963.2
    
    # Default location (Denver, CO)
    DEFAULT_LATITUDE: float = 39.7392
    DEFAULT_LONGITUDE: float = -104.9903
    
    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())
    
    @property
    def is_codespaces(self) -> bool:
        """Check if running in GitHub Codespaces."""
        return bool(os.getenv("CODESPACES") or os.getenv("GITHUB_CODESPACE_TOKEN"))
    
    @property
    def codespaces_name(self) -> Optional[str]:
        """Get Codespaces name for CORS."""
        return os.getenv("CODESPACE_NAME")
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins including Codespaces URLs if applicable."""
        origins = self._BASE_CORS_ORIGINS.copy()
        
        # Add Codespaces-specific origins
        if self.is_codespaces and self.codespaces_name:
            # Frontend typically runs on port 3000
            origins.append(f"https://{self.codespaces_name}-3000.app.github.dev")
            # Backend on port 8000
            origins.append(f"https://{self.codespaces_name}-8000.app.github.dev")
            # Preview URLs
            origins.append(f"https://{self.codespaces_name}-3000.preview.app.github.dev")
            origins.append(f"https://{self.codespaces_name}-8000.preview.app.github.dev")
        
        # Also add wildcard patterns for flexibility
        origins.extend([
            "https://*.app.github.dev",
            "https://*.preview.app.github.dev",
        ])
        
        return origins
    
    @property
    def default_location(self) -> tuple:
        """Return default location as (longitude, latitude) for MongoDB."""
        return (self.DEFAULT_LONGITUDE, self.DEFAULT_LATITUDE)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export a singleton instance
settings = get_settings()
