# API Documentation for Wayfarer

## Overview

Wayfairer provides a modular API through its LangGraph-based workflow. While primarily designed as a Streamlit application, the core functionality can be accessed programmatically through the main workflow engine.

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

```typescript
{
  "messages": List[AnyMessage],  // Conversation history
  "user_query": str,             // Original user input
  "destination": str,            // Target destination
  "departure_city": str,         // Starting location
  "dep_iata": str,               // Departure airport code
  "arr_iata": str,               // Arrival airport code
  "flight_search_query": str,    // Flight search parameters
  "hotel_search_query": str,     // Hotel search parameters
  "flight_results": str,         // Raw flight data
  "hotel_results": str,          // Raw hotel data
  "itinerary": str,              // Generated itinerary
  "llm_calls": int,              // Counter for LLM usage
  "is_travel_related": bool      // Intent classification result
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

### Tools

#### flight_tool.py - Flight Search Functionality

Provides flight search capabilities with fallback mechanisms.

##### Functions:

- `search_flights(query: str, dep_iata: str = None, arr_iata: str = None) -> str`
  - Searches for flights using AviationStack API
  - Falls back to Tavily search when API unavailable
  - Returns formatted flight information string

#### tavily_tool.py - Tavily Search Wrapper

Provides web search capabilities for hotel and travel information.

##### Functions:

- `tavily_search(query: str) -> str`
 

<tool_call>
<function=Bash>
<parameter=command>
git add API_DOCS.md