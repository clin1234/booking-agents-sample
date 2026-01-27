# Module 2: RAG Pattern Implementation

## 📋 Learning Objectives

By the end of this module, you will:
- Understand the Retrieval-Augmented Generation (RAG) pattern
- Build a custom retriever using vector search results
- Implement conversational AI with LangChain
- Create context-aware prompts for better AI responses
- Handle conversation memory and follow-up questions
- Structure AI responses for a chat interface

## 🎯 What You'll Build

You'll build a conversational AI assistant that helps users find Airbnb listings through natural language chat. The assistant will:
- Understand user preferences and requirements
- Retrieve relevant listings using vector search
- Generate personalized recommendations with explanations
- Remember conversation context for follow-up questions

### Example Conversation:

```
User: "I'm looking for a place in Chicago for a weekend getaway"

AI: "I found some great options in Chicago! Here are my top recommendations:

1. **Cozy Loft in Wicker Park** - $125/night
   Perfect for a weekend escape! This modern loft features exposed brick, 
   a fully equipped kitchen, and is walking distance to trendy restaurants 
   and nightlife.

2. **Sunny Studio near Navy Pier** - $95/night
   Great location for tourists! Close to Lake Michigan and downtown attractions.
   
Would you like more details about any of these, or should I search with 
different criteria?"

User: "The loft sounds nice. Does it have parking?"

AI: "Yes! The Cozy Loft in Wicker Park includes free street parking. It also 
has WiFi, a smart TV, and a workspace if you need to do any remote work during 
your stay. The neighborhood is very walkable, so you might not even need your 
car much. Would you like to see the full listing details or explore other options?"
```

## 📚 Concept: Retrieval-Augmented Generation (RAG)

### What is RAG?

RAG is a pattern that combines:
1. **Retrieval**: Finding relevant information from a knowledge base (our vector search)
2. **Augmentation**: Adding that information to the AI's context
3. **Generation**: Using an LLM to generate responses based on the retrieved context

### Why RAG?

Without RAG:
- ❌ AI only knows what it was trained on (outdated, generic)
- ❌ Can't answer questions about your specific data
- ❌ May "hallucinate" or make up information

With RAG:
- ✅ AI has access to your current, specific data
- ✅ Responses are grounded in real information
- ✅ Can cite sources and provide accurate details
- ✅ Knowledge base is updateable without retraining

### RAG Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User Query                                                  │
│  ┌──────────────────┐                                          │
│  │ "Find cozy       │                                          │
│  │  apartments in   │                                          │
│  │  Chicago"        │                                          │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           ▼                                                     │
│  2. Retrieval (Vector Search)                                  │
│  ┌──────────────────┐         ┌─────────────────┐            │
│  │ Convert query    │────────▶│ Search DocumentDB│            │
│  │ to embedding     │         │ for similar     │            │
│  └──────────────────┘         │ listings        │            │
│                                └────────┬────────┘            │
│                                         │                      │
│                                         ▼                      │
│  3. Context Assembly                                           │
│  ┌──────────────────────────────────────────┐                │
│  │ Top 5 listings:                          │                │
│  │ 1. Loft in Wicker Park - $125           │                │
│  │ 2. Studio near Navy Pier - $95          │                │
│  │ ...                                      │                │
│  └────────┬─────────────────────────────────┘                │
│           │                                                     │
│           ▼                                                     │
│  4. Augmentation (Prompt Engineering)                          │
│  ┌──────────────────────────────────────────┐                │
│  │ System: You are a helpful assistant...   │                │
│  │                                           │                │
│  │ Context: [Retrieved listings]            │                │
│  │                                           │                │
│  │ User Question: [Original query]          │                │
│  └────────┬─────────────────────────────────┘                │
│           │                                                     │
│           ▼                                                     │
│  5. Generation (LLM)                                           │
│  ┌──────────────────┐                                         │
│  │ OpenAI GPT       │                                         │
│  │ gpt-3.5-turbo    │                                         │
│  └────────┬─────────┘                                         │
│           │                                                     │
│           ▼                                                     │
│  6. Response                                                    │
│  ┌──────────────────────────────────────────┐                │
│  │ "I found some great options in Chicago!  │                │
│  │  Here are my top recommendations..."     │                │
│  └──────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Step 1: Set Up Environment

### Import Required Libraries

```python
import os
from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseRetriever, Document
from langchain.schema.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Initialize connections
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

DOCUMENTDB_CONNECTION_STRING = os.getenv('DOCUMENTDB_CONNECTION_STRING')
mongo_client = MongoClient(DOCUMENTDB_CONNECTION_STRING)
db = mongo_client['contoso_bookings']
collection = db['listings']

# Initialize LangChain components
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,  # Balance between creativity and consistency
    api_key=os.getenv('OPENAI_API_KEY')
)

print("✅ Environment initialized")
print(f"📊 Database: {collection.count_documents({})} listings available")
```

### 💡 Understanding Temperature

- **Temperature = 0**: Deterministic, consistent responses (good for factual Q&A)
- **Temperature = 0.7**: Balanced creativity and consistency (good for conversations)
- **Temperature = 1.0+**: More creative, varied responses (good for brainstorming)

## 🛠️ Step 2: Create a Custom Retriever

LangChain uses "retrievers" to fetch relevant documents. We'll create a custom retriever that uses our vector search.

### Implement the Custom Retriever

```python
from typing import List

class CustomDocumentDBRetriever(BaseRetriever):
    """
    Custom retriever that uses DocumentDB vector search to find relevant listings.
    """
    
    def __init__(self, collection, openai_client, top_k=5):
        """
        Initialize the retriever.
        
        Args:
            collection: MongoDB collection with vector search index
            openai_client: OpenAI client for generating embeddings
            top_k: Number of results to retrieve
        """
        self.collection = collection
        self.openai_client = openai_client
        self.top_k = top_k
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents for the given query.
        
        Args:
            query: The search query
            
        Returns:
            List of LangChain Document objects
        """
        # Generate embedding for the query
        query_embedding = self._generate_embedding(query)
        
        # Perform vector search
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": "descriptionVector",
                        "k": self.top_k
                    },
                    "returnStoredSource": True
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "name": 1,
                    "description": 1,
                    "summary": 1,
                    "space": 1,
                    "property_type": 1,
                    "bedrooms": 1,
                    "beds": 1,
                    "price": 1,
                    "amenities": 1,
                    "address": 1,
                    "searchScore": {"$meta": "searchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # Convert to LangChain Document format
        documents = []
        for result in results:
            # Create a formatted content string for the LLM
            content = f"""
Property: {result.get('name', 'N/A')}
Type: {result.get('property_type', 'N/A')}
Location: {result.get('address', {}).get('market', 'N/A')}, {result.get('address', {}).get('country', 'N/A')}
Bedrooms: {result.get('bedrooms', 'N/A')} | Beds: {result.get('beds', 'N/A')}
Price: ${result.get('price', 'N/A')} per night
Amenities: {', '.join(result.get('amenities', [])[:10])}
Description: {result.get('description', result.get('summary', 'N/A'))[:500]}
"""
            
            # Create Document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "id": str(result.get('_id', '')),
                    "name": result.get('name', ''),
                    "price": result.get('price', 0),
                    "location": result.get('address', {}).get('market', ''),
                    "similarity_score": result.get('searchScore', 0)
                }
            )
            documents.append(doc)
        
        return documents
    
    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version of _get_relevant_documents."""
        return self._get_relevant_documents(query)

# Initialize the retriever
retriever = CustomDocumentDBRetriever(
    collection=collection,
    openai_client=openai_client,
    top_k=5
)

# Test the retriever
test_docs = retriever._get_relevant_documents("cozy apartment near downtown")
print(f"\n✅ Retriever test successful")
print(f"📊 Retrieved {len(test_docs)} documents")
print(f"\n📄 First document preview:")
print(test_docs[0].page_content[:300] + "...")
```

**Expected Output:**
```
✅ Retriever test successful
📊 Retrieved 5 documents

📄 First document preview:

Property: Downtown Loft with City Views
Type: Apartment
Location: Chicago, United States
Bedrooms: 1 | Beds: 1
Price: $125.0 per night
Amenities: Wifi, Kitchen, Heating, Air conditioning, Washer, Dryer, TV, Coffee maker, Desk, Free parking
Description: Beautiful loft apartment in the heart of downtown...
```

## 🛠️ Step 3: Create the RAG Chain

Now we'll build a LangChain pipeline that combines retrieval and generation.

### Design the Prompt Template

```python
# System prompt that defines the AI's role and behavior
system_prompt = """You are a friendly and knowledgeable Airbnb assistant helping users find their perfect accommodation.

Your responsibilities:
- Analyze the user's requirements and preferences
- Recommend suitable listings from the provided context
- Explain why each listing matches their needs
- Be conversational, enthusiastic, and helpful
- If the user asks follow-up questions, use the conversation history to provide context-aware responses

Guidelines:
- Always base your recommendations on the retrieved listings context
- Highlight key features that match the user's stated preferences
- Mention price, location, and standout amenities
- If none of the listings are perfect matches, explain what's close and ask if they want to adjust criteria
- Keep responses concise but informative (2-4 sentences per listing)
- Use a friendly, conversational tone

Context with relevant listings:
{context}

Remember: Only recommend listings that appear in the context above. Do not make up or hallucinate listings."""

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{question}")
])

print("✅ Prompt template created")
```

### Build the RAG Chain

```python
def format_docs(docs: List[Document]) -> str:
    """Format retrieved documents into a readable context string."""
    if not docs:
        return "No relevant listings found."
    
    formatted = []
    for i, doc in enumerate(docs, 1):
        formatted.append(f"\n--- Listing {i} ---")
        formatted.append(doc.page_content)
        formatted.append(f"Similarity Score: {doc.metadata.get('similarity_score', 0):.4f}")
    
    return "\n".join(formatted)

# Create the RAG chain
rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
        "chat_history": lambda x: []  # We'll add memory in the next step
    }
    | prompt
    | llm
    | StrOutputParser()
)

print("✅ RAG chain created")
```

### Test the RAG Chain

```python
# Test with a simple query
test_question = "I'm looking for a cozy place in Chicago for a weekend getaway"
response = rag_chain.invoke(test_question)

print(f"\n🔍 Question: {test_question}")
print(f"\n🤖 Response:")
print(response)
```

**Expected Output:**
```
🔍 Question: I'm looking for a cozy place in Chicago for a weekend getaway

🤖 Response:
I found some wonderful options for your Chicago weekend getaway! Here are my top recommendations:

1. **Cozy Loft in Wicker Park** - $125/night
   This charming loft is perfect for a weekend escape! It features exposed brick walls, 
   modern amenities including WiFi and a full kitchen, plus it's in the trendy Wicker Park 
   neighborhood with easy access to great restaurants and nightlife.

2. **Sunny Studio near Navy Pier** - $95/night
   Great value for a cozy downtown experience! This studio is within walking distance of 
   Navy Pier and Lake Michigan, and includes all the essentials like WiFi, heating, and 
   a comfortable workspace.

3. **Artistic Apartment in Logan Square** - $110/night
   Perfect for a creative weekend! This unique space showcases local art and is located 
   in the vibrant Logan Square area, known for its craft breweries and live music venues.

Would you like more details about any of these properties, or should I search with different criteria?
```

## 🛠️ Step 4: Add Conversation Memory

To handle follow-up questions, we need to maintain conversation history.

### Implement Conversation Memory

```python
from typing import Dict, List, Tuple

class ConversationManager:
    """
    Manages conversation history and context for RAG interactions.
    """
    
    def __init__(self, rag_chain):
        """
        Initialize the conversation manager.
        
        Args:
            rag_chain: The LangChain RAG pipeline
        """
        self.rag_chain = rag_chain
        self.conversations: Dict[str, List[Tuple[str, str]]] = {}
    
    def get_history(self, session_id: str) -> List:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            List of LangChain message objects
        """
        if session_id not in self.conversations:
            return []
        
        messages = []
        for human_msg, ai_msg in self.conversations[session_id]:
            messages.append(HumanMessage(content=human_msg))
            messages.append(AIMessage(content=ai_msg))
        
        return messages
    
    def chat(self, session_id: str, question: str) -> str:
        """
        Process a chat message with conversation history.
        
        Args:
            session_id: Unique identifier for the conversation session
            question: User's question or message
            
        Returns:
            AI assistant's response
        """
        # Get conversation history
        chat_history = self.get_history(session_id)
        
        # Create chain input with history
        chain_input = {
            "question": question,
            "chat_history": chat_history
        }
        
        # Invoke the RAG chain
        # We need to reconstruct the chain with history support
        chain_with_history = (
            {
                "context": lambda x: retriever._get_relevant_documents(x["question"]) | RunnableLambda(format_docs),
                "question": lambda x: x["question"],
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        response = chain_with_history.invoke(chain_input)
        
        # Save to history
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append((question, response))
        
        return response
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            print(f"✅ Cleared history for session: {session_id}")
    
    def get_session_count(self, session_id: str) -> int:
        """Get the number of messages in a session."""
        return len(self.conversations.get(session_id, []))

# Initialize conversation manager
conversation_manager = ConversationManager(rag_chain)

print("✅ Conversation manager initialized")
```

### Test Conversation with Memory

```python
# Start a new conversation session
session_id = "user_123"

# First message
print("=" * 80)
print("💬 Conversation Test")
print("=" * 80)

question1 = "I need a place in Chicago with parking"
response1 = conversation_manager.chat(session_id, question1)
print(f"\n👤 User: {question1}")
print(f"\n🤖 Assistant:\n{response1}")

# Follow-up question (tests memory)
print("\n" + "-" * 80)
question2 = "Does the first one have a kitchen?"
response2 = conversation_manager.chat(session_id, question2)
print(f"\n👤 User: {question2}")
print(f"\n🤖 Assistant:\n{response2}")

# Another follow-up
print("\n" + "-" * 80)
question3 = "What about the price? Is it under $150?"
response3 = conversation_manager.chat(session_id, question3)
print(f"\n👤 User: {question3}")
print(f"\n🤖 Assistant:\n{response3}")

print("\n" + "=" * 80)
print(f"📊 Conversation length: {conversation_manager.get_session_count(session_id)} exchanges")
```

**Expected Output:**
```
================================================================================
💬 Conversation Test
================================================================================

👤 User: I need a place in Chicago with parking

🤖 Assistant:
Great news! I found several Chicago properties with parking available:

1. **Downtown Loft with Parking** - $125/night
   Perfect match! This modern loft includes free street parking and is located 
   in a walkable neighborhood near downtown. Features WiFi, a full kitchen, and 
   workspace.

2. **Family House with Garage** - $180/night
   This spacious 3-bedroom house comes with a private garage and driveway. Ideal 
   if you need secure parking and more space.

Would you like more information about either of these?

--------------------------------------------------------------------------------

👤 User: Does the first one have a kitchen?

🤖 Assistant:
Yes! The Downtown Loft with Parking includes a fully equipped kitchen with modern 
appliances. You'll have everything you need to prepare meals during your stay. The 
kitchen amenities make it great for longer stays or if you prefer cooking at home.

--------------------------------------------------------------------------------

👤 User: What about the price? Is it under $150?

🤖 Assistant:
Yes, it's well under your budget! The Downtown Loft is $125 per night, which gives 
you $25 of cushion under $150. It's a great value considering it includes free 
parking, a full kitchen, and the convenient downtown location. Would you like to 
proceed with this listing or explore other options?

================================================================================
📊 Conversation length: 3 exchanges
```

### 💡 Notice the Context Awareness

The AI remembers:
- "the first one" refers to the Downtown Loft mentioned earlier
- "it" and "the price" refer to the same property
- Previous recommendations inform follow-up answers

## 🛠️ Step 5: Enhance with Query Rephrasing

For better retrieval, we can rephrase follow-up questions to be standalone.

### Create a Rephrasing Chain

```python
# Prompt for rephrasing follow-up questions
rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", """Given a chat history and a follow-up question, rephrase the follow-up question 
to be a standalone question that includes relevant context from the chat history.

If the question is already standalone, return it as is.

Examples:
- Chat history: [User asks about Chicago apartments]
- Follow-up: "Does the first one have parking?"
- Standalone: "Does the Chicago apartment mentioned first have parking?"

- Chat history: [User asks about pet-friendly places]
- Follow-up: "What about the price?"
- Standalone: "What is the price of the pet-friendly listing?"
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# Create rephrasing chain
rephrase_chain = rephrase_prompt | llm | StrOutputParser()

print("✅ Rephrasing chain created")
```

### Update Conversation Manager with Rephrasing

```python
class EnhancedConversationManager(ConversationManager):
    """
    Enhanced conversation manager with query rephrasing for better retrieval.
    """
    
    def __init__(self, rag_chain, rephrase_chain):
        super().__init__(rag_chain)
        self.rephrase_chain = rephrase_chain
    
    def chat(self, session_id: str, question: str, verbose=False) -> str:
        """
        Process a chat message with query rephrasing and conversation history.
        
        Args:
            session_id: Unique identifier for the conversation session
            question: User's question or message
            verbose: If True, print the rephrased question
            
        Returns:
            AI assistant's response
        """
        # Get conversation history
        chat_history = self.get_history(session_id)
        
        # Rephrase the question if there's chat history
        if chat_history:
            rephrased_question = self.rephrase_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            if verbose:
                print(f"🔄 Rephrased: '{question}' → '{rephrased_question}'")
        else:
            rephrased_question = question
        
        # Use rephrased question for retrieval
        chain_with_history = (
            {
                "context": lambda x: retriever._get_relevant_documents(rephrased_question) | RunnableLambda(format_docs),
                "question": lambda x: x["question"],  # Use original question for response
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        chain_input = {
            "question": question,  # Show original question to user
            "chat_history": chat_history
        }
        
        response = chain_with_history.invoke(chain_input)
        
        # Save to history
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append((question, response))
        
        return response

# Initialize enhanced conversation manager
enhanced_manager = EnhancedConversationManager(rag_chain, rephrase_chain)

print("✅ Enhanced conversation manager initialized")
```

### Test Enhanced Conversation

```python
# Start a new session
session_id = "user_456"

print("\n" + "=" * 80)
print("💬 Enhanced Conversation Test (with rephrasing)")
print("=" * 80)

# First message
q1 = "Show me pet-friendly apartments in Denver"
r1 = enhanced_manager.chat(session_id, q1, verbose=True)
print(f"\n👤 User: {q1}")
print(f"\n🤖 Assistant:\n{r1}")

# Follow-up that needs rephrasing
print("\n" + "-" * 80)
q2 = "Any with a yard?"
r2 = enhanced_manager.chat(session_id, q2, verbose=True)
print(f"\n👤 User: {q2}")
print(f"\n🤖 Assistant:\n{r2}")

# Another follow-up
print("\n" + "-" * 80)
q3 = "What's the cheapest option?"
r3 = enhanced_manager.chat(session_id, q3, verbose=True)
print(f"\n👤 User: {q3}")
print(f"\n🤖 Assistant:\n{r3}")
```

**Expected Output:**
```
================================================================================
💬 Enhanced Conversation Test (with rephrasing)
================================================================================

👤 User: Show me pet-friendly apartments in Denver

🤖 Assistant:
I found some wonderful pet-friendly options in Denver:

1. **Mountain View Apartment with Pet Area** - $140/night
   Perfect for pet owners! This 2-bedroom apartment has a dedicated pet area and 
   is near several dog parks. Includes WiFi, kitchen, and allows dogs up to 50 lbs.

2. **Garden Level Condo with Patio** - $115/night
   Great for pets with outdoor access! The private patio opens to a fenced yard 
   area, and the location is close to hiking trails.

--------------------------------------------------------------------------------
🔄 Rephrased: 'Any with a yard?' → 'Are any of the pet-friendly apartments in Denver that I asked about equipped with a yard?'

👤 User: Any with a yard?

🤖 Assistant:
Yes! The Garden Level Condo (Listing 2) has a private patio that opens to a fenced 
yard area, which is perfect for your pets. It's at $115 per night, making it both 
pet and budget-friendly. The outdoor space gives your pet room to play safely!

--------------------------------------------------------------------------------
🔄 Rephrased: 'What's the cheapest option?' → 'What is the cheapest pet-friendly apartment in Denver with a yard from the options discussed?'

👤 User: What's the cheapest option?

🤖 Assistant:
The Garden Level Condo is the cheapest option at $115 per night. It's a great deal 
considering it includes the fenced yard area, pet-friendly amenities, and a full 
kitchen. Would you like more details about this property?
```

## 🛠️ Step 6: Structure Responses for the Frontend

For a chat UI, we want structured responses with metadata.

### Create a Structured Response Function

```python
import json
from datetime import datetime

def chat_with_structured_response(session_id: str, question: str, filters: dict = None):
    """
    Chat with structured response for frontend integration.
    
    Args:
        session_id: Unique session identifier
        question: User's message
        filters: Optional filters (bedrooms, price_max, etc.)
        
    Returns:
        dict: Structured response with message and metadata
    """
    # Get response
    response_text = enhanced_manager.chat(session_id, question)
    
    # Get the retrieved listings for metadata
    chat_history = enhanced_manager.get_history(session_id)
    
    # Rephrase if needed
    if chat_history:
        rephrased_q = rephrase_chain.invoke({
            "question": question,
            "chat_history": chat_history[:-2]  # Exclude the current exchange
        })
    else:
        rephrased_q = question
    
    # Retrieve documents
    docs = retriever._get_relevant_documents(rephrased_q)
    
    # Build listings metadata
    listings = []
    for doc in docs:
        listings.append({
            "id": doc.metadata.get("id"),
            "name": doc.metadata.get("name"),
            "price": doc.metadata.get("price"),
            "location": doc.metadata.get("location"),
            "similarity_score": doc.metadata.get("similarity_score")
        })
    
    # Structure the response
    structured_response = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "user_message": question,
        "assistant_message": response_text,
        "listings": listings,
        "message_count": enhanced_manager.get_session_count(session_id)
    }
    
    return structured_response

# Test structured response
test_session = "user_789"
structured_resp = chat_with_structured_response(
    session_id=test_session,
    question="Find me a luxury condo in Boston under $300"
)

print("\n📦 Structured Response:")
print(json.dumps(structured_resp, indent=2))
```

**Expected Output:**
```json
{
  "session_id": "user_789",
  "timestamp": "2026-01-15T14:30:45.123456",
  "user_message": "Find me a luxury condo in Boston under $300",
  "assistant_message": "I have some fantastic luxury condos in Boston for you:\n\n1. **Beacon Hill Luxury Condo** - $275/night\n   Stunning 2-bedroom condo in historic Beacon Hill with modern amenities, marble bathrooms, and city views. Premium finishes throughout!\n\n2. **Waterfront Penthouse** - $295/night\n   Incredible waterfront location with floor-to-ceiling windows, gourmet kitchen, and rooftop access. Just under your budget!\n\nBoth properties offer high-end experiences. Would you like more details about either one?",
  "listings": [
    {
      "id": "10054713",
      "name": "Beacon Hill Luxury Condo",
      "price": 275.0,
      "location": "Boston",
      "similarity_score": 0.8756
    },
    {
      "id": "10067342",
      "name": "Waterfront Penthouse",
      "price": 295.0,
      "location": "Boston",
      "similarity_score": 0.8623
    }
  ],
  "message_count": 1
}
```

## 🎓 What You've Learned

✅ **RAG Pattern**: Combining retrieval, augmentation, and generation  
✅ **Custom Retrievers**: Building LangChain retrievers for DocumentDB  
✅ **Prompt Engineering**: Designing effective system prompts for AI assistants  
✅ **Conversation Memory**: Maintaining context across multiple turns  
✅ **Query Rephrasing**: Improving retrieval for follow-up questions  
✅ **Structured Responses**: Formatting output for frontend integration  

## 🚀 Challenge: Enhance the RAG System

### Challenge 1: Add Sentiment Analysis (Medium)
Detect user sentiment and adjust the AI's tone accordingly.

**Requirements:**
- Analyze user messages for sentiment (positive, negative, neutral)
- Adjust response tone based on sentiment
- Be more empathetic for negative sentiment, enthusiastic for positive

<details>
<summary>💡 Hint</summary>

```python
def analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis using GPT."""
    prompt = f"""Analyze the sentiment of this message and respond with only one word: 
    'positive', 'negative', or 'neutral'.
    
    Message: {text}"""
    
    response = llm.invoke(prompt)
    return response.content.strip().lower()

# Update system prompt based on sentiment
def get_dynamic_system_prompt(sentiment: str) -> str:
    base_prompt = "You are a helpful Airbnb assistant."
    
    if sentiment == "negative":
        return base_prompt + " The user seems frustrated, so be extra patient and helpful."
    elif sentiment == "positive":
        return base_prompt + " The user is excited! Match their enthusiasm."
    else:
        return base_prompt
```
</details>

### Challenge 2: Implement Filter Extraction (Hard)
Automatically extract filters (price, bedrooms, location) from natural language queries.

**Requirements:**
- Parse user messages to identify filter criteria
- Extract: price range, number of bedrooms, location, amenities
- Apply these filters to the vector search

**Example:**
- Input: "3 bedroom house in Chicago under $200 with parking"
- Extracted: `{bedrooms: 3, location: "Chicago", price_max: 200, amenities: ["parking"]}`

<details>
<summary>💡 Hint</summary>

```python
filter_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """Extract search filters from the user's message. Return a JSON object with these fields:
    - bedrooms (number or null)
    - price_min (number or null)
    - price_max (number or null)
    - location (string or null)
    - amenities (array of strings or empty array)
    
    Only include fields that are explicitly mentioned. Return valid JSON only, no explanation."""),
    ("human", "{query}")
])

def extract_filters(query: str) -> dict:
    chain = filter_extraction_prompt | llm | StrOutputParser()
    result = chain.invoke({"query": query})
    return json.loads(result)

# Use in retriever
filters = extract_filters("3 bedroom house in Chicago under $200 with parking")
# Apply filters to MongoDB query
```
</details>

### Challenge 3: Add Source Citations (Medium)
Include clickable references to specific listings in the response.

**Requirements:**
- Format responses with numbered citations like [1], [2]
- Include a "Sources" section at the end with listing names and IDs
- Ensure citations match the listings actually used

<details>
<summary>💡 Hint</summary>

Update the system prompt:
```python
system_prompt_with_citations = """...previous prompt...

When recommending listings, add citations [1], [2], etc. 
At the end of your response, include a "Sources:" section that lists:
[1] Listing Name (ID: listing_id)
[2] Listing Name (ID: listing_id)
...
"""
```
</details>

### Challenge 4: Multi-turn Clarification (Advanced)
If the query is ambiguous, ask clarifying questions before searching.

**Requirements:**
- Detect vague queries ("find me something nice")
- Ask 2-3 specific clarifying questions
- Store preferences and use them for the actual search

**Example Flow:**
```
User: "I need a place in Chicago"
AI: "I'd love to help! A few questions:
     1. What's your budget per night?
     2. How many bedrooms do you need?
     3. Any must-have amenities?"
     
User: "Under $150, 2 bedrooms, and parking"
AI: [Performs search with extracted criteria]
```

<details>
<summary>💡 Hint</summary>

```python
def is_query_ambiguous(query: str) -> bool:
    """Check if query lacks essential details."""
    prompt = f"""Is this query too vague to search for accommodations? 
    Answer 'yes' or 'no'.
    
    Query: {query}
    
    A query is vague if it lacks: budget, bedroom count, or specific needs."""
    
    response = llm.invoke(prompt)
    return "yes" in response.content.lower()

def generate_clarifying_questions(query: str) -> str:
    """Generate clarifying questions."""
    prompt = f"""The user said: "{query}"
    
    Ask 2-3 specific clarifying questions to help find the perfect accommodation.
    Focus on: budget, number of bedrooms, must-have amenities, or travel purpose."""
    
    return llm.invoke(prompt).content
```
</details>

## 🎯 Bonus Challenge: Implement Conversation Branching

Allow users to "rewind" the conversation to a previous point and explore different options.

**Requirements:**
- Store conversation as a tree structure (not just a list)
- Support commands like "go back" or "try different options"
- Maintain multiple conversation branches per session

This is advanced and requires redesigning the conversation storage!

## 📖 Additional Resources

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)

## ✅ Checkpoint

Before moving to Module 3, ensure you have:

- [ ] Built a custom DocumentDB retriever for LangChain
- [ ] Created a RAG chain with proper prompts
- [ ] Implemented conversation memory
- [ ] Added query rephrasing for better retrieval
- [ ] Structured responses for frontend integration
- [ ] Tested multi-turn conversations
- [ ] Completed at least one challenge exercise

## 🎉 What's Next?

In **Module 3: Multi-Agent System with LangGraph**, you'll learn how to:
- Design a multi-agent architecture
- Create specialized agents (Search, Filter, Recommendation)
- Implement agent orchestration with LangGraph
- Handle complex workflows with state management
- Build a conversation router that delegates to the right agent
- Combine multiple AI capabilities into a cohesive system

---

**💬 Questions or Issues?**  
If you're stuck, check the troubleshooting section in Module 0, or ask your instructor for help!
