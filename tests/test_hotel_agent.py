"""
Tests for the hotel agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from main import hotel_agent

def test_hotel_agent_unknown_destination():
    """Test hotel agent when destination is unknown"""
    state = {
        "destination": "unknown",
        "user_query": "Test query"
    }
    result = hotel_agent(state)

    assert "Destination unknown" in result["hotel_results"]
    assert result["messages"][0].content == "[Hotel Agent] No destination found to search hotels."

@patch('main.tavily_search')
def test_hotel_agent_with_known_destination(mock_tavily_search):
    """Test hotel agent with known destination"""
    mock_tavily_search.return_value = "Hotel 1: Hotel A\nHotel 2: Hotel B"

    state = {
        "destination": "London",
        "user_query": "Hotels in London",
        "hotel_search_query": "luxury hotels London"
    }
    result = hotel_agent(state)

    assert result["hotel_results"] == "Hotel 1: Hotel A\nHotel 2: Hotel B"
    assert result["messages"][0].content == "[Hotel Agent] Searched and fetched hotel options."
    mock_tavily_search.assert_called_once_with("luxury hotels London")

@patch('main.tavily_search')
def test_hotel_agent_uses_default_query_when_none_provided(mock_tavily_search):
    """Test hotel agent uses default query when hotel_search_query is empty"""
    mock_tavily_search.return_value = "Hotel results"

    state = {
        "destination": "Paris",
        "user_query": "I need a hotel in Paris",
        "hotel_search_query": ""  # Empty, should use default
    }
    result = hotel_agent(state)

    agent(state)

    # Should call tavily_search with default query: "best hotels in Paris"
    mock_tavily_search.assert_called_once_with("best hotels in Paris")