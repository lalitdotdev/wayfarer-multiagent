"""
Tests for Wayfarer main application components
"""

import json
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

# Import the main application components
from main import (
    TravelState,
    router_agent,
    planner_agent,
    flight_agent,
    hotel_agent,
    itinerary_agent,
    final_agent
)


def test_travel_state_creation():
    """Test that TravelState can be created with expected fields"""
    state: TravelState = {
        "messages": [HumanMessage(content="Test message")],
        "user_query": "Test query",
        "destination": "Paris",
        "departure_city": "New York",
        "dep_iata": "JFK",
        "arr_iata": "CDG",
        "flight_search_query": "flights to Paris",
        "hotel_search_query": "hotels in Paris",
        "flight_results": "Flight data",
        "hotel_results": "Hotel data",
        "itinerary": "Travel itinerary",
        "llm_calls": 0,
        "is_travel_related": True
    }

    assert state["user_query"] == "Test query"
    assert state["destination"] == "Paris"
    assert state["is_travel_related"] is True


@patch('main.llm')
def test_router_agent_travel_query(mock_llm):
    """Test router_agent correctly identifies travel-related queries"""
    # Mock LLM response for travel query
    mock_response = MagicMock()
    mock_response.content = "TRAVEL"
    mock_llm.invoke.return_value = mock_response

    state = {
        "user_query": "I want to plan a trip to Paris",
        "messages": []
    }

    result = router_agent(state)
    assert result["is_travel_related"] is True
    assert result["llm_calls"] == 1
    mock_llm.invoke.assert_called_once()


@patch('main.llm')
def test_router_agent_non_travel_query(mock_llm):
    """Test router_agent correctly identifies non-travel queries"""
    # Mock LLM response for non-travel query
    mock_response = MagicMock()
    mock_response.content = "OTHER"
    mock_llm.invoke.return_value = mock_response

    state = {
        "user_query": "What is 2+2?",
        "messages": []
    }

    result = router_agent(state)
    assert result["is_travel_related"] is False
    assert result["llm_calls"] == 1
    mock_llm.invoke.assert_called_once()


@patch('main.llm')
def test_planner_agent_success(mock_llm):
    """Test planner_agent extracts travel details correctly"""
    # Mock LLM response with JSON
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "destination": " Tokyo",
        "departure_city": " San Francisco",
        "dep_iata": " SFO",
        "arr_iata": " NRT",
        "flight_search_query": "flights SFO to NRT",
        "hotel_search_query": "hotels in Tokyo"
    })
    mock_llm.invoke.return_value = mock_response

    state = {
        "user_query": "Plan a trip from San Francisco to Tokyo",
        "messages": [HumanMessage(content="Previous conversation")]
    }

    result = planner_agent(state)
    assert result["destination"] == "Tokyo"  # Should be stripped
    assert result["departure_city"] == "San Francisco"  # Should be stripped
    assert result["dep_iata"] == "SFO"  # Should be stripped
    assert result["arr_iata"] == "NRT"  # Should be stripped
    assert result["llm_calls"] == 1
    mock_llm.invoke.assert_called_once()


@patch('main.llm')
def test_planner_agent_json_parse_failure(mock_llm):
    """Test planner_agent handles JSON parse failure gracefully"""
    mock_response = MagicMock()
    mock_response.content = "Invalid JSON"
    mock_llm.invoke.return_value = mock_response

    state = {
        "user_query": "Plan a trip",
        "messages": [HumanMessage(content="Previous conversation")]
    }

    result = planner_agent(state)
    # Should fall back to existing state values or defaults
    assert result["llm_calls"] == 1
    mock_llm.invoke.assert_called_once()


def test_flight_agent_unknown_destination():
    """Test flight_agent handles unknown destination"""
    state = {
        "destination": "unknown",
        "user_query": "Test query"
    }

    result = flight_agent(state)
    assert "Destination unknown" in result["flight_results"]
    assert result["messages"][0].content == "[Flight Agent] No destination found to search flights."


def test_hotel_agent_unknown_destination():
    """Test hotel_agent handles unknown destination"""
    state = {
        "destination": "unknown",
        "user_query": "Test query"
    }

    result = hotel_agent(state)
    assert "Destination unknown" in result["hotel_results"]
    assert result["messages"][0].content == "[Hotel Agent] No destination found to search hotels."


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])