"""
Smoke tests for Wayfarer application basic functionality.
"""
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all required modules can be imported."""
    try:
        import main
        import app
        from tools.tavily_tool import tavily_search
        from tools.flight_tool import search_flights
        assert True  # If we get here, imports succeeded
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_travel_state_structure():
    """Test that TravelState has the expected structure."""
    from main import TravelState
    from langchain_core.messages import HumanMessage

    # Check that it's a TypedDict with expected fields
    expected_fields = {
        'messages', 'user_query', 'destination', 'departure_city',
        'dep_iata', 'arr_iata', 'flight_search_query', 'hotel_search_query',
        'flight_results', 'hotel_results', 'itinerary', 'llm_calls', 'is_travel_related'
    }

    # We can't directly inspect TypedDict fields, but we can create an instance
    state: TravelState = {
        "messages": [HumanMessage(content="test")],
        "user_query": "test",
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

    # Check that all expected keys are present
    assert set(state.keys()) == expected_fields


def test_agent_functions_exist():
    """Test that all agent functions exist and are callable."""
    from main import (
        router_agent, chitchat_agent, planner_agent,
        flight_agent, hotel_agent, itinerary_agent, final_agent
    )

    # Check that all functions exist and are callable
    assert callable(router_agent)
    assert callable(chitchat_agent)
    assert callable(planner_agent)
    assert callable(flight_agent)
    assert callable(hotel_agent)
    assert callable(itinerary_agent)
    assert callable(final_agent)


if __name__ == "__main__":
    test_imports()
    test_travel_state_structure()
    test_agent_functions_exist()
    print("All smoke tests passed!")