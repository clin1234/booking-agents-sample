"""
Chat Module - RAG Pattern Implementation
=========================================

Implements Module 2 of the workshop: Retrieval-Augmented Generation.

Features:
- Session-based chat history
- Question rephrasing for context awareness
- Vector search for relevant listings
- LangChain for LLM integration
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .config import settings
from .models import Listing, SearchResult

logger = logging.getLogger(__name__)


# =============================================================================
# Chat History Management
# =============================================================================

class ChatHistory:
    """In-memory chat history manager per session."""
    
    def __init__(self, max_messages: int = 20):
        self._messages: List[Dict[str, str]] = []
        self._max_messages = max_messages
    
    def add_user_message(self, content: str):
        """Add a user message to history."""
        self._messages.append({"role": "user", "content": content})
        self._trim()
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to history."""
        self._messages.append({"role": "assistant", "content": content})
        self._trim()
    
    def _trim(self):
        """Keep only the last N messages."""
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages."""
        return self._messages.copy()
    
    def get_formatted_history(self) -> str:
        """Get history formatted as string for prompts."""
        if not self._messages:
            return "No previous conversation."
        
        lines = []
        for msg in self._messages[-10:]:  # Last 10 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    
    def clear(self):
        """Clear all history."""
        self._messages = []


# Session-based history storage
_session_histories: Dict[str, ChatHistory] = defaultdict(ChatHistory)


def get_session_history(session_id: str) -> ChatHistory:
    """Get chat history for a session."""
    return _session_histories[session_id]


def get_chat_history(session_id: str) -> List[Dict[str, str]]:
    """Get chat history messages for API response."""
    return _session_histories[session_id].get_messages()


def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in _session_histories:
        _session_histories[session_id].clear()


# =============================================================================
# Prompts (matching Module 2 exercises)
# =============================================================================

REPHRASE_PROMPT = """Given the following conversation history and a follow-up question, 
rephrase the follow-up question to be a standalone search query that can be used 
to search for vacation rental listings.

Chat History:
{chat_history}

Follow-up Question: {question}

Standalone Search Query:"""

CONTEXT_PROMPT = """You are a friendly AI assistant helping users find vacation rental listings.
Your responses should be helpful, conversational, and based ONLY on the provided listings.

Guidelines:
- Only recommend listings that appear in the context below
- Mention specific details like price, bedrooms, amenities when relevant
- If no listings match the user's needs, politely say so
- Keep responses concise (under 150 words)
- Be enthusiastic but not pushy
- Ask follow-up questions to better understand user preferences

Available Listings:
{context}

User Question: {question}

Assistant Response:"""

FALLBACK_RESPONSE = """I don't have access to the AI chat features right now. 
This could be because:
- OpenAI API key is not configured
- The chat service encountered an error

You can still:
- Browse the listings shown on the map
- Use the search feature to find listings
- Complete Module 2 of the workshop to enable AI-powered chat!

Is there anything else I can help with?"""


# =============================================================================
# LangChain LLM Setup
# =============================================================================

def get_llm() -> Optional[ChatOpenAI]:
    """Get LangChain LLM if OpenAI is configured."""
    if not settings.has_openai_key:
        logger.warning("OpenAI API key not configured - chat will use fallback")
        return None
    
    try:
        return ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        return None


# =============================================================================
# Context Formatting
# =============================================================================

def format_listings_for_context(results: List[SearchResult]) -> str:
    """
    Format search results as context for the LLM.
    Matches the format expected in Module 2 exercises.
    """
    if not results:
        return "No listings available matching the search criteria."
    
    lines = []
    for i, result in enumerate(results, 1):
        listing = result.listing
        
        # Format amenities (first 5)
        amenities_str = ", ".join(listing.amenities[:5]) if listing.amenities else "Not specified"
        
        # Truncate description
        desc = listing.description or ""
        if len(desc) > 200:
            desc = desc[:200] + "..."
        
        lines.append(f"""
{i}. {listing.name}
   Price: ${listing.price:.0f}/night
   Type: {listing.property_type or 'Not specified'}
   Bedrooms: {listing.bedrooms or 'N/A'} | Beds: {listing.beds or 'N/A'}
   Amenities: {amenities_str}
   Description: {desc}
   Similarity Score: {result.score:.2f}
""")
    
    return "\n".join(lines)


def format_listings_simple(results: List[SearchResult]) -> str:
    """Simple format for fallback responses."""
    if not results:
        return "No listings found."
    
    lines = []
    for i, result in enumerate(results[:3], 1):
        listing = result.listing
        lines.append(f"{i}. {listing.name} - ${listing.price:.0f}/night")
    
    return "\n".join(lines)


# =============================================================================
# RAG Chat Function
# =============================================================================

async def generate_chat_response(
    message: str,
    session_id: str = "default"
) -> str:
    """
    Generate a chat response using RAG pattern.
    
    This is the main function implementing Module 2's RAG pipeline:
    1. Rephrase question considering chat history
    2. Search for relevant listings
    3. Generate response with listing context
    
    Args:
        message: User's message
        session_id: Session ID for conversation tracking
    
    Returns:
        AI-generated response string
    """
    # Import here to avoid circular imports
    from .search import search_listings
    
    history = get_session_history(session_id)
    llm = get_llm()
    
    # Add user message to history
    history.add_user_message(message)
    
    # If LLM not available, return fallback
    if not llm:
        return FALLBACK_RESPONSE
    
    try:
        # Step 1: Rephrase the question considering chat history
        # This makes follow-up questions work (e.g., "What about parking?")
        rephrase_prompt = ChatPromptTemplate.from_template(REPHRASE_PROMPT)
        rephrase_chain = rephrase_prompt | llm
        
        rephrased = await rephrase_chain.ainvoke({
            "chat_history": history.get_formatted_history(),
            "question": message
        })
        search_query = rephrased.content.strip()
        
        logger.info(f"Rephrased query: '{message}' -> '{search_query}'")
        
        # Step 2: Search for relevant listings using vector/text search
        results = search_listings(query=search_query, limit=5)
        
        # Step 3: Generate response with context
        context = format_listings_for_context(results)
        
        context_prompt = ChatPromptTemplate.from_template(CONTEXT_PROMPT)
        context_chain = context_prompt | llm
        
        response = await context_chain.ainvoke({
            "context": context,
            "question": message
        })
        
        response_text = response.content
        
        # Add assistant response to history
        history.add_assistant_message(response_text)
        
        return response_text
        
    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        
        # Fall back to search without LLM
        from .search import search_listings
        results = search_listings(query=message, limit=5)
        
        if results:
            listings_text = format_listings_simple(results)
            response_text = f"I found {len(results)} listings that might interest you:\n\n{listings_text}\n\nWould you like more details about any of these?"
        else:
            response_text = "I couldn't find any listings matching your criteria. Try adjusting your search terms."
        
        history.add_assistant_message(response_text)
        return response_text
