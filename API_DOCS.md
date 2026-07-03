# API Documentation for Wayfarer

## Overview
Wayfairer provides a modular API through its LangGraph-based workflow. While primarily designed as a Streamlit application, the core functionality can be accessed programmatically.

## Core Modules

### main.py - Workflow Engine
The main workflow orchestrator that manages the multi-agent travel planning process.

#### Functions:
- `router_agent(state)`: Classifies user intent as travel-related or chitchat
- `planner_agent(state)`: Extracts travel details from user input
- `flight_agent(state)`: Searches for flight options
- `hotel_agent(state)`: Searches for hotel options
- `itinerary_agent(state)`: Creates detailed travel itinerary
- `final_agent(state)`: Formats final response for user
- `chitchat_agent(state)`: Handles non-travel conversations

#### State Structure (TravelState):
```python
{
    "messages": List[AnyMessage],  # Conversation history
    "user_query": str,             # Original user input
    "destination": str,            # Target destination
    "departure_city": str,         # Starting location
    "dep_iata": str,               # Departure airport code
    "arr_iata": str,               # Arrival airport code
    "flight_search_query": str,    # Flight search parameters
    "hotel_search_query": str,     # Hotel search parameters
    "flight_results": str,         # Raw flight data
    "hotel_results": str,          # Raw hotel data
    "itinerary": str,              # Generated itinerary
    "llm_calls": int,              # Counter for LLM usage
    "is_travel_related": bool      # Intent classification result
}
```

### app.py - Streamlit Interface
Handles the user interface and real-time visualization of the agent workflow.

#### Key Components:
- Hero section with animated gradient background
- Destination strip with popular locations
- Input area with quick suggestion chips
- Real-time agent tracking visualization
- Metrics display (agents run, LLM calls, status)
- Boarding pass style results presentation
- Download functionality (Markdown/PDF)

### tools/ - External Service Integrations

#### flight_tool.py
Interfaces with AviationStack API for flight data:
- `search_flights(query, dep_iata, arr_iata)`: Main flight search function
- Handles API rate limiting and error cases
- Returns formatted flight information

#### tavily_tool.py
Interfaces with Tavily Search API for hotel/local information:
- `tavily_search(query)`: Main search function
- Returns structured search results with relevance scoring

## Data Flow
1. User submits query via Streamlit interface
2. Request sent to LangGraph workflow
3. Router agent determines if travel-related
4. Planner extracts travel details (destination, dates, etc.)
5. Flight and Hotel agents run in parallel:
   - Flight agent queries AviationStack
   - Hotel agent queries Tavily Search
6. Itinerary agent synthesizes results into narrative
7. Final agent formats response for presentation
8. Streamlit UI updates in real-time as each step completes
9. User can download results as Markdown or PDF

## Extending the System

### Adding New Agents
1. Create new agent function following the pattern:
   ```python
   def new_agent(state: TravelState) -> Dict:
       # Process state
       return {
           "updated_field": new_value,
           "messages": [AIMessage(content="...")],
           "llm_calls": 1  # if LLM used
       }
   ```
2. Add node to graph in main.py
3. Connect appropriate edges
4. Update UI to display new agent status

### Modifying Existing Agents
- Each agent receives the full TravelState
- Agents should only modify fields they own
- Use LLMs via the global `llm` instance (ChatGroq)
- Return minimal updates to avoid overwriting other agents' work
- Increment `llm_calls` by 1 for each LLM invocation

## Configuration
### Language Model Settings
In main.py:
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,  # Adjust for creativity vs consistency
    max_tokens=4096
)
```

### Workflow Configuration
The StateGraph in main.py defines:
- Node registration (`graph.add_node()`)
- Edge connections (`graph.add_edge()`, `graph.add_conditional_edges()`)
- Checkpointer setup for persistence (`PostgresSaver`)
- Graph compilation (`graph.compile()`)

## Error Handling
- Agents should catch exceptions and return graceful error messages
- External API calls include retry logic and fallback responses
- UI displays error states without crashing the application
- Logging can be extended for production monitoring

## Testing
Unit tests should:
1. Mock external API calls (AviationStack, Tavily)
2. Test agent functions with various input states
3. Verify state transitions in the workflow
4. Validate edge cases and error conditions
5. Test UI components with Streamlit testing utilities

## Performance Considerations
- Parallel execution of flight and hotel agents
- Streaming responses reduce perceived latency
- Database connection pooling via PostgresSaver
- Efficient state passing between agents
- Minimal DOM updates in Streamlit for smooth UX