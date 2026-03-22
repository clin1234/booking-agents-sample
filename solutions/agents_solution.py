"""
Multi-Agent System for Booking Search (SOLUTION)
==================================================

This is the complete solution for Module 3 of the workshop.
If you get stuck, compare your src/api/agents.py with this file.

To use this solution: copy the contents into src/api/agents.py
(do NOT run this file directly from the solutions/ folder).

Implements: LangGraph-based multi-agent system for intelligent
booking search and recommendations.

Agents:
- Supervisor: Routes queries to the search pipeline or direct response
- Search Agent: Handles venue/listing searches
- Filter Agent: Applies filters and refinements
- Recommendation Agent: Provides personalized suggestions
- Response Agent: Generates the final user-facing response

Graph Structure:
    [START] → [Supervisor] → "search"  → [Search] → [Filter] → [Recommend] → [Respond] → [END]
                           → "respond" → [Respond] → [END]

The system gracefully degrades if LangGraph is not available,
falling back to direct RAG responses.
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
# Agent State Definition
# ============================================================================

class AgentState(TypedDict):
    """Shared state passed between agents in the graph."""
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    search_results: List[Dict[str, Any]]
    filters: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    next_agent: str
    final_response: str


# ============================================================================
# Agent Tools
# ============================================================================

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

    if max_price is not None:
        filtered = [l for l in filtered if l.get('price', float('inf')) <= max_price]

    if property_type:
        filtered = [l for l in filtered if property_type.lower() in l.get('property_type', '').lower()]

    if min_bedrooms is not None:
        filtered = [l for l in filtered if (l.get('bedrooms') or 0) >= min_bedrooms]

    if amenities:
        def has_amenities(listing):
            listing_amenities = [a.lower() for a in listing.get('amenities', [])]
            return all(a.lower() in listing_amenities for a in amenities)
        filtered = [l for l in filtered if has_amenities(l)]

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
        Sorted/ranked list of recommended listings
    """
    if not listings:
        return []

    if preference == "budget":
        # Sort by price, lowest first
        return sorted(listings, key=lambda x: x.get('price', float('inf')))[:5]
    elif preference == "quality":
        # Sort by search relevance score, highest first
        return sorted(listings, key=lambda x: x.get('score', 0), reverse=True)[:5]
    else:
        # Balanced: combine relevance score and price
        def rank(l):
            relevance = l.get('score', 0.5)
            price = l.get('price', 100)
            # Normalize: higher is better
            return relevance - (price / 500.0)
        return sorted(listings, key=rank, reverse=True)[:5]


# ============================================================================
# LLM Setup
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

async def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor agent that routes queries to the search pipeline or direct response.

    Routes to:
    - "search": The user wants to find, filter, or get recommendations for listings
    - "respond": The user is making small talk or asking a non-search question
    """
    llm = create_llm()

    system_prompt = """You are a supervisor agent for a booking search system.

Analyze the user's query and decide the next step:

- "search": The user wants to find, filter, or get recommendations for listings
  (e.g., "find apartments", "2-bedroom under $200", "best places near downtown")
- "respond": The user is making small talk, saying thanks, or asking a non-search question
  (e.g., "hello", "thanks", "what can you do?")

Respond with ONLY one word: search or respond"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['user_query'])
    ]

    response = await llm.ainvoke(messages)
    next_agent = response.content.strip().lower()

    # Validate response — default to search for any listing-related query
    if next_agent not in ('search', 'respond'):
        next_agent = 'search'

    return {
        'next_agent': next_agent,
        'messages': [AIMessage(content=f"Routing to: {next_agent}")]
    }


async def search_node(state: AgentState) -> dict:
    """
    Search agent that finds relevant listings using vector search.
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


async def filter_node(state: AgentState) -> dict:
    """
    Filter agent that extracts constraints from the query and applies them.
    Acts as a no-op when no filter constraints are detected.
    """
    llm = create_llm()

    # Extract filter intent from query
    system_prompt = """Extract EXPLICIT filter criteria from the user query.
ONLY extract filters that the user specifically states as constraints.
Do NOT infer filters from general search terms.

Rules:
- "under $200" or "less than $200" → max_price: 200
- "2 bedroom" or "at least 3 bedrooms" → min_bedrooms: N
- "with wifi and parking" → amenities: ["Wifi", "Parking"]
- "apartment" as a search term (e.g. "show me apartments") → do NOT filter, respond with {}
- "apartment" as a constraint (e.g. "only apartments") → property_type: "Apartment"

Respond in JSON format with these optional fields:
- max_price: number (maximum price per night)
- property_type: string (ONLY if user says "only" or explicitly constrains type)
- min_bedrooms: integer (minimum number of bedrooms)
- amenities: array of strings (e.g. ["Wifi", "Kitchen", "Free parking"])

Example: {"max_price": 200, "min_bedrooms": 2}

When in doubt, respond with: {}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['user_query'])
    ]

    try:
        response = await llm.ainvoke(messages)
        filters = json.loads(response.content)

        # Apply filters (no-op if filters is empty)
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

    except Exception as e:
        logger.error(f"Filter agent error: {e}")
        return {
            'messages': [AIMessage(content=f"Filter error: {str(e)}")]
        }


async def recommend_node(state: AgentState) -> dict:
    """
    Recommendation agent that ranks listings based on user preferences.
    """
    llm = create_llm()

    # Determine preference from query
    system_prompt = """Analyze the user query and determine their preference.

Respond with ONLY one word:
- "budget": User prioritizes low prices
- "quality": User prioritizes high ratings/quality
- "balanced": User wants a good balance

Query: {query}"""

    messages = [
        SystemMessage(content=system_prompt.format(query=state['user_query'])),
    ]

    try:
        response = await llm.ainvoke(messages)
        preference = response.content.strip().lower()
        if preference not in ['budget', 'quality', 'balanced']:
            preference = 'balanced'

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
        # Fall back to top results
        return {
            'recommendations': state['search_results'][:5],
            'messages': [AIMessage(content="Fallback recommendations")]
        }


async def respond_node(state: AgentState) -> dict:
    """
    Response agent that generates the final user-facing response.
    """
    llm = create_llm()

    # Format listings for context
    recs = state.get('recommendations', []) or state.get('search_results', [])[:5]

    if not recs:
        return {
            'final_response': "I couldn't find any listings matching your criteria. Try broadening your search!"
        }

    listings_context = "\n".join([
        f"- {r.get('name', 'Unknown')}: {r.get('description', '')[:100]}... "
        f"(Type: {r.get('property_type', 'N/A')}, Bedrooms: {r.get('bedrooms', 'N/A')}, "
        f"Price: ${r.get('price', 'N/A')}/night)"
        for r in recs[:5]
    ])

    system_prompt = """You are a helpful booking assistant. Based on the search results below,
provide a friendly, concise response to the user's query. Mention 2-3 top options with brief highlights.

Search Results:
{listings}

Keep your response conversational and under 200 words."""

    messages = [
        SystemMessage(content=system_prompt.format(listings=listings_context)),
        HumanMessage(content=state['user_query'])
    ]

    try:
        response = await llm.ainvoke(messages)
        return {'final_response': response.content}
    except Exception as e:
        logger.error(f"Response agent error: {e}")
        return {'final_response': f"Here are some options I found:\n{listings_context}"}


# ============================================================================
# Graph Builder
# ============================================================================

def build_agent_graph():
    """
    Build the LangGraph agent workflow.

    Graph Structure:

        [START] → [Supervisor] → "search"  → [Search] → [Filter] → [Recommend] → [Respond] → [END]
                               → "respond" → [Respond] → [END]

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

    # Linear pipeline: search → filter → recommend → respond → END
    workflow.add_edge("search", "filter")
    workflow.add_edge("filter", "recommend")
    workflow.add_edge("recommend", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()


# ============================================================================
# Public Interface
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
