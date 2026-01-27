"""
Multi-Agent System for Booking Search
=====================================

This module implements a LangGraph-based multi-agent system for intelligent
booking search and recommendations. It's the capstone of Module 3.

Agents:
- Supervisor: Routes queries to appropriate specialist agents
- Search Agent: Handles venue/listing searches
- Filter Agent: Applies filters and refinements
- Recommendation Agent: Provides personalized suggestions

The system gracefully degrades if LangGraph is not available, falling back
to direct RAG responses.
"""

import logging
from typing import TypedDict, Annotated, Literal, Optional, List, Dict, Any
from dataclasses import dataclass

from .config import settings
from .models import Listing

logger = logging.getLogger(__name__)

# Check if LangGraph is available
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available - multi-agent features disabled")


# ============================================================================
# Agent State Definition
# ============================================================================

class AgentState(TypedDict):
    """Shared state passed between agents in the graph."""
    messages: List[BaseMessage]
    user_query: str
    search_results: List[Dict[str, Any]]
    filters: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    next_agent: str
    final_response: str


# ============================================================================
# Agent Tools
# ============================================================================

def create_search_tool(search_fn):
    """Create a search tool that uses the provided search function."""
    
    @tool
    def search_listings(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for listings matching the query.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching listings with scores
        """
        try:
            from .search import search_listings as do_search
            results = do_search(query, limit=limit)
            return [r.model_dump() for r in results]
        except Exception as e:
            logger.error(f"Search tool error: {e}")
            return []
    
    return search_listings


@tool
def apply_filters(
    listings: List[Dict[str, Any]],
    min_rating: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    city: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Apply filters to a list of listings.
    
    Args:
        listings: List of listing dictionaries
        min_rating: Minimum rating filter
        max_price: Maximum price filter  
        category: Category filter
        city: City filter
        
    Returns:
        Filtered list of listings
    """
    filtered = listings.copy()
    
    if min_rating is not None:
        filtered = [l for l in filtered if l.get('rating', 0) >= min_rating]
    
    if max_price is not None:
        filtered = [l for l in filtered if l.get('price', float('inf')) <= max_price]
    
    if category:
        filtered = [l for l in filtered if category.lower() in l.get('category', '').lower()]
    
    if city:
        filtered = [l for l in filtered if city.lower() in l.get('city', '').lower()]
    
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
        # Sort by rating, highest first
        return sorted(listings, key=lambda x: x.get('rating', 0), reverse=True)[:5]
    else:
        # Balanced: combine rating and price into a score
        def score(l):
            rating = l.get('rating', 3.0)
            price = l.get('price', 100)
            # Normalize: higher is better
            return (rating / 5.0) - (price / 500.0)
        return sorted(listings, key=score, reverse=True)[:5]


# ============================================================================
# Agent Nodes
# ============================================================================

def create_llm():
    """Create the appropriate LLM based on configuration."""
    if settings.AZURE_OPENAI_ENDPOINT:
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            temperature=0.7,
        )
    else:
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.7,
        )


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor agent that routes queries to appropriate specialists.
    
    Analyzes the user query and decides which agent should handle it:
    - search: For finding listings
    - filter: For applying constraints
    - recommend: For personalized suggestions
    - respond: For generating final response
    """
    llm = create_llm()
    
    system_prompt = """You are a supervisor agent for a booking search system.
    
Analyze the user's query and decide which specialist agent should handle it:

- "search": The user wants to find listings (e.g., "find restaurants in Seattle")
- "filter": The user wants to filter results (e.g., "only show 4+ star places")
- "recommend": The user wants recommendations (e.g., "what's the best option?")
- "respond": Ready to give final response to user

Current state:
- Search results: {num_results} listings found
- Filters applied: {filters}
- Recommendations: {num_recs} items

Respond with ONLY one word: search, filter, recommend, or respond"""

    num_results = len(state.get('search_results', []))
    filters = state.get('filters', {})
    num_recs = len(state.get('recommendations', []))
    
    messages = [
        SystemMessage(content=system_prompt.format(
            num_results=num_results,
            filters=filters,
            num_recs=num_recs
        )),
        HumanMessage(content=state['user_query'])
    ]
    
    response = llm.invoke(messages)
    next_agent = response.content.strip().lower()
    
    # Validate response
    valid_agents = ['search', 'filter', 'recommend', 'respond']
    if next_agent not in valid_agents:
        # Default behavior based on state
        if num_results == 0:
            next_agent = 'search'
        elif num_recs == 0:
            next_agent = 'recommend'
        else:
            next_agent = 'respond'
    
    state['next_agent'] = next_agent
    state['messages'].append(AIMessage(content=f"Routing to: {next_agent}"))
    
    return state


def search_node(state: AgentState) -> AgentState:
    """
    Search agent that finds relevant listings.
    """
    try:
        from .search import search_listings
        
        results = search_listings(state['user_query'], limit=20)
        state['search_results'] = [r.model_dump() for r in results]
        state['messages'].append(AIMessage(content=f"Found {len(results)} listings"))
        
    except Exception as e:
        logger.error(f"Search agent error: {e}")
        state['search_results'] = []
        state['messages'].append(AIMessage(content=f"Search error: {str(e)}"))
    
    state['next_agent'] = 'recommend'  # Move to recommendations
    return state


def filter_node(state: AgentState) -> AgentState:
    """
    Filter agent that applies constraints to results.
    """
    llm = create_llm()
    
    # Extract filter intent from query
    system_prompt = """Extract filter criteria from the user query.
    
Respond in JSON format with these optional fields:
- min_rating: number (1-5)
- max_price: number
- category: string
- city: string

Example: {"min_rating": 4.0, "city": "Seattle"}

If no clear filters, respond with: {}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['user_query'])
    ]
    
    try:
        response = llm.invoke(messages)
        import json
        filters = json.loads(response.content)
        state['filters'] = filters
        
        # Apply filters
        filtered = apply_filters.invoke({
            'listings': state['search_results'],
            **filters
        })
        state['search_results'] = filtered
        state['messages'].append(AIMessage(content=f"Applied filters, {len(filtered)} results remain"))
        
    except Exception as e:
        logger.error(f"Filter agent error: {e}")
        state['messages'].append(AIMessage(content=f"Filter error: {str(e)}"))
    
    state['next_agent'] = 'recommend'
    return state


def recommend_node(state: AgentState) -> AgentState:
    """
    Recommendation agent that ranks and suggests listings.
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
        response = llm.invoke(messages)
        preference = response.content.strip().lower()
        if preference not in ['budget', 'quality', 'balanced']:
            preference = 'balanced'
        
        recs = get_recommendations.invoke({
            'listings': state['search_results'],
            'preference': preference
        })
        state['recommendations'] = recs
        state['messages'].append(AIMessage(content=f"Generated {len(recs)} recommendations ({preference})"))
        
    except Exception as e:
        logger.error(f"Recommendation agent error: {e}")
        # Fall back to top results
        state['recommendations'] = state['search_results'][:5]
        state['messages'].append(AIMessage(content=f"Fallback recommendations"))
    
    state['next_agent'] = 'respond'
    return state


def respond_node(state: AgentState) -> AgentState:
    """
    Response agent that generates the final user-facing response.
    """
    llm = create_llm()
    
    # Format listings for context
    recs = state.get('recommendations', []) or state.get('search_results', [])[:5]
    
    if not recs:
        state['final_response'] = "I couldn't find any listings matching your criteria. Try broadening your search!"
        return state
    
    listings_context = "\n".join([
        f"- {r.get('name', 'Unknown')}: {r.get('description', '')[:100]}... "
        f"(Rating: {r.get('rating', 'N/A')}, Price: ${r.get('price', 'N/A')})"
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
        response = llm.invoke(messages)
        state['final_response'] = response.content
    except Exception as e:
        logger.error(f"Response agent error: {e}")
        state['final_response'] = f"Here are some options I found:\n{listings_context}"
    
    return state


# ============================================================================
# Graph Builder
# ============================================================================

def build_agent_graph():
    """
    Build the LangGraph agent workflow.
    
    Graph Structure:
    
        [START]
           ↓
      [Supervisor] ←────────────┐
           ↓                    │
      ┌────┴────┬──────┐        │
      ↓         ↓      ↓        │
   [Search] [Filter] [Recommend]│
      └────┬────┴──────┘        │
           ↓                    │
      [Supervisor] ─────────────┘
           ↓
      [Respond]
           ↓
        [END]
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
        next_agent = state.get('next_agent', 'search')
        return next_agent
    
    # Add edges
    workflow.set_entry_point("supervisor")
    
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "search": "search",
            "filter": "filter",
            "recommend": "recommend",
            "respond": "respond",
        }
    )
    
    # After search/filter/recommend, go back to supervisor
    workflow.add_edge("search", "supervisor")
    workflow.add_edge("filter", "supervisor")
    workflow.add_edge("recommend", "supervisor")
    
    # Respond ends the workflow
    workflow.add_edge("respond", END)
    
    return workflow.compile()


# ============================================================================
# Public Interface
# ============================================================================

# Compiled graph (lazy initialization)
_agent_graph = None


def get_agent_graph():
    """Get the compiled agent graph, building it if necessary."""
    global _agent_graph
    if _agent_graph is None and LANGGRAPH_AVAILABLE:
        _agent_graph = build_agent_graph()
    return _agent_graph


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
        
        return {
            "response": final_state['final_response'],
            "agent_path": agent_path,
            "search_results": final_state.get('recommendations', [])[:10],
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
