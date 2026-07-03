"""
Tests for Wayfarer travel concierge tools
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Import the tools to test
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


def test_tavily_search_import():
    """Test that tavily_search can be imported"""
    assert tavily_search is not None


def test_flight_tool_import():
    """Test that search_flights can be imported"""
    assert search_flights is not None


@patch('tools.tavily_tool.get_client')
def test_tavily_search_success(mock_get_client):
    """Test tavily_search returns expected format on success"""
    # Mock the Tavily client and response
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.search.return_value = {
        "results": [
            {
                "title": "Test Hotel",
                "url": "https://example.com/hotel",
                "content": "This is a test hotel with great amenities and service."
            }
        ]
    }

    result = tavily_search("test hotel")
    assert isinstance(result, str)
    assert "Test Hotel" in result
    assert "https://example.com/hotel" in result


@patch('tools.flight_tool.requests.get')
def test_search_flights_aviationstack_success(mock_get):
    """Test search_flights with successful AviationStack API response"""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "airline": {"name": "Test Airline"},
                "departure": {"airport": "JFK"},
                "arrival": {"airport": "LAX"},
                "flight_status": "scheduled",
                "flight_date": "2024-01-01"
            }
        ]
    }
    mock_get.return_value = mock_response

    # Set environment variable for API key
    with patch.dict(os.environ, {"AVIATIONSTACK_API_KEY": "test-key"}):
        result = search_flights("test flight", dep_iata="JFK", arr_iata="LAX")
        assert isinstance(result, str)
        assert "Test Airline" in result
        assert "JFK" in result
        assert "LAX" in result


@patch('tools.flight_tool.requests.get')
def test_search_flights_aviationstack_failure(mock_get):
    """Test search_flights falls back to Tavily when AviationStack fails"""
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    # Mock Tavily search fallback
    with patch('tools.flight_tool.tavily_search') as mock_tavily:
        mock_tavily.return_value = "Fallback flight results from Tavily"

        with patch.dict(os.environ, {"AVIATIONSTACK_API_KEY": "test-key"}):
            result = search_flights("test flight", dep_iata="JFK", arr_iata="LAX")
            assert result == "Fallback flight results from Tavily"
            mock_tavily.assert_called_once()


@patch('tools.flight_tool.tavily_search')
def test_search_flights_no_api_key(mock_tavily_search):
    """Test search_flights uses Tavily when no API key is available"""
    mock_tavily_search.return_value = "Tavily fallback results"

    # Ensure no API key is set
    with patch.dict(os.environ, {}, clear=True):
        result = search_flights("test flight")
        assert result == "Tavily fallback results"
        mock_tavily_search.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])