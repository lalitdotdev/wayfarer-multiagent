"""
Tests for the flight agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from main import flight_agent

def test_flight_agent_unknown_destination():
    """Test flight agent when destination is unknown"""
    state = {
        "destination": "unknown",
        "user_query": "Test query"
    }
    result = flight_agent(state)

    assert "Destination unknown" in result["flight_results"]
    assert result["messages"][0].content == "[Flight Agent] No destination found to search flights."

@patch('main.search_flights')
def test_flight_agent_with_known_destination(mock_search_flights):
    """Test flight agent with known destination"""
    mock_search_flights.return_value = "Flight 1: Airline A\nFlight 2: Airline B"

    state = {
        "destination": "Paris",
        "user_query": "Flight to Paris",
        "dep_iata": "JFK",
        "arr_iata": "CDG",
        "flight_search_query": "flights to Paris"
    }
    result = flight_agent(state)

    assert result["flight_results"] == "Flight 1: Airline A\nFlight 2: Airline B"
    assert result["messages"][0].content == "[Flight Agent] Searched and fetched flight options."
    mock_search_flights.assert_called_once_with(
        query="flights to Paris",
        dep_iata="JFK",
        arr_iata="CDG"
    )

@patch('main.search_flights')
def test_flight_agent_uses_user_query_when_no_search_query(mock_search_flights):
    """Test flight agent uses user query when flight_search_query is empty"""
    mock_search_flights.return_value = "Flight results"

    state = {
        "destination": "London",
        "user_query": "I want to fly to London",
        "dep_iata": "LAX",
        "arr_iata": "LHR",
        "flight_search_query": ""  # Empty, should fall back to user_query
    }
    result = flight_agent(state)

    mock_search_flights.assert_called_once_with(
        query="I want to fly to London",
        dep_iata="LAX",
        arr_iata="LHR"
    )