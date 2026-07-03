"""
Tests for the final agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from main import final_agent

def test_final_agent_with_itinerary():
    """Test final agent with a travel-related state"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "Here is your travel plan: Visit Paris and enjoy the food!"
        mock_llm.invoke.return_value = mock_response

        state = {
            "itinerary": "Day 1: Arrive in Paris. Day 2: Eat croissants.",
            "is_travel_related": True
        }
        result = final_agent(state)

        assert isinstance(result["messages"][0], AIMessage)
        assert "travel plan" in result["messages"][0].content
        assert "Paris" in result["messages"][0].content
        assert result["llm_calls"] == 1

def test_final_agent_non_travel():
    """Test final agent with non-travel related state"""
    state = {
        "is_travel_related": False
    }
    result = final_agent(state)

    # Should return empty dict
    assert result == {}