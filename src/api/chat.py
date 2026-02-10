"""
Chat Module - RAG Pattern Implementation
=========================================

Module 2 Exercise: Build a Retrieval-Augmented Generation chat system.

You'll implement:
- Session-based chat history (Step 2)
- Prompt templates for rephrasing and context (Step 3)
- Context formatting for the LLM (Step 4)
- The full RAG pipeline function (Step 5)

Follow the exercises in exercises/Module-02.md to fill in each TODO.
If you get stuck, check solutions/chat_solution.py for the complete code.
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
# Step 2: Chat History Management
# =============================================================================
# TODO: Implement the ChatHistory class.
#
# This class stores messages for a single conversation session.
# Each message is a dict with "role" ("user" or "assistant") and "content".
#
# Requirements:
#   - __init__: accept max_messages (default 20), store an empty list
#   - add_user_message(content): append {"role": "user", "content": content}
#   - add_assistant_message(content): append {"role": "assistant", "content": content}
#   - _trim(): if list exceeds max_messages, keep only the last N
#   - get_messages(): return a copy of the messages list
#   - get_formatted_history(): return a string like "User: ...\nAssistant: ..."
#     for the last 10 messages (used in prompts). Return "No previous conversation."
#     if empty.
#   - clear(): reset the messages list

class ChatHistory:
    """In-memory chat history manager per session."""
    pass  # TODO: Replace with your implementation


# Session-based history storage — maps session_id to ChatHistory
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
# Step 3: Prompt Templates
# =============================================================================
# TODO: Write two prompt template strings and one fallback string.
#
# REPHRASE_PROMPT — Given chat history and a follow-up question, rephrase it
#   into a standalone search query. Must contain {chat_history} and {question}.
#
# CONTEXT_PROMPT — System prompt for the AI assistant. Include guidelines for
#   how to respond (only use provided listings, be concise, etc.).
#   Must contain {context} and {question}.
#
# FALLBACK_RESPONSE — A static message returned when the LLM is unavailable
#   (e.g., no API key). Tell the user they can still browse listings.

REPHRASE_PROMPT = ""  # TODO: Write your rephrase prompt

CONTEXT_PROMPT = ""  # TODO: Write your context/system prompt

FALLBACK_RESPONSE = ""  # TODO: Write your fallback message


# =============================================================================
# LangChain LLM Setup (provided — no changes needed)
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
# Step 4: Context Formatting
# =============================================================================
# TODO: Implement format_listings_for_context().
#
# This function takes a list of SearchResult objects and builds a readable
# string that the LLM uses as its "knowledge base" for answering questions.
#
# Each SearchResult has:
#   - result.listing  (a Listing model with name, price, property_type,
#                       bedrooms, beds, amenities, description, etc.)
#   - result.score    (similarity score from vector search)
#
# Format each listing like:
#   1. Listing Name
#      Price: $120/night
#      Type: Apartment
#      Bedrooms: 2 | Beds: 3
#      Amenities: Wifi, Kitchen, ...
#      Description: (first 200 chars)...
#      Similarity Score: 0.87
#
# Return "No listings available matching the search criteria." if empty.

def format_listings_for_context(results: List[SearchResult]) -> str:
    """Format search results as context for the LLM."""
    pass  # TODO: Replace with your implementation


def format_listings_simple(results: List[SearchResult]) -> str:
    """Simple format for fallback responses (provided — no changes needed)."""
    if not results:
        return "No listings found."
    
    lines = []
    for i, result in enumerate(results[:3], 1):
        listing = result.listing
        lines.append(f"{i}. {listing.name} - ${listing.price:.0f}/night")
    
    return "\n".join(lines)


# =============================================================================
# Step 5: RAG Chat Function
# =============================================================================
# TODO: Implement generate_chat_response().
#
# This is the core RAG pipeline. It should:
#   1. Get the session history and LLM
#   2. Add the user's message to history
#   3. If no LLM available, return FALLBACK_RESPONSE
#   4. Rephrase the question using REPHRASE_PROMPT + chat history
#      (use ChatPromptTemplate.from_template and chain with llm)
#   5. Search for listings using the rephrased query
#      (call search_listings(query=..., limit=5))
#   6. Format the search results as context
#   7. Generate the final response using CONTEXT_PROMPT + context
#   8. Add the assistant's response to history
#   9. Return the response text
#
# On error, fall back to returning simple search results without the LLM.
#
# Important: Use ainvoke() for async LangChain calls.

async def generate_chat_response(
    message: str,
    session_id: str = "default"
) -> str:
    """
    Generate a chat response using RAG pattern.
    
    Args:
        message: User's message
        session_id: Session ID for conversation tracking
    
    Returns:
        AI-generated response string
    """
    # Import here to avoid circular imports
    from .search import search_listings
    
    pass  # TODO: Replace with your implementation
