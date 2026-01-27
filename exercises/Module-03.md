# Module 3: Multi-Agent System with LangGraph

### 📓 **[Open the Jupyter Notebook](../notebooks/module-03.ipynb)** to follow along with the code exercises.

## 📋 Learning Objectives

By the end of this module, you will:
- Understand multi-agent system architecture and benefits
- Design specialized agents with distinct responsibilities
- Implement agent orchestration using LangGraph
- Manage complex state across multiple agents
- Build a supervisor agent that routes tasks intelligently
- Create a production-ready multi-agent chat system

## 🎯 What You'll Build

You'll create a sophisticated multi-agent system where specialized agents work together to help users find accommodations:

**Agent Team:**
1. **Search Agent** - Finds listings using vector search
2. **Filter Agent** - Extracts and applies filters from natural language
3. **Recommendation Agent** - Analyzes listings and provides personalized recommendations
4. **Supervisor Agent** - Routes tasks to the appropriate agent

### Example Multi-Agent Conversation:

```
User: "I need a pet-friendly place in Chicago, 3 bedrooms, under $200"

[Supervisor routes to Filter Agent]
Filter Agent: Extracts filters → {location: "Chicago", bedrooms: 3, price_max: 200, amenities: ["pet-friendly"]}

[Supervisor routes to Search Agent]
Search Agent: Performs vector search with filters → Returns 5 listings

[Supervisor routes to Recommendation Agent]
Recommendation Agent: 
"Based on your needs, I recommend:

1. **Family House in Lincoln Park** - $185/night ⭐
   Perfect match! This 3-bedroom house welcomes pets and has a fenced yard. 
   Great family neighborhood with parks nearby.

2. **Spacious Apartment with Pet Area** - $175/night
   Excellent value! Dedicated pet washing station and close to dog-friendly trails.

Both are well under your $200 budget. The Lincoln Park house is my top pick 
for the yard access. Interested in booking?"
```

## 📚 Concept: Multi-Agent Systems

### What are Multi-Agent Systems?

A multi-agent system uses multiple specialized AI agents that:
- Each handle specific tasks they're optimized for
- Communicate and coordinate with each other
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
│  User Query: "Pet-friendly 3BR in Chicago under $200"          │
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
│  │ Filter   │ │ Search   │ │Recommend │ │ Memory   │        │
│  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent    │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │            │            │            │               │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                           │                                     │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   Shared State         │                        │
│              │  - Filters             │                        │
│              │  - Search Results      │                        │
│              │  - Conversation        │                        │
│              │  - Current Agent       │                        │
│              └────────────────────────┘                        │
│                           │                                     │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   Final Response       │                        │
│              └────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Step 1: Install and Import LangGraph

### Install LangGraph

```python
# Run in terminal or notebook cell
# !pip install langgraph

# Verify installation
import langgraph
print(f"✅ LangGraph version: {langgraph.__version__}")
```

### Import Required Libraries

```python
import os
from typing import Annotated, TypedDict, Literal
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Load environment
load_dotenv()

# Initialize connections
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
mongo_client = MongoClient(os.getenv('DOCUMENTDB_CONNECTION_STRING'))
db = mongo_client['contoso_bookings']
collection = db['listings']

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv('OPENAI_API_KEY')
)

print("✅ Environment initialized for multi-agent system")
```

## 🛠️ Step 2: Define the Shared State

The state is shared across all agents and tracks the conversation.

### Create the State Schema

```python
import operator
from typing import Sequence

class AgentState(TypedDict):
    """
    Shared state that all agents can read and write to.
    """
    # Messages in the conversation
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]
    
    # Current user query
    current_query: str
    
    # Extracted filters
    filters: dict
    
    # Search results
    search_results: list
    
    # Next agent to execute
    next_agent: str
    
    # Final response to user
    final_response: str
    
    # Conversation session ID
    session_id: str

print("✅ Agent state schema defined")
```

### 💡 Understanding the State

- **messages**: Full conversation history (automatically appended)
- **current_query**: The user's latest question
- **filters**: Extracted search criteria (bedrooms, price, location, etc.)
- **search_results**: Listings found by the Search Agent
- **next_agent**: Which agent should run next (routing decision)
- **final_response**: The response to send back to the user
- **session_id**: Tracks the conversation session

## 🛠️ Step 3: Build Specialized Agents

### Agent 1: Filter Extraction Agent

```python
def filter_agent(state: AgentState) -> AgentState:
    """
    Extract structured filters from natural language query.
    
    Responsibilities:
    - Parse user query for search criteria
    - Extract: bedrooms, price range, location, amenities, property type
    - Return structured filter dictionary
    """
    query = state["current_query"]
    
    # Create extraction prompt
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a filter extraction specialist. Extract search criteria from user queries.

Return a JSON object with these fields (use null if not mentioned):
- bedrooms: number or null
- beds: number or null
- price_min: number or null
- price_max: number or null
- location: string (city/market name) or null
- property_type: string ("House", "Apartment", "Condominium", etc.) or null
- amenities: array of strings (e.g., ["Wifi", "Kitchen", "Parking"])

Examples:
Query: "3 bedroom house in Chicago under $200"
Output: {{"bedrooms": 3, "property_type": "House", "location": "Chicago", "price_max": 200, "amenities": []}}

Query: "apartment with parking and kitchen"
Output: {{"property_type": "Apartment", "amenities": ["Parking", "Kitchen"]}}

Only return valid JSON, no explanation."""),
        ("human", "{query}")
    ])
    
    # Extract filters
    chain = extraction_prompt | llm | StrOutputParser()
    try:
        import json
        filters_json = chain.invoke({"query": query})
        filters = json.loads(filters_json)
        
        # Clean up the filters (remove null values)
        filters = {k: v for k, v in filters.items() if v is not None and v != [] and v != ""}
        
        print(f"🔍 Filter Agent: Extracted filters: {filters}")
    except Exception as e:
        print(f"⚠️ Filter Agent: Error extracting filters: {e}")
        filters = {}
    
    # Update state
    state["filters"] = filters
    state["next_agent"] = "search"  # Route to search agent next
    
    return state

print("✅ Filter Agent created")
```

### Agent 2: Search Agent

```python
def search_agent(state: AgentState) -> AgentState:
    """
    Perform vector search with extracted filters.
    
    Responsibilities:
    - Generate embedding for the query
    - Execute DocumentDB vector search with cosmosSearch
    - Apply filters to refine results
    - Return top matching listings
    """
    query = state["current_query"]
    filters = state.get("filters", {})
    
    # Generate embedding
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    # Build MongoDB match conditions from filters
    match_conditions = {}
    
    if "bedrooms" in filters:
        match_conditions["bedrooms"] = {"$gte": filters["bedrooms"]}
    
    if "beds" in filters:
        match_conditions["beds"] = {"$gte": filters["beds"]}
    
    if "price_min" in filters or "price_max" in filters:
        price_condition = {}
        if "price_min" in filters:
            price_condition["$gte"] = filters["price_min"]
        if "price_max" in filters:
            price_condition["$lte"] = filters["price_max"]
        match_conditions["price"] = price_condition
    
    if "location" in filters:
        match_conditions["address.market"] = {"$regex": filters["location"], "$options": "i"}
    
    if "property_type" in filters:
        match_conditions["property_type"] = {"$regex": filters["property_type"], "$options": "i"}
    
    if "amenities" in filters and filters["amenities"]:
        match_conditions["amenities"] = {"$all": filters["amenities"]}
    
    # Build aggregation pipeline
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "descriptionVector",
                    "k": 20  # Fetch more to account for filtering
                },
                "returnStoredSource": True
            }
        }
    ]
    
    # Add filter stage if we have conditions
    if match_conditions:
        pipeline.append({"$match": match_conditions})
    
    # Add projection and limit
    pipeline.extend([
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "description": 1,
                "summary": 1,
                "property_type": 1,
                "bedrooms": 1,
                "beds": 1,
                "price": 1,
                "amenities": 1,
                "address": 1,
                "searchScore": {"$meta": "searchScore"}
            }
        },
        {"$limit": 5}
    ])
    
    # Execute search
    results = list(collection.aggregate(pipeline))
    
    print(f"🔎 Search Agent: Found {len(results)} listings")
    
    # Update state
    state["search_results"] = results
    state["next_agent"] = "recommend"  # Route to recommendation agent
    
    return state

print("✅ Search Agent created")
```

### Agent 3: Recommendation Agent

```python
def recommendation_agent(state: AgentState) -> AgentState:
    """
    Analyze search results and provide personalized recommendations.
    
    Responsibilities:
    - Analyze retrieved listings against user preferences
    - Rank and explain why each listing matches
    - Generate conversational, helpful response
    - Suggest next steps
    """
    query = state["current_query"]
    results = state.get("search_results", [])
    filters = state.get("filters", {})
    
    if not results:
        response = "I couldn't find any listings matching your criteria. Would you like to adjust your search parameters?"
        state["final_response"] = response
        state["next_agent"] = "end"
        return state
    
    # Format results for the LLM
    formatted_results = []
    for idx, result in enumerate(results, 1):
        formatted_results.append(f"""
Listing {idx}:
- Name: {result.get('name', 'N/A')}
- Type: {result.get('property_type', 'N/A')}
- Location: {result.get('address', {}).get('market', 'N/A')}
- Bedrooms: {result.get('bedrooms', 'N/A')} | Beds: {result.get('beds', 'N/A')}
- Price: ${result.get('price', 'N/A')}/night
- Amenities: {', '.join(result.get('amenities', [])[:8])}
- Description: {result.get('summary', result.get('description', ''))[:200]}...
- Match Score: {result.get('searchScore', 0):.4f}
""")
    
    context = "\n".join(formatted_results)
    
    # Create recommendation prompt
    rec_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly accommodation recommendation specialist.

Your task:
1. Analyze the retrieved listings against the user's query
2. Recommend the top 2-3 listings that best match their needs
3. Explain WHY each listing is a good match
4. Highlight key features (price, location, amenities)
5. Provide a clear, enthusiastic, conversational response

Guidelines:
- Be specific about what makes each listing suitable
- Mention the price and any standout amenities
- If all listings are similar quality, recommend based on best value
- End with a helpful question or next step suggestion
- Keep response concise (3-4 paragraphs total)

User's Query: {query}
Extracted Filters: {filters}

Available Listings:
{context}"""),
        ("human", "Provide your recommendations based on the listings above.")
    ])
    
    # Generate recommendation
    chain = rec_prompt | llm | StrOutputParser()
    response = chain.invoke({
        "query": query,
        "filters": filters,
        "context": context
    })
    
    print(f"💡 Recommendation Agent: Generated personalized response")
    
    # Update state
    state["final_response"] = response
    state["next_agent"] = "end"
    
    return state

print("✅ Recommendation Agent created")
```

### Agent 4: Supervisor Agent

```python
def supervisor_agent(state: AgentState) -> AgentState:
    """
    Route tasks to the appropriate agent based on conversation state.
    
    Responsibilities:
    - Analyze the current state and user query
    - Decide which agent should handle the task
    - Handle edge cases and errors
    """
    query = state.get("current_query", "")
    
    # Determine routing logic
    if not state.get("filters"):
        # No filters extracted yet, go to filter agent
        state["next_agent"] = "filter"
        print("📋 Supervisor: Routing to Filter Agent")
    elif not state.get("search_results"):
        # Filters exist but no search yet, go to search agent
        state["next_agent"] = "search"
        print("📋 Supervisor: Routing to Search Agent")
    elif not state.get("final_response"):
        # Have results but no recommendation yet, go to recommendation agent
        state["next_agent"] = "recommend"
        print("📋 Supervisor: Routing to Recommendation Agent")
    else:
        # Everything is done
        state["next_agent"] = "end"
        print("📋 Supervisor: Task complete")
    
    return state

print("✅ Supervisor Agent created")
```

## 🛠️ Step 4: Build the LangGraph Workflow

### Create the State Graph

```python
def create_agent_graph():
    """
    Create the LangGraph workflow that orchestrates all agents.
    """
    # Initialize the graph with state
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("filter", filter_agent)
    workflow.add_node("search", search_agent)
    workflow.add_node("recommend", recommendation_agent)
    
    # Define the routing logic
    def route_agent(state: AgentState) -> str:
        """Determine which agent to call next."""
        next_agent = state.get("next_agent", "end")
        
        if next_agent == "end":
            return END
        return next_agent
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add edges (transitions between agents)
    workflow.add_conditional_edges(
        "supervisor",
        route_agent,
        {
            "filter": "filter",
            "search": "search",
            "recommend": "recommend",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "filter",
        route_agent,
        {
            "search": "search",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "search",
        route_agent,
        {
            "recommend": "recommend",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "recommend",
        route_agent,
        {
            END: END
        }
    )
    
    # Compile the graph
    memory = MemorySaver()  # Enables conversation persistence
    app = workflow.compile(checkpointer=memory)
    
    return app

# Create the graph
agent_graph = create_agent_graph()

print("✅ Multi-agent graph created and compiled")
```

### Visualize the Graph

```python
# Optional: Visualize the workflow
try:
    from IPython.display import Image, display
    
    # Generate graph visualization
    graph_image = agent_graph.get_graph().draw_mermaid_png()
    display(Image(graph_image))
    print("📊 Agent workflow visualization displayed")
except Exception as e:
    print(f"ℹ️ Visualization requires graphviz: {e}")
```

## 🛠️ Step 5: Run the Multi-Agent System

### Execute a Query

```python
def run_multi_agent_query(query: str, session_id: str = "default") -> dict:
    """
    Execute a query through the multi-agent system.
    
    Args:
        query: User's natural language query
        session_id: Conversation session identifier
        
    Returns:
        dict: Final state with response and metadata
    """
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "current_query": query,
        "filters": {},
        "search_results": [],
        "next_agent": "supervisor",
        "final_response": "",
        "session_id": session_id
    }
    
    # Configuration for checkpointing
    config = {"configurable": {"thread_id": session_id}}
    
    print(f"\n{'='*80}")
    print(f"🚀 Starting Multi-Agent Query")
    print(f"{'='*80}")
    print(f"📝 Query: {query}")
    print(f"🔑 Session: {session_id}")
    print(f"{'='*80}\n")
    
    # Run the graph
    final_state = agent_graph.invoke(initial_state, config)
    
    print(f"\n{'='*80}")
    print(f"✅ Multi-Agent Processing Complete")
    print(f"{'='*80}\n")
    
    return final_state

# Test the system
result = run_multi_agent_query(
    query="Find me a pet-friendly 3 bedroom house in Chicago under $200",
    session_id="test_user_1"
)

# Display the response
print("🤖 Final Response:")
print("-" * 80)
print(result["final_response"])
print("-" * 80)

# Show extracted filters
print(f"\n🔍 Extracted Filters: {result['filters']}")
print(f"📊 Search Results Count: {len(result['search_results'])}")
```

**Expected Output:**
```
================================================================================
🚀 Starting Multi-Agent Query
================================================================================
📝 Query: Find me a pet-friendly 3 bedroom house in Chicago under $200
🔑 Session: test_user_1
================================================================================

📋 Supervisor: Routing to Filter Agent
🔍 Filter Agent: Extracted filters: {'bedrooms': 3, 'property_type': 'House', 'location': 'Chicago', 'price_max': 200, 'amenities': ['Pet-friendly']}
📋 Supervisor: Routing to Search Agent
🔎 Search Agent: Found 5 listings
📋 Supervisor: Routing to Recommendation Agent
💡 Recommendation Agent: Generated personalized response

================================================================================
✅ Multi-Agent Processing Complete
================================================================================

🤖 Final Response:
--------------------------------------------------------------------------------
I found some excellent pet-friendly houses in Chicago that fit your criteria perfectly!

**Top Recommendation: Lincoln Park Family House** - $185/night ⭐
This 3-bedroom house is my top pick! It welcomes pets and features a fenced backyard—
perfect for your furry friends. Located in the family-friendly Lincoln Park neighborhood 
with easy access to parks and trails. Includes WiFi, full kitchen, parking, and a 
washer/dryer. Well under your $200 budget!

**Runner-Up: Wicker Park Pet Paradise** - $195/night
Another fantastic option! This charming 3-bedroom house has a dedicated pet washing 
station and is steps from dog-friendly cafes. Modern amenities throughout and a great 
location for exploring the city.

Both properties are highly rated by pet owners. The Lincoln Park house offers better 
value and more outdoor space. Would you like to see photos or check availability?
--------------------------------------------------------------------------------

🔍 Extracted Filters: {'bedrooms': 3, 'property_type': 'House', 'location': 'Chicago', 'price_max': 200, 'amenities': ['Pet-friendly']}
📊 Search Results Count: 5
```

## 🛠️ Step 6: Add Conversation Continuity

### Handle Follow-up Questions

```python
def multi_agent_chat(query: str, session_id: str) -> str:
    """
    Chat interface that handles follow-up questions using conversation memory.
    
    Args:
        query: User's message
        session_id: Conversation session ID
        
    Returns:
        str: Assistant's response
    """
    result = run_multi_agent_query(query, session_id)
    return result["final_response"]

# Test conversation with follow-ups
print("\n" + "="*80)
print("💬 Multi-Agent Conversation Test")
print("="*80)

session = "conversation_test_1"

# First query
q1 = "I need a place in Boston for a business trip"
r1 = multi_agent_chat(q1, session)
print(f"\n👤 User: {q1}")
print(f"\n🤖 Assistant:\n{r1}\n")

# Follow-up
print("-"*80)
q2 = "Does the first one have a workspace?"
r2 = multi_agent_chat(q2, session)
print(f"\n👤 User: {q2}")
print(f"\n🤖 Assistant:\n{r2}\n")

# Another follow-up
print("-"*80)
q3 = "What about parking?"
r3 = multi_agent_chat(q3, session)
print(f"\n👤 User: {q3}")
print(f"\n🤖 Assistant:\n{r3}\n")
```

## 🛠️ Step 7: Advanced Features

### Add Error Handling Agent

```python
def error_handler_agent(state: AgentState) -> AgentState:
    """
    Handle errors and provide helpful fallback responses.
    """
    if not state.get("search_results"):
        state["final_response"] = """I couldn't find any listings matching those exact criteria. 
        
Here are some suggestions:
- Try expanding your search area
- Increase your budget slightly
- Reduce the number of required bedrooms
- Check different dates if you're flexible

Would you like me to search with adjusted criteria?"""
        state["next_agent"] = "end"
    
    return state

print("✅ Error Handler Agent created")
```

### Add Clarification Agent

```python
def clarification_agent(state: AgentState) -> AgentState:
    """
    Ask clarifying questions for vague queries.
    """
    query = state["current_query"]
    
    # Check if query is too vague
    vague_prompt = ChatPromptTemplate.from_messages([
        ("system", """Determine if this query is too vague to search for accommodations.
        
A query is vague if it lacks:
- Location
- Budget indication
- Bedroom/size requirements
- Any specific needs

Reply with only 'YES' or 'NO'."""),
        ("human", "{query}")
    ])
    
    chain = vague_prompt | llm | StrOutputParser()
    is_vague = "yes" in chain.invoke({"query": query}).lower()
    
    if is_vague:
        # Generate clarifying questions
        clarify_prompt = ChatPromptTemplate.from_messages([
            ("system", """The user's query is vague. Ask 2-3 specific clarifying questions to help them.
            
Focus on:
- Where do you want to stay? (city/neighborhood)
- What's your budget per night?
- How many bedrooms do you need?
- Any must-have amenities?

Be friendly and conversational."""),
            ("human", "User said: {query}")
        ])
        
        chain = clarify_prompt | llm | StrOutputParser()
        response = chain.invoke({"query": query})
        
        state["final_response"] = response
        state["next_agent"] = "end"
        print("❓ Clarification Agent: Query too vague, asking for details")
    else:
        # Query is clear enough, proceed normally
        state["next_agent"] = "filter"
        print("✅ Clarification Agent: Query is sufficiently detailed")
    
    return state

print("✅ Clarification Agent created")
```

### Update Graph with New Agents

```python
def create_enhanced_agent_graph():
    """
    Create an enhanced multi-agent graph with error handling and clarification.
    """
    workflow = StateGraph(AgentState)
    
    # Add all agents
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("clarification", clarification_agent)
    workflow.add_node("filter", filter_agent)
    workflow.add_node("search", search_agent)
    workflow.add_node("recommend", recommendation_agent)
    workflow.add_node("error_handler", error_handler_agent)
    
    # Routing function
    def route_agent(state: AgentState) -> str:
        next_agent = state.get("next_agent", "end")
        if next_agent == "end":
            return END
        return next_agent
    
    # Entry point: start with clarification
    workflow.set_entry_point("clarification")
    
    # Add edges
    workflow.add_conditional_edges(
        "clarification",
        route_agent,
        {
            "filter": "filter",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "supervisor",
        route_agent,
        {
            "filter": "filter",
            "search": "search",
            "recommend": "recommend",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "filter",
        route_agent,
        {
            "search": "search",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "search",
        route_agent,
        {
            "recommend": "recommend",
            "error_handler": "error_handler",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "recommend",
        route_agent,
        {
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "error_handler",
        route_agent,
        {
            END: END
        }
    )
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

# Create enhanced graph
enhanced_graph = create_enhanced_agent_graph()

print("✅ Enhanced multi-agent graph created")
```

## 🎓 What You've Learned

✅ **Multi-Agent Architecture**: Designing systems with specialized agents  
✅ **LangGraph**: Building stateful workflows with state graphs  
✅ **Agent Orchestration**: Routing tasks intelligently between agents  
✅ **State Management**: Sharing data across multiple agents  
✅ **Conversation Memory**: Maintaining context across interactions  
✅ **Error Handling**: Gracefully managing edge cases  
✅ **Production Patterns**: Building robust, maintainable AI systems  

## 🚀 Challenge: Enhance the Multi-Agent System

### Challenge 1: Add a Booking Agent (Medium)
Create an agent that handles booking confirmations and next steps.

**Requirements:**
- Trigger when user expresses interest (e.g., "I'll take it", "Book this one")
- Provide booking information (how to reserve, payment, cancellation policy)
- Generate a booking summary

<details>
<summary>💡 Hint</summary>

```python
def booking_agent(state: AgentState) -> AgentState:
    """Handle booking requests and provide next steps."""
    query = state["current_query"].lower()
    
    # Check if user wants to book
    intent_prompt = """Is the user trying to book/reserve an accommodation?
    Reply YES or NO.
    
    User message: {query}"""
    
    # If yes, generate booking instructions
    booking_prompt = """The user wants to book a listing. Provide helpful next steps:
    1. Confirm which listing they're interested in
    2. Explain the booking process
    3. Mention key policies (cancellation, payment, check-in)
    4. Provide a call-to-action
    
    Be enthusiastic and helpful!"""
    
    # Implementation here
    pass
```
</details>

### Challenge 2: Add Price Negotiation Agent (Advanced)
Implement an agent that suggests alternatives when listings are over budget.

**Requirements:**
- Detect when all results exceed user's budget
- Suggest nearby alternatives or different dates
- Explain value propositions for slightly pricier options

<details>
<summary>💡 Hint</summary>

```python
def negotiation_agent(state: AgentState) -> AgentState:
    """Suggest alternatives when results don't match budget."""
    filters = state.get("filters", {})
    results = state.get("search_results", [])
    
    price_max = filters.get("price_max")
    
    if price_max and results:
        # Check if all results are over budget
        all_over_budget = all(r.get("price", 0) > price_max for r in results)
        
        if all_over_budget:
            # Generate alternative suggestions
            prompt = """All listings are slightly over the user's ${price_max} budget.
            
Suggest alternatives:
1. Explain the value of slightly pricier options
2. Suggest reducing bedrooms or amenities
3. Recommend nearby areas with lower prices
4. Mention flexibility (weekday vs weekend rates)

Be helpful, not pushy."""
            
            # Generate response
            pass
```
</details>

### Challenge 3: Add Analytics Agent (Hard)
Create an agent that analyzes user preferences and provides market insights.

**Requirements:**
- Track what users search for across sessions
- Provide insights (e.g., "Listings in this area typically cost $150-200")
- Suggest optimal times to book based on pricing trends

**This requires:**
- Database to store search analytics
- Aggregation queries for insights
- Trend analysis logic

### Challenge 4: Multi-Modal Agent (Very Advanced)
Add an agent that can analyze listing images.

**Requirements:**
- Use GPT-4 Vision or similar to analyze property photos
- Describe visual features (modern, cozy, spacious, etc.)
- Match visual style to user preferences

<details>
<summary>💡 Hint</summary>

Requires:
- Image URLs in your dataset
- OpenAI Vision API or similar multimodal model
- Image downloading and preprocessing logic
</details>

## 🎯 Bonus Challenge: Human-in-the-Loop

Implement a pattern where the system asks for human approval before booking.

**Requirements:**
- After recommendation, ask "Would you like to proceed?"
- Wait for explicit user confirmation
- Support "show me more options" to continue searching

This teaches you about **interactive agent loops** and **conditional workflows**.

## 📊 Performance Considerations

### Optimize Agent Performance

```python
# 1. Parallel Agent Execution (for independent agents)
from langgraph.graph import ParallelNode

# Execute filter and clarification in parallel
workflow.add_node("parallel_start", ParallelNode([
    clarification_agent,
    filter_agent
]))

# 2. Caching for repeated searches
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query_hash: str):
    """Cache search results for identical queries."""
    # Implementation
    pass

# 3. Streaming responses (for real-time UI updates)
async def stream_agent_response(query: str, session_id: str):
    """Stream agent responses as they're generated."""
    config = {"configurable": {"thread_id": session_id}}
    
    async for event in enhanced_graph.astream_events(initial_state, config):
        if event["event"] == "on_chat_model_stream":
            yield event["data"]["chunk"]
```

## 📖 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems Guide](https://python.langchain.com/docs/use_cases/multi_agent/)
- [State Management Patterns](https://langchain-ai.github.io/langgraph/concepts/state/)
- [Agent Architectures](https://blog.langchain.dev/langgraph-multi-agent-workflows/)

## ✅ Checkpoint

Before completing the workshop, ensure you have:

- [ ] Built a multi-agent system with specialized agents
- [ ] Implemented agent orchestration with LangGraph
- [ ] Created a supervisor agent for task routing
- [ ] Managed shared state across agents
- [ ] Added conversation memory and continuity
- [ ] Tested with complex multi-turn conversations
- [ ] Implemented error handling
- [ ] Completed at least one challenge exercise

## 🎉 Workshop Complete!

Congratulations! You've built a sophisticated AI-powered application with:

✅ **Vector Search** - Semantic search with DocumentDB cosmosSearch  
✅ **RAG Pattern** - Context-aware AI responses with LangChain  
✅ **Multi-Agent System** - Specialized agents orchestrated with LangGraph  

### What You Can Build Next:

1. **Deploy to Production**
   - Containerize with Docker
   - Deploy to Azure Container Apps or Kubernetes
   - Add authentication and rate limiting
   - Implement monitoring and logging

2. **Add More Features**
   - Image analysis with vision models
   - Voice input/output with Whisper and TTS
   - Multi-language support
   - Mobile app integration

3. **Scale the System**
   - Add more agent types (booking, customer service, analytics)
   - Implement agent collaboration patterns
   - Build agent testing and evaluation frameworks
   - Create agent performance dashboards

### Key Takeaways:

🎯 **Vector Search** enables semantic understanding beyond keywords  
🎯 **RAG Pattern** grounds AI responses in your real data  
🎯 **Multi-Agent Systems** make complex AI applications maintainable  
🎯 **LangGraph** provides powerful orchestration for stateful workflows  

---

**🌟 Thank you for participating in this workshop!**

**💬 Questions or Feedback?**  
Reach out to your instructor or check the GitHub repository for updates and additional examples!

**🔗 Connect & Share:**  
Share what you built with #ContosoBookings #VectorSearch #MultiAgentAI

