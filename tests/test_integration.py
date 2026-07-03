"""
Integration tests for the travel agent workflow
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage
from main import app

def test_travel_workflow_happy_path():
    """Test a complete travel workflow with all steps"""
    # Mock the external services
    with patch('main.search_flights') as mock_flights, \
         patch('main.tavily_search') as mock_hotels, \
         patch('main.llm') as mock_llm:

        # Setup mocks
        mock_flights.return_value = "Air France Flight 123: Paris to New York"
        mock_hotels.return_value = "Hilton Paris: 5-star hotel near Eiffel Tower"

        # Mock LLM responses for each agent that uses it
        # We need to mock multiple calls: router, planner, itinerary, final, etc.
        # We'll use side_effect to return different values for each call
        mock_llm_response_sequence = [
            # Router agent: should say TRAVEL
            MagicMock(content="TRAVEL"),
            # Planner agent: returns JSON with trip details
            MagicMock(content='{"destination": "Paris", "departure_city": "New York", "dep_iata": "JFK", "arr_iata": "CDG", "flight_search_query": "flights JFK to CDG", "hotel_search_query": "hotels in Paris"}'),
            # Itinerary agent: creates itinerary
            MagicMock(content="Day 1: Arrive in Paris. Stay at Hilton.\\nDay 2: Visit Louvre."),
            # Final agent: formats the final response
            MagicMock(content="Your trip to Paris is planned!\\nDay 1: Arrive in Paris. Stay at Hilton.\\nDay 2: Visit Louvre.")
        ]
        mock_llm.side_effect = mock_llm_response_sequence

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
        config = {"configurable": {"thread_id": "test_session"}}

        # Run the graph
        result = app.invoke(inputs, config=config)

        # Check that we got a response
        assert "messages" in result
        assert len(result["messages"]) > 0
        # The last message should be from the agent (AIMessage)
        last_message = result["messages"][-1]
        assert last_message.type == "ai"
        assert "Paris" in last_message.content
        assert "Hilton" in last_message.content

        # Verify that our mocks were called
        assert mock_flights.called
        assert mock_hotels.called
        assert mock_llm.call_count == 4  # router, planner, itinerary, final