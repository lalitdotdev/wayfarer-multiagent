"""
Integration tests for the travel agent workflow
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from main import app

def test_full_travel_flow():
    """Test the full travel flow with mocked dependencies"""
    # Mock the external tools
    with patch('main.search_flights') as mock_flights, \
         patch('main.tavily_search') as mock_hotels, \
         patch('main.llm') as mock_llm:

        # Mock flight search to return some flight data
        mock_flights.return_value = "Flight 1: Airline A from JFK to CDG\nFlight 2: Airline B from JFK to CDG"

        # Mock hotel search to return some hotel data
        mock_hotels.return_value = "Hotel 1: Hotel Paris\nHotel 2: Hotel Lyon"

        # Mock the LLM responses for each agent
        # We need to mock responses for router, planner, itinerary, final agents
        # Let's create a sequence of responses
        mock_responses = [
            # Router agent: should return TRAVEL
            MagicMock(content="TRAVEL"),
            # Planner agent: should return JSON with travel details
            MagicMock(content='{"destination": "Paris", "departure_city": "New York", "dep_iata": "JFK", "arr_iata": "CDG", "flight_search_query": "flights to Paris", "hotel_search_query": "hotels in Paris"}'),
            # Itinerary agent: should return an itinerary
            MagicMock(content="Day 1: Arrive in Paris. Check into hotel.\nDay 2: Visit the Louvre."),
            # Final agent: should return a formatted response
            MagicMock(content="Your trip to Paris: Day 1: Arrive in Paris. Check into hotel. Day 2: Visit the Louvre.")
        ]
        mock_llm.invoke.side_effect = mock_responses

        # Initial state
        inputs = {
            "messages": [HumanMessage(content="I want to go to Paris from New York")],
            "user_query": "I want to go to Paris from New York",
            "destination": "unknown",
            "departure_city": "unknown",
            "dep_iata": "unknown",
            "arr_iata": "unknown",
            "flight_search_query": "",
            "hotel_search_query": "",
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
            "is_travel_related": True
        }

        # Configuration for the graph (using a fixed thread_id for testing)
        config = {
            "configurable": {
                "thread_id": "test_thread"
            }
        }

        # Run the graph
        result = app.invoke(inputs, config=config)

        # Check that we got a response
        assert "messages" in result
        assert len(result["messages"]) > 0
        # The last message should be from the agent (AIMessage)
        last_message = result["messages"][-1]
        assert isinstance(last_message, AIMessage)
        assert "Paris" in last_message.content
        assert "Louvre" in last_message.content

        # Verify that our mocks were called
        assert mock_flights.called
        assert mock_hotels.called
        assert mock_llm.invoke.call_count == 4  # router, planner, itinerary, final