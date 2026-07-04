"""
Tests for Wayfarer travel concierge tools and utilities
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Import the tools to test
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from utils import extract_iata_codes, format_currency, validate_date_range, extract_travel_duration


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


@patch('tools.tavily_tool.get_client')
def test_tavily_search_no_api_key(mock_get_client):
    """Test tavily_search handles missing API key"""
    mock_get_client.side_effect = ValueError("TAVILY_API_KEY is not set in environment variables.")

    result = tavily_search("test query")
    assert "Search service is not properly configured" in result


@patch('tools.tavily_tool.get_client')
def test_tavily_search_rate_limit_error(mock_get_client):
    """Test tavily_search handles rate limit error"""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    # Simulate a rate limit error (e.g., HTTP 429)
    mock_client.search.side_effect = Exception("429 Client Error: Too Many Requests for url: https://api.tivly.com/v2/search")

    result = tavily_search("test query")
    assert "Search service is currently experiencing high demand" in result


@patch('tools.tavily_tool.get_client')
def test_tavily_search_generic_error(mock_get_client):
    """Test tavily_search handles generic error"""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.search.side_effect = Exception("Internal Server Error")

    result = tavily_search("test query")
    assert "Search service is temporarily unavailable" in result


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


@patch('tools.flight_tool.requests.get')
def test_search_flights_aviationstack_timeout(mock_get):
    """Test search_flights falls back to Tavily when AviationStack times out"""
    # Mock timeout
    mock_get.side_effect = Exception("Timeout")

    # Mock Tavily search fallback
    with patch('tools.flight_tool.tavily_search') as mock_tavily:
        mock_tavily.return_value = "Fallback flight results from Tavily"

        with patch.dict(os.environ, {"AVIATIONSTACK_API_KEY": "test-key"}):
            result = search_flights("test flight", dep_iata="JFK", arr_iata="LAX")
            assert result == "Fallback flight results from Tavily"
            mock_tavily.assert_called_once()


@patch('tools.flight_tool.requests.get')
def test_search_flights_aviationstack_invalid_json(mock_get):
    """Test search_flights falls back to Tavily when AviationStack returns invalid JSON"""
    # Mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    # Mock Tavily search fallback
    with patch('tools.flight_tool.tavily_search') as mock_tavily:
        mock_tavily.return_value = "Fallback flight results from Tavily"

        with patch.dict(os.environ, {"AVIATIONSTACK_API_KEY": "test-key"}):
            result = search_flights("test flight", dep_iata="JFK", arr_iata="LAX")
            assert result == "Fallback flight results from Tavily"
            mock_tavily.assert_called_once()


@patch('tools.flight_tool.requests.get')
def test_search_flights_both_apis_fail(mock_get):
    """Test search_returns error message when both APIs fail"""
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    # Mock Tavily search to also fail
    with patch('tools.flight_tool.tavily_search') as mock_tavily:
        mock_tavily.return_value = "Error from Tavily"

        with patch.dict(os.environ, {"AVIATIONSTACK_API_KEY": "test-key"}):
            result = search_flights("test flight", dep_iata="JFK", arr_iata="LAX")
            assert result == "Error from Tavily"


@patch('tools.flight_tool.tavily_search')
def test_search_flights_no_api_key(mock_tavily_search):
    """Test search_flights uses Tavily when no API key is available"""
    mock_tavily_search.return_value = "Tavily fallback results"

    # Ensure no API key is set
    with patch.dict(os.environ, {}, clear=True):
        result = search_flights("test flight")
        assert result == "Tavily fallback results"
        mock_tavily_search.assert_called_once()


# Utility function tests
def test_extract_iata_codes():
    """Test IATA code extraction from text"""
    # Test with two codes
    result = extract_iata_codes("Fly from JFK to LAX")
    assert result.get('departure') == 'JFK'
    assert result.get('arrival') == 'LAX'

    # Test with one code (arrival)
    result = extract_iata_codes("Going to NRT")
    assert result.get('arrival') == 'NRT'
    assert 'departure' not in result

    # Test with one code (departure)
    result = extract_iata_codes("Departing from SFO")
    assert result.get('departure') == 'SFO'
    assert 'arrival' not in result

    # Test with no codes
    result = extract_iata_codes("Going to Paris")
    assert result == {}

    # Test case insensitivity
    result = extract_iata_codes("fly from jfk to lax")
    assert result.get('departure') == 'JFK'
    assert result.get('arrival') == 'LAX'


def test_format_currency():
    """Test currency formatting"""
    # Test default currency (INR)
    assert format_currency(1234.5) == "₹1,234.50"
    assert format_currency(0) == "₹0.00"
    assert format_currency(1000000) == "₹1,000,000.00"

    # Test custom currency
    assert format_currency(100, "$") == "$100.00"
    assert format_currency(50.5, "€") == "€50.50"
    assert format_currency(99.99, "£") == "£99.99"


def test_validate_date_range():
    """Test date range validation"""
    # Valid dates
    assert validate_date_range("2023-01-01", "2023-12-31") == True
    assert validate_date_range("2023-06-15", "2023-06-15") == True  # Same day

    # Invalid dates
    assert validate_date_range("2023-12-31", "2023-01-01") == False  # End before start
    assert validate_date_range("not-a-date", "2023-01-01") == False
    assert validate_date_range("2023-01-01", "not-a-date") == False
    assert validate_date_range("2023-13-01", "2023-01-01") == False  # Invalid month
    assert validate_date_range("2023-01-32", "2023-01-01") == False  # Invalid day


def test_extract_travel_duration():
    """Test travel duration extraction"""
    # Test various formats
    assert extract_travel_duration("7-day trip to Paris") == 7
    assert extract_travel_duration("10 day vacation") == 10
    assert extract_travel_duration("Stay for 5 days") == 5
    assert extract_travel_duration("3 days trip") == 3
    assert extract_travel_duration("2-week tour") == 14  # 2 weeks = 14 days
    assert extract_travel_duration("weekend getaway") == 7  # Default 1 week
    assert extract_travel_duration("Just visiting") is None  # No duration


if __name__ == "__main__":
    pytest.main([__file__])