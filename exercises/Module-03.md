# Module 3: Multi-Agent System with LangGraph

### 📂 **You'll be editing:** [`src/api/agents.py`](../src/api/agents.py)
### ✅ **Solution:** [`solutions/agents_solution.py`](../solutions/agents_solution.py) — check here if you get stuck

## 📋 Learning Objectives

By the end of this module, you will:
- Understand multi-agent system architecture and benefits
- Design specialized agents with distinct responsibilities
- Implement agent orchestration using LangGraph
- Manage complex state across multiple agents
- Build a supervisor agent that routes tasks intelligently
- Create a production-ready multi-agent chat system

## 🎯 What You'll Build

You'll implement the multi-agent backend that powers the application's intelligent search. When a user types a complex query, your code will:
1. Route the query to the right specialist agent via a **supervisor**
2. **Search** for listings using vector search
3. **Filter** results based on extracted constraints
4. **Recommend** top listings based on user preferences
5. **Respond** with a friendly, conversational answer

### Example Multi-Agent Conversation:

```
User: "I need a place with a kitchen, 2 bedrooms, under $200"

[Supervisor routes to Search Agent]
Search Agent: Performs vector search → Returns 20 listings

[Search routes to Recommend Agent]
Recommend Agent: Ranks by balanced preference → Top 5

[Recommend routes to Respond Agent]
Respond Agent:
"Based on your needs, I recommend:

1. **Cozy Cottage in LoHi** - $161/night ⭐
   Perfect match! This 2-bedroom guesthouse has a full kitchen and great reviews.

2. **Spacious Apartment near Downtown** - $175/night
   Excellent value! Fully equipped kitchen and close to restaurants.

Both are well under your $200 budget. Interested in booking?"
```

## 📚 Concept: Multi-Agent Systems

### What are Multi-Agent Systems?

A multi-agent system uses multiple specialized AI agents that:
- Each handle specific tasks they're optimized for
- Communicate and coordinate through shared state
- Work together to solve complex problems
- Make decisions about task delegation

### Why Use Multi-Agent Systems?

**Single Agent Approach:**
❌ One agent tries to do everything
❌ Complex prompts that confuse the model
❌ Difficult to maintain and debug
❌ Limited by context window size

**Multi-Agent Approach:**
✅ Specialized agents with clear responsibilities
✅ Simpler, focused prompts per agent
✅ Easier to test and improve individual components
✅ More scalable and maintainable
✅ Better error handling and recovery

### Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Query: "Pet-friendly 3BR in Denver under $200"           │
│                           │                                     │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   Supervisor Agent     │                        │
│              │  (Task Router)         │                        │
│              └────────┬───────────────┘                        │
│                       │                                         │
│          ┌────────────┼────────────┬──────────┐               │
│          │            │            │          │               │
│          ▼            ▼            ▼          ▼               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Search   │ │ Filter   │ │Recommend │ │ Respond  │        │
│  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent    │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘        │
│       └────────────┴────────────┘                             │
│                           │                                     │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   Shared State         │                        │
│              │  - Messages            │                        │
│              │  - Search Results      │                        │
│              │  - Filters             │                        │
│              │  - Recommendations     │                        │
│              │  - Final Response      │                        │
│              └────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### LangGraph

[LangGraph](https://langchain-ai.github.io/langgraph/) is a framework for building stateful, multi-agent workflows. Key concepts:

| Concept | Description |
|---------|-------------|
| **StateGraph** | A directed graph where nodes are functions and edges define transitions |
| **State (TypedDict)** | A shared dictionary passed between all nodes |
| **Nodes** | Functions that take state, do work, and return updated state |
| **Edges** | Transitions between nodes — can be direct or conditional |
| **Conditional Edges** | Route to different nodes based on state values |
| **Entry Point** | The first node to execute |
| **END** | Special sentinel that terminates the workflow |

---

## 🛠️ Step 1: Explore the Existing Code

Before writing anything, take a few minutes to understand how the pieces fit together.

### 1a. Review the search module

Open [`src/api/search.py`](../src/api/search.py) and find:

- **`search_listings(query, limit, filters)`** — the unified search function that performs vector search against DocumentDB
- **`generate_embedding(text)`** — converts text to a vector using OpenAI

Your agents will call `search_listings()` to find relevant listings.

### 1b. Review the chat module

Open [`src/api/chat.py`](../src/api/chat.py). The multi-agent system falls back to `generate_chat_response()` when LangGraph isn't available — so Module 2 must be complete first.

### 1c. Review the API endpoint

Open [`src/api/main.py`](../src/api/main.py) and find the `/query_message` endpoint. Notice it calls `run_agent_query()` when multi-agent is available — that's the function you'll implement in Step 6.

### 1d. Open the exercise file

Open [`src/api/agents.py`](../src/api/agents.py). This is where you'll work for the rest of Module 3. You'll see:
- Imports and LangGraph availability check (already done)
- `AgentState` TypedDict (Step 2 — TODO)
- Agent tools: `create_search_tool`, `apply_filters`, `get_recommendations` (Step 3 — TODO)
- Agent nodes: `supervisor_node`, `search_node`, `filter_node`, `recommend_node`, `respond_node` (Step 4 — TODO)
- `build_agent_graph()` (Step 5 — TODO)
- `run_agent_query()` and `is_multi_agent_available()` (Step 6 — TODO)

The `create_llm()` function and `get_agent_graph()` helper are already implemented for you.

---

## 🛠️ Step 2: Define the Agent State

📂 **Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the `AgentState` class

The `AgentState` is a `TypedDict` that acts as the shared memory for all agents. Every agent function receives this state, reads what it needs, does its work, and writes its results back.

### Requirements

Define these fields on `AgentState`:

| Field | Type | Purpose |
|-------|------|---------|
| `messages` | `List[BaseMessage]` | Conversation history (human + AI messages) |
| `user_query` | `str` | The user's original natural language query |
| `search_results` | `List[Dict[str, Any]]` | Listings found by the search agent |
| `filters` | `Dict[str, Any]` | Extracted filter criteria (price, property_type, bedrooms, etc.) |
| `recommendations` | `List[Dict[str, Any]]` | Ranked/recommended listings |
| `next_agent` | `str` | Which agent should run next (routing decision) |
| `final_response` | `str` | The final response text to send to the user |

### 💡 Why a TypedDict?

LangGraph uses `TypedDict` to define the schema of the shared state. This gives you:
- Type checking in your IDE
- Clear documentation of what data flows between agents
- Validation that all required fields are present

<details>
<summary>🔑 Solution</summary>

```python
class AgentState(TypedDict):
    """Shared state passed between agents in the graph."""
    messages: List[BaseMessage]
    user_query: str
    search_results: List[Dict[str, Any]]
    filters: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    next_agent: str
    final_response: str
```

</details>

---

## 🛠️ Step 3: Implement the Agent Tools

📂 **Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the Step 3 section

Tools are decorated functions that agents can invoke to perform data operations. You'll implement three tools.

### 3a. `create_search_tool(search_fn)`

A factory function that returns a `@tool`-decorated search function.

**Requirements:**
- The inner function accepts `query: str` and `limit: int = 10`
- Import `search_listings` from `.search`
- Call `search_listings(query, limit=limit)`
- Return results as a list of dicts (use `r.model_dump()` on each result)
- Wrap in try/except — return `[]` on error

<details>
<summary>🔑 Solution</summary>

```python
def create_search_tool(search_fn):
    """Create a search tool that uses the provided search function."""
    
    @tool
    def search_listings(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for listings matching the query."""
        try:
            from .search import search_listings as do_search
            results = do_search(query, limit=limit)
            return [r.model_dump() for r in results]
        except Exception as e:
            logger.error(f"Search tool error: {e}")
            return []
    
    return search_listings
```

</details>

### 3b. `apply_filters`

A `@tool`-decorated function that filters a list of listings.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `listings` | `List[Dict[str, Any]]` | Listings to filter |
| `max_price` | `Optional[float]` | Keep listings with `price <= max_price` |
| `property_type` | `Optional[str]` | Keep listings where property_type contains this string (case-insensitive) |
| `min_bedrooms` | `Optional[int]` | Keep listings where `bedrooms >= min_bedrooms` |
| `amenities` | `Optional[List[str]]` | Keep listings that have all required amenities (case-insensitive) |

**Requirements:**
- Start with a copy of the listings list
- Apply each filter only if the parameter is not `None`
- Return the filtered list

<details>
<summary>🔑 Solution</summary>

```python
@tool
def apply_filters(
    listings: List[Dict[str, Any]],
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    min_bedrooms: Optional[int] = None,
    amenities: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Apply filters to a list of listings."""
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
```

</details>

### 3c. `get_recommendations`

A `@tool`-decorated function that ranks listings by user preference.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `listings` | `List[Dict[str, Any]]` | Listings to rank |
| `preference` | `str` | One of `"budget"`, `"quality"`, or `"balanced"` |

**Ranking strategies:**
- `"budget"` — Sort by price ascending (cheapest first), return top 5
- `"quality"` — Sort by score descending (most relevant first), return top 5
- `"balanced"` — Rank each listing as `score - (price / 500.0)`, sort descending, return top 5

<details>
<summary>🔑 Solution</summary>

```python
@tool
def get_recommendations(
    listings: List[Dict[str, Any]],
    preference: str = "balanced"
) -> List[Dict[str, Any]]:
    """Get personalized recommendations from listings."""
    if not listings:
        return []
    
    if preference == "budget":
        return sorted(listings, key=lambda x: x.get('price', float('inf')))[:5]
    elif preference == "quality":
        return sorted(listings, key=lambda x: x.get('score', 0), reverse=True)[:5]
    else:
        def rank(l):
            relevance = l.get('score', 0.5)
            price = l.get('price', 100)
            return relevance - (price / 500.0)
        return sorted(listings, key=rank, reverse=True)[:5]
```

</details>

---

## 🛠️ Step 4: Implement the Agent Nodes

📂 **Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the Step 4 section

Each agent node is a function with the signature `(state: AgentState) -> AgentState`. Nodes read from the shared state, perform their specialized task, update the state, and return it.

### 4a. `supervisor_node`

The supervisor is the "brain" of the system — it decides which specialist should handle the query.

**Requirements:**
1. Call `create_llm()` to get an LLM instance
2. Build a system prompt describing the four routing options:
   - `"search"` — user wants to find listings (e.g., "find apartments near downtown Denver")
   - `"filter"` — user wants to apply constraints (e.g., "under $150 with 2 bedrooms")
   - `"recommend"` — user wants recommendations (e.g., "what's the best value?")
   - `"respond"` — ready to give a final answer
3. Include the current state summary (number of results, filters, recommendations)
4. Ask the LLM to respond with ONLY one word
5. Validate the LLM's response — if not one of the four valid options, use fallback logic:
   - No search results yet → `"search"`
   - No recommendations yet → `"recommend"`
   - Otherwise → `"respond"`
6. Set `state['next_agent']` to the chosen agent
7. Append a routing message (`AIMessage`) to `state['messages']`

### 💡 Why validation?

LLMs sometimes return extra text or unexpected answers. The validation step ensures the system always routes to a valid agent, even if the LLM misbehaves.

<details>
<summary>🔑 Solution</summary>

```python
def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor agent that routes queries to appropriate specialists."""
    llm = create_llm()
    
    system_prompt = """You are a supervisor agent for a booking search system.
    
Analyze the user's query and decide which specialist agent should handle it:

- "search": The user wants to find listings (e.g., "find apartments near downtown Denver")
- "filter": The user wants to filter results (e.g., "only show places under $150 with 2 bedrooms")
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
    
    valid_agents = ['search', 'filter', 'recommend', 'respond']
    if next_agent not in valid_agents:
        if num_results == 0:
            next_agent = 'search'
        elif num_recs == 0:
            next_agent = 'recommend'
        else:
            next_agent = 'respond'
    
    state['next_agent'] = next_agent
    state['messages'].append(AIMessage(content=f"Routing to: {next_agent}"))
    
    return state
```

</details>

### 4b. `search_node`

The search agent finds relevant listings using vector search.

**Requirements:**
1. Import `search_listings` from `.search`
2. Call `search_listings(state['user_query'], limit=20)`
3. Convert each result to a dict: `{**r.listing.model_dump(), 'score': r.score}`
4. Store the list in `state['search_results']`
5. Append a status message to `state['messages']` (e.g., "Found N listings")
6. Set `state['next_agent'] = 'recommend'`
7. Wrap in try/except — on error, set empty results and log the error

<details>
<summary>🔑 Solution</summary>

```python
def search_node(state: AgentState) -> AgentState:
    """Search agent that finds relevant listings."""
    try:
        from .search import search_listings
        
        results = search_listings(state['user_query'], limit=20)
        state['search_results'] = [
            {**r.listing.model_dump(), 'score': r.score}
            for r in results
        ]
        state['messages'].append(AIMessage(content=f"Found {len(results)} listings"))
        
    except Exception as e:
        logger.error(f"Search agent error: {e}")
        state['search_results'] = []
        state['messages'].append(AIMessage(content=f"Search error: {str(e)}"))
    
    state['next_agent'] = 'recommend'
    return state
```

</details>

### 4c. `filter_node`

The filter agent extracts constraints from the user's query and applies them to search results.

**Requirements:**
1. Call `create_llm()` to get an LLM instance
2. Send a system prompt asking the LLM to extract filter criteria as JSON:
   - Fields: `max_price` (number), `property_type` (string), `min_bedrooms` (integer), `amenities` (array of strings)
   - Example: `{"max_price": 200, "property_type": "Apartment", "min_bedrooms": 2}`
3. Parse the JSON response with `json.loads()` (remember to `import json`)
4. Store the parsed filters in `state['filters']`
5. Call `apply_filters.invoke()` with the search results and parsed filters
6. Update `state['search_results']` with the filtered results
7. Append a status message to `state['messages']`
8. Set `state['next_agent'] = 'recommend'`
9. Handle JSON parse errors and other exceptions gracefully

<details>
<summary>🔑 Solution</summary>

```python
def filter_node(state: AgentState) -> AgentState:
    """Filter agent that applies constraints to results."""
    llm = create_llm()
    
    system_prompt = """Extract filter criteria from the user query.
    
Respond in JSON format with these optional fields:
- max_price: number (maximum price per night)
- property_type: string (e.g. "Apartment", "House", "Condo", "Guesthouse")
- min_bedrooms: integer (minimum number of bedrooms)
- amenities: array of strings (e.g. ["Wifi", "Kitchen", "Free parking"])

Example: {"max_price": 200, "property_type": "Apartment", "min_bedrooms": 2}

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
```

</details>

### 4d. `recommend_node`

The recommendation agent ranks listings based on user preferences.

**Requirements:**
1. Call `create_llm()` to get an LLM instance
2. Use a system prompt to determine the user's preference from their query — the LLM should respond with ONLY one word: `"budget"`, `"quality"`, or `"balanced"`
3. Validate the response — default to `"balanced"` if invalid
4. Call `get_recommendations.invoke()` with the search results and detected preference
5. Store the recommendations in `state['recommendations']`
6. Append a status message to `state['messages']`
7. Set `state['next_agent'] = 'respond'`
8. On error, fall back to `state['search_results'][:5]`

<details>
<summary>🔑 Solution</summary>

```python
def recommend_node(state: AgentState) -> AgentState:
    """Recommendation agent that ranks and suggests listings."""
    llm = create_llm()
    
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
        state['recommendations'] = state['search_results'][:5]
        state['messages'].append(AIMessage(content=f"Fallback recommendations"))
    
    state['next_agent'] = 'respond'
    return state
```

</details>

### 4e. `respond_node`

The response agent generates the final user-facing message.

**Requirements:**
1. Call `create_llm()` to get an LLM instance
2. Get recommendations from state (fall back to `search_results[:5]` if empty)
3. If there are no results at all, set a "no results found" message and return early
4. Format the top 5 listings into a context string with name, description snippet, property type, bedrooms, and price
5. Build a system prompt asking the LLM to be a friendly booking assistant and keep the response under 200 words
6. Invoke the LLM and store the response in `state['final_response']`
7. On error, fall back to the raw listings context string

<details>
<summary>🔑 Solution</summary>

```python
def respond_node(state: AgentState) -> AgentState:
    """Response agent that generates the final user-facing response."""
    llm = create_llm()
    
    recs = state.get('recommendations', []) or state.get('search_results', [])[:5]
    
    if not recs:
        state['final_response'] = "I couldn't find any listings matching your criteria. Try broadening your search!"
        return state
    
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
        response = llm.invoke(messages)
        state['final_response'] = response.content
    except Exception as e:
        logger.error(f"Response agent error: {e}")
        state['final_response'] = f"Here are some options I found:\n{listings_context}"
    
    return state
```

</details>

---

## 🛠️ Step 5: Build the LangGraph Workflow

📂 **Edit:** [`src/api/agents.py`](../src/api/agents.py) — find `build_agent_graph()`

This function wires all agent nodes into a LangGraph `StateGraph`. The graph defines how agents connect and in what order they execute.

### Graph Structure

```
    [START]
       ↓
  [Supervisor] ←────────────────┐
       ↓                        │
  (conditional routing)         │
       ↓                        │
  ┌────┴────┬───────┬──────┐    │
  ↓         ↓       ↓      ↓   │
[Search] [Filter] [Recommend] [Respond]
  │         │       │           │
  └────┬────┘       │           │
       ↓            │           │
  [Recommend] ◄─────┘           │
       ↓                        │
  [Respond]                     │
       ↓                        │
     [END]                      │
```

### Requirements

1. Return `None` if `LANGGRAPH_AVAILABLE` is `False`
2. Create a `StateGraph(AgentState)`
3. Add all 5 nodes: `"supervisor"`, `"search"`, `"filter"`, `"recommend"`, `"respond"`
4. Set `"supervisor"` as the entry point
5. Add **conditional edges** from `"supervisor"` — define a routing function that reads `state['next_agent']` and maps to node names:
   ```python
   {"search": "search", "filter": "filter", "recommend": "recommend", "respond": "respond"}
   ```
6. Add **direct edges** for the linear flow after routing:
   - `"search"` → `"recommend"`
   - `"filter"` → `"recommend"`
   - `"recommend"` → `"respond"`
   - `"respond"` → `END`
7. Compile the graph and return it

### 💡 Conditional vs Direct Edges

- **Conditional edges** let the supervisor dynamically choose the next agent based on state
- **Direct edges** create a fixed flow after the initial routing — this prevents loops and ensures the pipeline always progresses forward

<details>
<summary>🔑 Solution</summary>

```python
def build_agent_graph():
    """Build the LangGraph agent workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None
    
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
    
    workflow.add_edge("search", "recommend")
    workflow.add_edge("filter", "recommend")
    workflow.add_edge("recommend", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()
```

</details>

---

## 🛠️ Step 6: Implement the Public Interface

📂 **Edit:** [`src/api/agents.py`](../src/api/agents.py) — find `run_agent_query()` and `is_multi_agent_available()`

These are the functions that `main.py` imports. They expose the multi-agent system to the rest of the application.

### 6a. `run_agent_query(query, session_id)`

This async function is the main entry point for the multi-agent system.

**Requirements:**
1. Get the compiled graph via `get_agent_graph()`
2. If the graph is `None` (LangGraph not installed), fall back to simple RAG:
   - Import `generate_chat_response` from `.chat`
   - Return `{"response": ..., "agent_path": ["fallback_rag"], "search_results": [], "multi_agent": False}`
3. Initialize the `AgentState` with the query, empty lists/dicts for all fields
4. Run the graph: `final_state = await graph.ainvoke(initial_state)`
5. Extract the agent path by finding routing messages in `final_state['messages']`
6. Return a dict with:
   - `"response"` — `final_state['final_response']`
   - `"agent_path"` — list of agent names from routing messages
   - `"search_results"` — `final_state['recommendations'][:10]`
   - `"multi_agent"` — `True`
7. On any exception, fall back to simple RAG (same as step 2)

### 6b. `is_multi_agent_available()`

Returns `True` if LangGraph is installed AND the agent graph compiled successfully.

<details>
<summary>🔑 Solution</summary>

```python
async def run_agent_query(query: str, session_id: str = "default") -> Dict[str, Any]:
    """Run a query through the multi-agent system."""
    graph = get_agent_graph()
    
    if graph is None:
        from .chat import generate_chat_response
        response = await generate_chat_response(query, session_id)
        return {
            "response": response,
            "agent_path": ["fallback_rag"],
            "search_results": [],
            "multi_agent": False
        }
    
    try:
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "search_results": [],
            "filters": {},
            "recommendations": [],
            "next_agent": "",
            "final_response": ""
        }
        
        final_state = await graph.ainvoke(initial_state)
        
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
```

</details>

---

## 🧪 Step 7: Test Your Implementation

Now let's verify everything works end-to-end.

### 7a. Restart the API

If you're running with Docker Compose:

```bash
docker-compose up --build
```

Or if running the API directly:

```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7b. Check multi-agent availability

```bash
curl http://localhost:8000/health
```

Look for `"multi_agent_available": true` in the response. If it's `false`, make sure LangGraph is installed:

```bash
pip install langgraph langchain langchain-openai
```

### 7c. Test with curl

**Simple search query:**
```bash
curl -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me a cozy place near downtown Denver", "session_id": "test1"}'
```

**Complex multi-criteria query:**
```bash
curl -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "3 bedroom house under $200 with parking", "session_id": "test2"}'
```

**Budget-focused query:**
```bash
curl -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the cheapest option available?", "session_id": "test3"}'
```

### 7d. Test in the frontend

Open http://localhost:3000 and use the chat panel. Try queries that exercise different agents:

1. **Search Agent**: "Show me apartments in Denver"
2. **Filter Agent**: "Only show places with at least 2 bedrooms under $150"
3. **Recommend Agent**: "What's the best value option?"
4. **Multi-agent pipeline**: "2-bedroom apartment with kitchen and parking, under $200"

### 7e. What to check for

| ✅ Working | ❌ Possible Issue |
|-----------|-----------------|
| Response mentions specific listings | Check `respond_node()` — is the context being formatted? |
| Multi-agent path shown in response | Check `supervisor_node()` — is it appending routing messages? |
| Budget queries return cheapest first | Check `recommend_node()` — is preference detection working? |
| Graceful fallback without LangGraph | Check `run_agent_query()` — is it falling back to RAG? |

---

## 🎓 What You've Learned

✅ **Multi-Agent Architecture**: Designing systems with specialized agents
✅ **LangGraph**: Building stateful workflows with `StateGraph`
✅ **Agent Orchestration**: Routing tasks intelligently with a supervisor
✅ **Shared State**: Coordinating data across multiple agents via `TypedDict`
✅ **Tool Design**: Creating `@tool`-decorated functions for data operations
✅ **Graceful Degradation**: Falling back to simpler systems when dependencies are unavailable
✅ **End-to-End Integration**: Wiring your agents into a running web application

---

## 🚀 Challenges

### Challenge 1: Add a Clarification Agent (Medium)

Create an agent that detects vague queries and asks clarifying questions before searching.

**Requirements:**
- Use the LLM to determine if a query is too vague (missing location, budget, size)
- If vague, generate 2–3 clarifying questions and set as `final_response`
- If detailed enough, route to the filter agent

Add a new `clarification_node` and wire it into `build_agent_graph()` as the entry point (before supervisor).

### Challenge 2: Add Error Handling Agent (Medium)

Create an agent that handles the case when search returns zero results.

**Requirements:**
- Check if `search_results` is empty after the search agent runs
- Suggest ways to broaden the search (different area, higher budget, fewer bedrooms)
- Set a helpful `final_response`

### Challenge 3: Add a Booking Agent (Hard)

Create an agent that handles booking intent (e.g., "I'll take the first one").

**Requirements:**
- Detect booking intent from the query
- Generate a booking summary with listing details
- Provide next steps (how to reserve, payment, cancellation policy)

Add it as a new routing option in the supervisor.

### Challenge 4: Implement Conversation Memory (Hard)

The current system treats each query independently. Add conversation memory so follow-up questions work:

- "Find me places in Denver" → searches normally
- "Do any of those have parking?" → references previous results

**Hint:** Use `MemorySaver` from LangGraph and pass a `thread_id` config when invoking the graph.

---

## ✅ Checkpoint

Before completing the workshop, ensure you have:

- [ ] Defined the `AgentState` TypedDict with all 7 fields
- [ ] Implemented `create_search_tool`, `apply_filters`, and `get_recommendations` tools
- [ ] Implemented all 5 agent nodes (supervisor, search, filter, recommend, respond)
- [ ] Built the LangGraph workflow in `build_agent_graph()`
- [ ] Implemented `run_agent_query()` with fallback to simple RAG
- [ ] Implemented `is_multi_agent_available()`
- [ ] Tested search queries via the API or frontend
- [ ] Verified the supervisor routes correctly based on query intent
- [ ] Completed at least one challenge exercise

## 🎉 Workshop Complete!

Congratulations! You've built a sophisticated AI-powered application with:

✅ **Vector Search** (Module 1) — Semantic search with DocumentDB cosmosSearch
✅ **RAG Pattern** (Module 2) — Context-aware AI responses with LangChain
✅ **Multi-Agent System** (Module 3) — Specialized agents orchestrated with LangGraph

### Key Takeaways:

🎯 **Vector Search** enables semantic understanding beyond keywords
🎯 **RAG Pattern** grounds AI responses in your real data
🎯 **Multi-Agent Systems** make complex AI applications maintainable
🎯 **LangGraph** provides powerful orchestration for stateful workflows

---

**💬 Stuck?** Compare your code with [`solutions/agents_solution.py`](../solutions/agents_solution.py) or ask your instructor for help!
