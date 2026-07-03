"""
Tests for the itinerary agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from main import itinerary_agent

def test_itinerary_agent_unknown_destination():
    """Test itinerary agent when destination is unknown"""
    state = {
        "destination": "unknown",
        "user_query": "Test query"
    }
    result = itinerary_agent(state)

    assert result["itinerary"] == "No travel destination specified."
    assert result["messages"][0].content == "[Itinerary Agent] Skipped itinerary generation."

@patch('main.llm')
def test_itinerary_agent_with_data(mock_llm):
    """Test itinerary agent with flight and hotel data"""
    mock_response = MagicMock()
    mock_response.content = "Generated itinerary for Paris"
    mock_llm.invoke.return_value = mock_response

    state = {
        "destination": "Paris",
        "user_query": "Plan a trip to Paris",
        "departure_city": "New York",
        "flight_results": "Flight 1: Airline A\nFlight 2: Airline B",
        "hotel_results": "Hotel 1: Hotel X\nHotel 2: Hotel Y"
    }
    result = itinerary_agent(state)

    assert result["itinerary"] == "Generated itinerary for Paris"
    assert result["messages"][0].content == "Generated itinerary for Paris"
    assert result["llm_calls"] == 1
    # Check that the LLM was called with a prompt containing the data
    call_args = mock_llm.invoke.call_args[0][0]
    assert isinstance(call_args[0], HumanMessage)
    prompt = call_args[0].content
    assert "Plan a trip to Paris" in prompt
    assert "Paris" in prompt
    assert "New York" in prompt
    assert "Flight 1: Airline A" in prompt
    assert "Hotel 1: Hotel X" in prompt

@patch('main.llm')
def test_itinerary_agent_uses_user_query_for_prompt(mock_llm):
    """Test itinerary agent uses user query in prompt"""
    mock_response = MagicMock()
    mock_response.content = "Itinerary content"
    mock_llm.invoke.return_value = mock_response

    state = {
        "destination": "Tokyo",
        "user_query": "I want to visit Tokyo for cherry blossoms",
        "departure_city": "London",
        "flight_results": "Flight data",
        "hotel_results": "Hotel data"
    }
    result = itinerary_agent(state)

    assert result["itinerary"] == "Itinerary content"
    # Verify the prompt contains the user query
    call_args = mock_llm.invoke.call_args[0][0]
    prompt = call_args[0].content
    assert "I want to visit Tokyo for cherry blossoms" in prompt