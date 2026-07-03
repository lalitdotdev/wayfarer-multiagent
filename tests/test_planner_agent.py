"""
Tests for the planner agent
"""
from unittest.mock import patch, MagicMock
import json
from langchain_core.messages import HumanMessage
from main import planner_agent

def test_planner_agent_success():
    """Test planner agent with valid JSON response"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "destination": "Paris",
            "departure_city": "New York",
            "dep_iata": "JFK",
            "arr_iata": "CDG",
            "flight_search_query": "flights JFK to CDG",
            "hotel_search_query": "hotels in Paris"
        })
        mock_llm.invoke.return_value = mock_response

        state = {
            "user_query": "Plan a trip from New York to Paris",
            "messages": [HumanMessage(content="Previous conversation")]
        }
        result = planner_agent(state)

        assert result["destination"] == "Paris"
        assert result["departure_city"] == "New York"
        assert result["dep_iata"] == "JFK"
        assert result["arr_iata"] == "CDG"
        assert result["flight_search_query"] == "flights JFK to CDG"
        assert result["hotel_search_query"] == "hotels in Paris"
        assert result["llm_calls"] == 1

def test_planner_agent_json_failure():
    """Test planner agent handles invalid JSON gracefully"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "Invalid JSON"
        mock_llm.invoke.return_value = mock_response

        state = {
            "user_query": "Plan a trip",
            "messages": [HumanMessage(content="Previous conversation")]
        }
        result = planner_agent(state)

        # Should fall back to existing state or defaults
        assert result["llm_calls"] == 1
        # The function should return defaults when JSON parsing fails
        assert result["destination"] == "unknown"  # default from state
        assert result["departure_city"] == "unknown"

def test_planner_agent_missing_fields():
    """Test planner agent handles missing fields in JSON"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        # Missing some fields
        mock_response.content = json.dumps({
            "destination": "Tokyo",
            "departure_city": "San Francisco"
            # Missing dep_iata, arr_iata, etc.
        })
        mock_llm.invoke.return_value = mock_response

        state = {
            "user_query": "Plan a trip to Tokyo",
            "messages": [HumanMessage(content="Previous conversation")]
        }
        result = planner_agent(state)

        assert result["destination"] == "Tokyo"
        assert result["departure_city"] == "San Francisco"
        # Missing fields should fall back to state or default
        assert result["dep_iata"] == "unknown"
        assert result["arr_iata"] == "unknown"
        assert result["llm_calls"] == 1