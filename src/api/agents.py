"""
Multi-Agent System for Booking Search
=====================================

Module 3 Exercise: Build a LangGraph-based multi-agent system.

You'll implement:
- Shared agent state definition (Step 2)
- Agent tools for filtering and recommendations (Step 3)
- Specialized agent nodes: supervisor, search, filter, recommend, respond (Step 4)
- LangGraph workflow connecting agents (Step 5)
- The public run_agent_query function (Step 6)

Follow the exercises in exercises/Module-03.md to fill in each TODO.
If you get stuck, check solutions/agents_solution.py for the complete code.
"""

import json
import logging
import operator
from typing import TypedDict, Annotated, Literal, Optional, List, Dict, Any
from dataclasses import dataclass

from .config import settings
from .models import Listing

logger = logging.getLogger(__name__)

# Check if LangGraph is available
try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available - multi-agent features disabled")


# ============================================================================
# Step 2: Agent State Definition
# ============================================================================
# TODO: Define the AgentState TypedDict.
#
# This is the shared state passed between every agent in the graph.
# Each agent reads from and writes to this state.
#
# Required fields:
#   - messages:        Annotated[List[BaseMessage], operator.add]
#                      — conversation message history (uses operator.add
#                        so returning [new_msg] appends instead of replacing)
#   - user_query:      str                      — the user's original query
#   - search_results:  List[Dict[str, Any]]     — listings found by search
#   - filters:         Dict[str, Any]           — extracted filter criteria
#   - recommendations: List[Dict[str, Any]]     — ranked/recommended listings
#   - next_agent:      str                      — which agent to run next
#   - final_response:  str                      — the response to send to the user

class AgentState(TypedDict):
    """Shared state passed between agents in the graph."""
    pass  # TODO: Replace with your field definitions


# ============================================================================
# Step 3: Agent Tools
# ============================================================================
# TODO: Implement the two agent tools below.
#
# These are LangChain @tool-decorated functions that agents can invoke.
# They perform the actual data operations (filter, rank).

# 3a. apply_filters
# -------------------
# TODO: Implement apply_filters as a @tool.
#
# This tool takes a list of listing dicts and optional filter parameters,
# then returns only the listings that pass all filters.
#
# Parameters:
#   - listings:      List[Dict[str, Any]]      — the listings to filter
#   - max_price:     Optional[float]           — maximum price per night
#   - property_type: Optional[str]             — property type substring match
#   - min_bedrooms:  Optional[int]             — minimum number of bedrooms
#   - amenities:     Optional[List[str]]       — required amenities
#
# Filter logic:
#   - max_price:     keep listings where price <= max_price
#   - property_type: keep listings where property_type contains the string (case-insensitive)
#   - min_bedrooms:  keep listings where bedrooms >= min_bedrooms
#   - amenities:     keep listings where all required amenities are present (case-insensitive)

# Uncomment and implement:
# @tool
# def apply_filters(...) -> List[Dict[str, Any]]:
#     pass


# 3b. get_recommendations
# -------------------------
# TODO: Implement get_recommendations as a @tool.
#
# This tool takes a list of listings and a preference string,
# then returns the top 5 ranked by the preference strategy.
#
# Parameters:
#   - listings:   List[Dict[str, Any]]
#   - preference: str — one of "budget", "quality", or "balanced"
#
# Ranking strategies:
#   - "budget":   sort by price ascending (cheapest first)
#   - "quality":  sort by score descending (most relevant first)
#   - "balanced": rank = score - (price / 500.0), sort descending

# Uncomment and implement:
# @tool
# def get_recommendations(...) -> List[Dict[str, Any]]:
#     pass


# ============================================================================
# LLM Setup (provided — no changes needed)
# ============================================================================

def create_llm():
    """Create the LLM for agent use."""
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0.7,
    )


# ============================================================================
# Step 4: Agent Nodes
# ============================================================================
# TODO: Implement the five agent node functions below.
#
# Each node is an async function that takes an AgentState and returns a dict
# containing only the state fields that changed. For the messages field,
# return a list of new messages — they will be appended automatically
# (thanks to the operator.add annotation on AgentState.messages).

# 4a. supervisor_node
# ---------------------
# TODO: Implement supervisor_node(state).
#
# The supervisor analyzes the user query and decides whether to run
# the full search pipeline or respond directly.
#
# It should:
#   1. Call create_llm() to get an LLM instance
#   2. Build a system prompt that describes the two routing options:
#      - "search":  user wants to find, filter, or get recommendations for listings
#      - "respond": user is making small talk or asking a non-search question
#   3. Ask the LLM to respond with ONLY one word
#   4. Validate the response — if not "search" or "respond", default to "search"
#   5. Return a dict with:
#      - 'next_agent': the chosen route
#      - 'messages': [AIMessage with routing info]

async def supervisor_node(state: AgentState) -> dict:
    """Supervisor agent that routes queries to search pipeline or direct response."""
    pass  # TODO: Replace with your implementation


# 4b. search_node
# -----------------
# TODO: Implement search_node(state).
#
# The search agent finds relevant listings using vector search.
#
# It should:
#   1. Import search_listings from .search
#   2. Call search_listings(state['user_query'], limit=20)
#   3. Convert results to dicts: {**r.listing.model_dump(), 'score': r.score}
#   4. Return a dict with:
#      - 'search_results': the list of result dicts
#      - 'messages': [AIMessage with status]
#   5. Handle exceptions gracefully (empty results + error message)

async def search_node(state: AgentState) -> dict:
    """Search agent that finds relevant listings."""
    pass  # TODO: Replace with your implementation


# 4c. filter_node
# -----------------
# TODO: Implement filter_node(state).
#
# The filter agent extracts constraints from the query and applies them.
# Acts as a no-op when no filter constraints are detected.
#
# It should:
#   1. Call create_llm() to get an LLM instance
#   2. Use a system prompt to extract filter criteria as JSON from the user query
#      (fields: max_price, property_type, min_bedrooms, amenities)
#   3. Parse the JSON response (use json.loads())
#   4. If filters were extracted, call apply_filters with the search_results
#   5. If no filters (empty {}), pass results through unchanged
#   6. Return a dict with:
#      - 'filters': the parsed filter dict
#      - 'search_results': filtered (or unchanged) results
#      - 'messages': [AIMessage with status]
#   7. Handle JSON parse errors and other exceptions

async def filter_node(state: AgentState) -> dict:
    """Filter agent that applies constraints to results."""
    pass  # TODO: Replace with your implementation


# 4d. recommend_node
# --------------------
# TODO: Implement recommend_node(state).
#
# The recommendation agent ranks listings based on user preferences.
#
# It should:
#   1. Call create_llm() to get an LLM instance
#   2. Use a system prompt to determine the user's preference from the query
#      (respond with "budget", "quality", or "balanced")
#   3. Call get_recommendations with the search results and detected preference
#   4. Return a dict with:
#      - 'recommendations': the ranked list
#      - 'messages': [AIMessage with status]
#   5. On error, fall back to state['search_results'][:5]

async def recommend_node(state: AgentState) -> dict:
    """Recommendation agent that ranks and suggests listings."""
    pass  # TODO: Replace with your implementation


# 4e. respond_node
# ------------------
# TODO: Implement respond_node(state).
#
# The response agent generates the final user-facing message.
#
# It should:
#   1. Call create_llm() to get an LLM instance
#   2. Get recommendations (or fall back to search_results[:5])
#   3. If no results at all, return a "no results" message
#   4. Format the top 5 listings into a context string
#   5. Use a system prompt asking the LLM to generate a friendly,
#      concise booking assistant response (under 200 words)
#   6. Return a dict with:
#      - 'final_response': the generated response text
#   7. On error, fall back to the raw listings context

async def respond_node(state: AgentState) -> dict:
    """Response agent that generates the final user-facing response."""
    pass  # TODO: Replace with your implementation


# ============================================================================
# Step 5: Build the LangGraph Workflow
# ============================================================================
# TODO: Implement build_agent_graph().
#
# This function assembles all agent nodes into a LangGraph StateGraph.
#
# Graph structure:
#   [START] → [Supervisor] → "search"  → [Search] → [Filter] → [Recommend] → [Respond] → [END]
#                           → "respond" → [Respond] → [END]
#
# Steps:
#   1. Return None if LANGGRAPH_AVAILABLE is False
#   2. Create a StateGraph(AgentState)
#   3. Add all 5 nodes: supervisor, search, filter, recommend, respond
#   4. Set "supervisor" as the entry point
#   5. Add conditional edges from supervisor using a routing function
#      that reads state['next_agent'] and maps to:
#      {"search": "search", "respond": "respond"}
#   6. Add direct edges for the linear pipeline:
#      search→filter, filter→recommend, recommend→respond, respond→END
#   7. Compile and return the graph

def build_agent_graph():
    """Build the LangGraph agent workflow."""
    pass  # TODO: Replace with your implementation


# ============================================================================
# Step 6: Public Interface
# ============================================================================
# TODO: Implement run_agent_query() and is_multi_agent_available().
#
# These are the functions imported by main.py.

# Compiled graph (lazy initialization)
_agent_graph = None


def get_agent_graph():
    """Get the compiled agent graph, building it if necessary."""
    global _agent_graph
    if _agent_graph is None and LANGGRAPH_AVAILABLE:
        _agent_graph = build_agent_graph()
    return _agent_graph


# 6a. run_agent_query
# ----------------------
# TODO: Implement run_agent_query(query, session_id).
#
# This async function runs a query through the multi-agent system.
#
# It should:
#   1. Get the compiled graph via get_agent_graph()
#   2. If graph is None, fall back to simple RAG:
#      - Import generate_chat_response from .chat
#      - Return {"response": ..., "agent_path": ["fallback_rag"],
#                "search_results": [], "multi_agent": False}
#   3. Initialize the AgentState with the query and empty collections
#   4. Run the graph with await graph.ainvoke(initial_state)
#   5. Extract the agent path from routing messages in state['messages']
#   6. Format results: separate 'score' from listing data into
#      {"listing": {...}, "score": N} structure
#   7. Return a dict with: response, agent_path, search_results, multi_agent=True
#   8. On error, fall back to simple RAG (same as step 2)

async def run_agent_query(query: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Run a query through the multi-agent system.

    Args:
        query: User's natural language query
        session_id: Session identifier for conversation tracking

    Returns:
        Dictionary with response and metadata
    """
    pass  # TODO: Replace with your implementation


# 6b. is_multi_agent_available
# ------------------------------
# TODO: Implement is_multi_agent_available().
#
# Returns True if LangGraph is installed AND the graph compiled successfully.

def is_multi_agent_available() -> bool:
    """Check if multi-agent system is available."""
    return False  # TODO: Replace with your implementation
