# Module 3: Multi-Agent System with LangGraph

### You'll be editing: [`src/api/agents.py`](../src/api/agents.py)
### Solution: [`solutions/agents_solution.py`](../solutions/agents_solution.py) — check here if you get stuck

## Learning Objectives

By the end of this module, you will:
- Understand how a multi-agent system routes and processes queries
- Implement filter and ranking logic for agent tools
- Add LLM-powered routing, filter extraction, and response generation
- Test each enhancement incrementally with immediate feedback

## What You'll Build

The multi-agent scaffold in `agents.py` already works — it searches, recommends, and responds using hardcoded placeholder logic. Your job is to make it **intelligent** by filling in TODO blocks with LLM-powered implementations.

### Before vs. After

| Behavior | Before (placeholder) | After (your code) |
|----------|---------------------|-------------------|
| Routing | Always routes to search | LLM decides: search vs. respond |
| Filtering | No filters applied | LLM extracts price, bedrooms, amenities from query |
| Ranking | Returns first 5 results | Ranks by budget, quality, or balanced preference |
| Response | Raw listing dump | Friendly conversational answer |

### Example Multi-Agent Conversation (after all exercises):

```
User: "I need a place with a kitchen, 2 bedrooms, under $200"

[Supervisor routes to Search]
Search Agent: Performs vector search -> Returns 20 listings

[Search routes to Filter]
Filter Agent: Extracts "kitchen, 2 bedrooms, under $200" -> Applies filters -> 8 remain

[Filter routes to Recommend]
Recommend Agent: Ranks by balanced preference -> Top 5

[Recommend routes to Respond]
Respond Agent:
"Based on your needs, I recommend:

1. **Cozy Cottage in LoHi** - $161/night
   Perfect match! This 2-bedroom guesthouse has a full kitchen and great reviews.

2. **Spacious Apartment near Downtown** - $175/night
   Excellent value! Fully equipped kitchen and close to restaurants.

Both are well under your $200 budget. Interested in booking?"
```

---

## Concept: Multi-Agent Systems

### What are Multi-Agent Systems?

A multi-agent system uses multiple specialized AI agents that:
- Each handle specific tasks they're optimized for
- Communicate and coordinate through shared state
- Work together to solve complex problems

### Architecture of Our System

```
    [START]
       |
  [Supervisor]  ── decides: search or respond?
       |
  ┌────┴──────────────┐
  v                   v
[Search]          [Respond] --> [END]
  |
[Filter]   ── extracts constraints from query
  |
[Recommend]  ── ranks by preference
  |
[Respond]  ── generates friendly answer
  |
[END]
```

### LangGraph Key Concepts

| Concept | Description |
|---------|-------------|
| **StateGraph** | A directed graph where nodes are functions and edges define transitions |
| **State (TypedDict)** | A shared dictionary passed between all nodes |
| **Nodes** | Async functions that take state, do work, and return updated fields |
| **Edges** | Transitions between nodes — can be direct or conditional |

---

## Step 1: Explore the Scaffold

Before writing code, understand what's already built for you.

### 1a. Verify the system works

The multi-agent system should work out of the box with placeholder logic. Check:

```bash
curl http://localhost:8000/health | python -m json.tool
```

Look for `"multi_agent": true`. If it's `false`, restart the backend:
```bash
pkill -f uvicorn
cd /workspaces/booking-agents-sample && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 1b. Test the placeholder behavior

```bash
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me apartments in Denver", "session_id": "test1"}' | python -m json.tool
```

You should see:
- `"multi_agent": true` — the agent graph is running
- `"search_results"` — listings returned (unfiltered, unranked)
- `"message"` — a raw listing dump (not conversational yet)

This is the **baseline**. Each exercise you complete will improve the output.

### 1c. Review the scaffold

Open [`src/api/agents.py`](../src/api/agents.py) and note the structure:

| Section | Status | What it does |
|---------|--------|-------------|
| `AgentState` | Provided | Shared state definition with 7 fields |
| `apply_filters` | **Exercise 1a** | TODO: add filter conditions |
| `get_recommendations` | **Exercise 1b** | TODO: add ranking strategies |
| `create_llm()` | Provided | Creates the ChatOpenAI instance |
| `supervisor_node` | **Exercise 2a** | TODO: replace hardcoded routing with LLM |
| `search_node` | Provided | Finds listings via vector search |
| `filter_node` | **Exercise 2b** | TODO: replace hardcoded `{}` with LLM filter extraction |
| `recommend_node` | **Exercise 3a** | TODO: replace hardcoded "balanced" with LLM preference detection |
| `respond_node` | **Exercise 3b** | TODO: replace raw listing dump with LLM response |
| `build_agent_graph()` | Provided | Wires nodes into the LangGraph pipeline |
| `run_agent_query()` | Provided | Public interface called by the API |

---

## Step 2: Exercise 1 — Implement the Tools

**Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the `Exercise 1a` and `Exercise 1b` TODO blocks

### Exercise 1a: `apply_filters`

The function receives a list of listings and optional filter parameters. Currently it returns all listings unfiltered. Add the filter conditions.

**For each parameter that is not `None`, remove non-matching listings:**

| Parameter | Condition |
|-----------|-----------|
| `max_price` | Keep where `price <= max_price` |
| `property_type` | Keep where `property_type` contains the string (case-insensitive) |
| `min_bedrooms` | Keep where `bedrooms >= min_bedrooms` |
| `amenities` | Keep where ALL required amenities are present (case-insensitive) |

<details>
<summary>Solution</summary>

```python
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
```

</details>

### Exercise 1b: `get_recommendations`

The function receives listings and a preference string. Currently it returns the first 5. Add ranking strategies.

| Preference | Strategy |
|-----------|----------|
| `"budget"` | Sort by price ascending, return top 5 |
| `"quality"` | Sort by score descending, return top 5 |
| `"balanced"` | Rank = `score - (price / 500.0)`, sort descending, return top 5 |

<details>
<summary>Solution</summary>

```python
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

### Test Exercise 1

The tools are used by the filter and recommend nodes. Since filter extraction is still hardcoded (Exercise 2), test ranking directly:

```bash
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me the cheapest places in Denver", "session_id": "ex1"}' | python -m json.tool
```

Check the `search_results` — the listings should now be sorted by the "balanced" ranking strategy (the default). Before Exercise 1, they were in arbitrary order.

---

## Step 3: Exercise 2 — Add LLM Routing and Filter Extraction

**Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the `Exercise 2a` and `Exercise 2b` TODO blocks

### Exercise 2a: `supervisor_node` — LLM Routing

Currently the supervisor always routes to `"search"`. Replace with an LLM call that decides between `"search"` and `"respond"`.

**Steps:**
1. Call `create_llm()` to get an LLM instance
2. Build a system prompt explaining the two routing options
3. Send `[SystemMessage(prompt), HumanMessage(state['user_query'])]` with `await llm.ainvoke(messages)`
4. Parse: `next_agent = response.content.strip().lower()`
5. Validate: if not in `('search', 'respond')`, default to `'search'`

<details>
<summary>Solution</summary>

```python
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

    if next_agent not in ('search', 'respond'):
        next_agent = 'search'
```

</details>

### Exercise 2b: `filter_node` — LLM Filter Extraction

Currently the filter node uses `filters = {}` (no filters). Replace with an LLM call that extracts constraints from the query as JSON.

**Steps:**
1. Call `create_llm()`
2. Build a system prompt asking the LLM to extract filter criteria as JSON:
   - `max_price` (number), `property_type` (string), `min_bedrooms` (integer), `amenities` (array)
   - Return `{}` if no clear filters
3. Send the prompt with `await llm.ainvoke(messages)`
4. Parse: `filters = json.loads(response.content)`
5. Wrap in try/except for JSON parse errors

**Important:** After parsing, the existing code below the TODO block handles applying the filters and returning the result. You just need to replace `filters = {}` with the LLM extraction.

<details>
<summary>Solution</summary>

```python
    llm = create_llm()

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
    except Exception as e:
        logger.error(f"Filter extraction error: {e}")
        filters = {}
```

</details>

### Test Exercise 2

**Test routing:**
```bash
# Should route to "respond" (no search needed)
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, what can you help me with?", "session_id": "ex2a"}' | python -m json.tool
```
Check `agent_path` — it should show `["respond"]` instead of `["search"]`.

**Test filter extraction:**
```bash
# Should extract filters and narrow results
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "2 bedroom place under $150 with wifi", "session_id": "ex2b"}' | python -m json.tool
```
Check the `search_results` count — it should be less than 5 (filtered down from 20). All returned listings should have 2+ bedrooms, price ≤ $150, and wifi. Before this exercise, all 5 results passed through unfiltered.

```bash
# No explicit constraints — should NOT filter
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me places in Denver", "session_id": "ex2c"}' | python -m json.tool
```
Check that `search_results` has 5 results (no filtering applied). This verifies the LLM doesn't over-extract filters from general search terms.

---

## Step 4: Exercise 3 — Add LLM Ranking and Response

**Edit:** [`src/api/agents.py`](../src/api/agents.py) — find the `Exercise 3a` and `Exercise 3b` TODO blocks

### Exercise 3a: `recommend_node` — LLM Preference Detection

Currently uses `preference = "balanced"`. Replace with an LLM call that detects the user's ranking preference.

**Steps:**
1. Call `create_llm()`
2. Build a system prompt asking the LLM to determine the user's preference — respond with ONLY one word: `"budget"`, `"quality"`, or `"balanced"`
3. Send the prompt with `await llm.ainvoke(messages)`
4. Parse and validate — default to `"balanced"` if invalid

<details>
<summary>Solution</summary>

```python
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
        response = await llm.ainvoke(messages)
        preference = response.content.strip().lower()
        if preference not in ['budget', 'quality', 'balanced']:
            preference = 'balanced'
    except Exception as e:
        logger.error(f"Preference detection error: {e}")
        preference = 'balanced'
```

</details>

### Exercise 3b: `respond_node` — LLM Conversational Response

Currently returns a raw listing dump. Replace with an LLM call that generates a friendly, conversational response.

**Steps:**
1. Call `create_llm()`
2. Build a system prompt telling the LLM to be a friendly booking assistant. Include `listings_context` as the available search results. Ask it to mention 2-3 top options and keep under 200 words.
3. Send `[SystemMessage(prompt), HumanMessage(state['user_query'])]` with `await llm.ainvoke(messages)`
4. Return `{'final_response': response.content}`
5. On error, fall back to the raw `listings_context` string

**Note:** Replace the entire `return` statement at the bottom of the TODO block.

<details>
<summary>Solution</summary>

```python
    llm = create_llm()

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
```

</details>

### Test Exercise 3

```bash
# Should detect "budget" preference and return cheapest first
curl -s -X POST http://localhost:8000/query_message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the cheapest place available?", "session_id": "ex3"}' | python -m json.tool
```

Check the `message` field — it should now be a friendly, conversational response mentioning specific listings by name, instead of a raw bullet-point dump.

---

## Step 5: Integration Test

Open http://localhost:3000 and test the full system in the chat panel:

1. **Full pipeline**: "2-bedroom apartment with kitchen and parking, under $200"
2. **Budget preference**: "What's the cheapest place available?"
3. **Direct response**: "Hello, what can you help me with?"
4. **Follow-up filter**: "Show me places near downtown" then "Only ones with wifi"

### What to check for

| Working | Possible Issue |
|---------|---------------|
| Response mentions specific listings by name | Check Exercise 3b — is the LLM prompt correct? |
| Filter constraints applied (fewer results) | Check Exercise 2b — is JSON parsing working? |
| Budget queries return cheapest first | Check Exercise 3a — is preference detection working? |
| "Hello" gets a direct response (no search) | Check Exercise 2a — is supervisor routing to "respond"? |
| Listings appear on the map | Check that `search_results` is non-empty in the API response |

---

## What You've Learned

- **Multi-Agent Architecture**: How specialized agents coordinate through shared state
- **LangGraph**: Building stateful workflows with `StateGraph`, nodes, and edges
- **Fill-in-the-Blanks Pattern**: Working with a scaffold — understanding infrastructure before adding logic
- **LLM Prompting**: Writing system prompts for routing, extraction, and generation
- **Incremental Testing**: Verifying each enhancement independently

---

## Challenges

### Challenge 1: Add a Clarification Agent (Medium)

Create an agent that detects vague queries and asks clarifying questions before searching.

**Requirements:**
- Use the LLM to determine if a query is too vague (missing location, budget, size)
- If vague, generate 2-3 clarifying questions and set as `final_response`
- If detailed enough, route to the search pipeline

Add a new `clarification_node` and wire it into `build_agent_graph()` between supervisor and search.

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

- "Find me places in Denver" -> searches normally
- "Do any of those have parking?" -> references previous results

**Hint:** Use `MemorySaver` from LangGraph and pass a `thread_id` config when invoking the graph.

---

## Checkpoint

Before completing the workshop, ensure you have:

- [ ] Verified the scaffold works out of the box (Step 1)
- [ ] Implemented `apply_filters` with all 4 filter conditions (Exercise 1a)
- [ ] Implemented `get_recommendations` with 3 ranking strategies (Exercise 1b)
- [ ] Added LLM routing in `supervisor_node` (Exercise 2a)
- [ ] Added LLM filter extraction in `filter_node` (Exercise 2b)
- [ ] Added LLM preference detection in `recommend_node` (Exercise 3a)
- [ ] Added LLM response generation in `respond_node` (Exercise 3b)
- [ ] Tested the full system in the frontend

## Workshop Complete!

Congratulations! You've built a sophisticated AI-powered application with:

- **Vector Search** (Module 1) — Semantic search with DocumentDB cosmosSearch
- **RAG Pattern** (Module 2) — Context-aware AI responses with LangChain
- **Multi-Agent System** (Module 3) — Specialized agents orchestrated with LangGraph

---

**Stuck?** Compare your code with [`solutions/agents_solution.py`](../solutions/agents_solution.py) or ask your instructor for help!
