"""
Multi-Agent System for Booking Search
=====================================

Module 3 Exercise: Enhance the multi-agent system with LLM intelligence.

The scaffold below is a WORKING multi-agent system that runs out of the box.
It uses hardcoded placeholder logic — your job is to replace the TODO blocks
with real LLM-powered implementations.

Exercises:
  1. Implement tool logic (apply_filters + get_recommendations)
  2. Add LLM routing + filter extraction (supervisor_node + filter_node)
  3. Add LLM ranking + response (recommend_node + respond_node)

Each exercise is independently testable — the system works before, during,
and after you fill in the TODOs. It just gets smarter as you go.

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
# Agent State (provided — no changes needed)
# ============================================================================

class AgentState(TypedDict):
    """
    Shared state passed between agents in the graph.

    The `messages` field uses operator.add so that returning
    {'messages': [new_msg]} appends rather than replaces.
    All other fields use replace semantics (last write wins).
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    search_results: List[Dict[str, Any]]
    filters: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    next_agent: str
    final_response: str


# ============================================================================
# Exercise 1: Agent Tools
# ============================================================================
# These tools perform the data operations that agents invoke.
# Currently they use passthrough logic — your job is to add
# the real filter conditions and ranking strategies.

@tool
def apply_filters(
    listings: List[Dict[str, Any]],
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    min_bedrooms: Optional[int] = None,
    amenities: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Apply filters to a list of listings.

    Args:
        listings: List of listing dictionaries
        max_price: Maximum price filter
        property_type: Property type substring match (e.g. "Apartment", "House")
        min_bedrooms: Minimum number of bedrooms
        amenities: Required amenities (e.g. ["Wifi", "Kitchen"])

    Returns:
        Filtered list of listings
    """
    filtered = listings.copy()

    # --- TODO: Exercise 1a -------------------------------------------------
    # Add filter logic here. For each parameter that is not None,
    # remove listings that don't match:
    #
    #   if max_price is not None:
    #       keep listings where price <= max_price
    #
    #   if property_type:
    #       keep listings where property_type contains the string (case-insensitive)
    #
    #   if min_bedrooms is not None:
    #       keep listings where bedrooms >= min_bedrooms
    #
    #   if amenities:
    #       keep listings where ALL required amenities are present (case-insensitive)
    #
    # Without this, all listings pass through unfiltered.
    # --- END TODO -----------------------------------------------------------

    return filtered


@tool
def get_recommendations(
    listings: List[Dict[str, Any]],
    preference: str = "balanced"
) -> List[Dict[str, Any]]:
    """
    Get personalized recommendations from listings.

    Args:
        listings: List of listing dictionaries
        preference: User preference - "budget", "quality", or "balanced"

    Returns:
        Sorted/ranked list of recommended listings (top 5)
    """
    if not listings:
        return []

    # --- TODO: Exercise 1b -------------------------------------------------
    # Implement three ranking strategies and return the top 5:
    #
    #   if preference == "budget":
    #       sort by price ascending (cheapest first)
    #
    #   elif preference == "quality":
    #       sort by score descending (highest relevance first)
    #
    #   else:  # "balanced"
    #       rank = score - (price / 500.0), sort descending
    #
    # Without this, returns the first 5 listings unranked.
    # --- END TODO -----------------------------------------------------------

    return listings[:5]


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
# Agent Nodes
# ============================================================================
# Each node is an async function that takes AgentState and returns a dict
# containing only the fields that changed. The graph merges these into
# the shared state automatically.
#
# Exercises 2 and 3 ask you to replace the hardcoded placeholder logic
# with LLM-powered implementations. The nodes work before you make changes —
# they just use simple defaults instead of AI reasoning.


# --- Exercise 2a: supervisor_node -----------------------------------------

async def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor agent that routes queries to the search pipeline or direct response.

    Routes to:
    - "search": The user wants to find, filter, or get recommendations for listings
    - "respond": The user is making small talk or asking a non-search question
    """

    # --- TODO: Exercise 2a -------------------------------------------------
    # Replace the hardcoded routing below with an LLM-based decision.
    #
    # Steps:
    #   1. Call create_llm() to get an LLM instance
    #   2. Build a system prompt explaining the two routing options:
    #      - "search": user wants to find, filter, or get recommendations
    #      - "respond": user is making small talk, saying thanks, etc.
    #   3. Send [SystemMessage(prompt), HumanMessage(state['user_query'])]
    #      to the LLM with: response = await llm.ainvoke(messages)
    #   4. Parse: next_agent = response.content.strip().lower()
    #   5. Validate: if next_agent not in ('search', 'respond'), default to 'search'
    #
    # Current placeholder: always routes to "search"
    next_agent = "search"
    # --- END TODO -----------------------------------------------------------

    return {
        'next_agent': next_agent,
        'messages': [AIMessage(content=f"Routing to: {next_agent}")]
    }


# --- search_node (provided — no changes needed) ---------------------------

async def search_node(state: AgentState) -> dict:
    """
    Search agent that finds relevant listings using vector search.
    This node is fully implemented — no TODO needed.
    """
    try:
        from .search import search_listings

        results = search_listings(state['user_query'], limit=20)
        search_results = [
            {**r.listing.model_dump(), 'score': r.score}
            for r in results
        ]
        return {
            'search_results': search_results,
            'messages': [AIMessage(content=f"Found {len(results)} listings")]
        }

    except Exception as e:
        logger.error(f"Search agent error: {e}")
        return {
            'search_results': [],
            'messages': [AIMessage(content=f"Search error: {str(e)}")]
        }


# --- Exercise 2b: filter_node ---------------------------------------------

async def filter_node(state: AgentState) -> dict:
    """
    Filter agent that extracts constraints from the query and applies them.
    Acts as a no-op when no filter constraints are detected.
    """

    # --- TODO: Exercise 2b -------------------------------------------------
    # Replace the hardcoded empty filters below with LLM-based extraction.
    #
    # Steps:
    #   1. Call create_llm() to get an LLM instance
    #   2. Build a system prompt asking the LLM to extract EXPLICIT filter
    #      criteria as JSON. ONLY extract filters the user specifically states
    #      as constraints — do NOT infer from general search terms.
    #      Fields: max_price (number), property_type (string, only if user
    #      says "only" or explicitly constrains), min_bedrooms (integer),
    #      amenities (array of strings).
    #      Tell the LLM: when in doubt, respond with {}
    #   3. Send [SystemMessage(prompt), HumanMessage(state['user_query'])]
    #      to the LLM with: response = await llm.ainvoke(messages)
    #   4. Parse: filters = json.loads(response.content)
    #   5. If filters is not empty, apply them:
    #      filtered = apply_filters.invoke({'listings': state['search_results'], **filters})
    #      Return {'filters': filters, 'search_results': filtered, 'messages': [...]}
    #   6. If filters is empty {}, return {'filters': {}, 'messages': [...]}
    #   7. Wrap in try/except for JSON parse errors
    #
    # Current placeholder: no filters extracted (passthrough)
    filters = {}
    # --- END TODO -----------------------------------------------------------

    if filters:
        filtered = apply_filters.invoke({
            'listings': state['search_results'],
            **filters
        })
        return {
            'filters': filters,
            'search_results': filtered,
            'messages': [AIMessage(content=f"Applied filters, {len(filtered)} results remain")]
        }
    else:
        return {
            'filters': {},
            'messages': [AIMessage(content="No filters to apply")]
        }


# --- Exercise 3a: recommend_node ------------------------------------------

async def recommend_node(state: AgentState) -> dict:
    """
    Recommendation agent that ranks listings based on user preferences.
    """

    # --- TODO: Exercise 3a -------------------------------------------------
    # Replace the hardcoded preference below with LLM-based detection.
    #
    # Steps:
    #   1. Call create_llm() to get an LLM instance
    #   2. Build a system prompt asking the LLM to determine the user's
    #      preference. It should respond with ONLY one word:
    #        - "budget": user prioritizes low prices
    #        - "quality": user prioritizes high ratings/quality
    #        - "balanced": user wants a good balance
    #   3. Send [SystemMessage(prompt)] to the LLM
    #   4. Parse: preference = response.content.strip().lower()
    #   5. Validate: if not in ('budget', 'quality', 'balanced'), default to 'balanced'
    #
    # Current placeholder: always uses "balanced"
    preference = "balanced"
    # --- END TODO -----------------------------------------------------------

    try:
        recs = get_recommendations.invoke({
            'listings': state['search_results'],
            'preference': preference
        })
        return {
            'recommendations': recs,
            'messages': [AIMessage(content=f"Generated {len(recs)} recommendations ({preference})")]
        }
    except Exception as e:
        logger.error(f"Recommendation agent error: {e}")
        return {
            'recommendations': state['search_results'][:5],
            'messages': [AIMessage(content="Fallback recommendations")]
        }


# --- Exercise 3b: respond_node --------------------------------------------

async def respond_node(state: AgentState) -> dict:
    """
    Response agent that generates the final user-facing response.
    """
    # Get recommendations (or fall back to search results)
    recs = state.get('recommendations', []) or state.get('search_results', [])[:5]

    if not recs:
        return {
            'final_response': "I couldn't find any listings matching your criteria. Try broadening your search!"
        }

    # Format listings for context (used by both placeholder and LLM response)
    listings_context = "\n".join([
        f"- {r.get('name', 'Unknown')}: {r.get('description', '')[:100]}... "
        f"(Type: {r.get('property_type', 'N/A')}, Bedrooms: {r.get('bedrooms', 'N/A')}, "
        f"Price: ${r.get('price', 'N/A')}/night)"
        for r in recs[:5]
    ])

    # --- TODO: Exercise 3b -------------------------------------------------
    # Replace the raw listings response below with an LLM-generated one.
    #
    # Steps:
    #   1. Call create_llm() to get an LLM instance
    #   2. Build a system prompt telling the LLM to be a friendly booking
    #      assistant. Include listings_context as the search results.
    #      Ask it to mention 2-3 top options and keep under 200 words.
    #   3. Send [SystemMessage(prompt), HumanMessage(state['user_query'])]
    #      to the LLM with: response = await llm.ainvoke(messages)
    #   4. Return {'final_response': response.content}
    #   5. On error, fall back to the raw listings_context string
    #
    # Current placeholder: returns the raw listings context
    return {'final_response': f"Here are some options I found:\n\n{listings_context}"}
    # --- END TODO -----------------------------------------------------------


# ============================================================================
# Graph Builder (provided — no changes needed)
# ============================================================================

def build_agent_graph():
    """
    Build the LangGraph agent workflow.

    Graph Structure:

        [START] -> [Supervisor] -> "search"  -> [Search] -> [Filter] -> [Recommend] -> [Respond] -> [END]
                                -> "respond" -> [Respond] -> [END]

    The supervisor decides whether the query needs the full search pipeline
    or can be answered directly (e.g., greetings, non-search questions).
    The filter agent is a no-op when no constraints are detected.
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("search", search_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("recommend", recommend_node)
    workflow.add_node("respond", respond_node)

    # Define routing logic
    def route_from_supervisor(state: AgentState) -> str:
        return state.get('next_agent', 'search')

    # Set entry point and conditional routing
    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "search": "search",
            "respond": "respond",
        }
    )

    # Linear pipeline: search -> filter -> recommend -> respond -> END
    workflow.add_edge("search", "filter")
    workflow.add_edge("filter", "recommend")
    workflow.add_edge("recommend", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()


# ============================================================================
# Public Interface (provided — no changes needed)
# ============================================================================

def get_agent_graph():
    """
    Build a fresh agent graph on each call.

    Rebuilding ensures that code changes to node functions take effect
    immediately when using uvicorn --reload during the workshop.
    """
    if not LANGGRAPH_AVAILABLE:
        return None
    return build_agent_graph()


async def run_agent_query(query: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Run a query through the multi-agent system.

    Args:
        query: User's natural language query
        session_id: Session identifier for conversation tracking

    Returns:
        Dictionary with response and metadata
    """
    graph = get_agent_graph()

    if graph is None:
        # Fallback to simple RAG
        from .chat import generate_chat_response
        response = await generate_chat_response(query, session_id)
        return {
            "response": response,
            "agent_path": ["fallback_rag"],
            "search_results": [],
            "multi_agent": False
        }

    try:
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "search_results": [],
            "filters": {},
            "recommendations": [],
            "next_agent": "",
            "final_response": ""
        }

        # Run the graph
        final_state = await graph.ainvoke(initial_state)

        # Extract agent path from messages
        agent_path = [
            msg.content.replace("Routing to: ", "")
            for msg in final_state['messages']
            if isinstance(msg, AIMessage) and msg.content.startswith("Routing to:")
        ]

        # Format results with score separated from listing data
        results = final_state.get('recommendations', [])[:10]
        search_results = []
        for r in results:
            result_copy = r.copy()
            score = result_copy.pop('score', 1.0)
            search_results.append({
                'listing': result_copy,
                'score': score
            })

        return {
            "response": final_state['final_response'],
            "agent_path": agent_path,
            "search_results": search_results,
            "multi_agent": True
        }

    except Exception as e:
        logger.error(f"Agent graph error: {e}")
        # Fallback
        from .chat import generate_chat_response
        response = await generate_chat_response(query, session_id)
        return {
            "response": response,
            "agent_path": ["error_fallback"],
            "search_results": [],
            "multi_agent": False,
            "error": str(e)
        }


def is_multi_agent_available() -> bool:
    """Check if multi-agent system is available."""
    return LANGGRAPH_AVAILABLE and get_agent_graph() is not None
