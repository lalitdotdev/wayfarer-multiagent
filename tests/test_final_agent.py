"""
Tests for the final agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from main import final_agent

def test_final_agent_non_travel():
    """Test final agent when query is not travel-related"""
    state = {
        "is_travel_related": False,
        "itinerary": "Some itinerary"
    }
    result = final_agent(state)
    assert result == {}

@patch('main.llm')
def test_final_agent_with_itinerary(mock_llm):
    """Test final agent with itinerary"""
    mock_response = MagicMock()
    mock_response.content = "Final response with itinerary"
    mock_llm.invoke.return_value = mock_response

    state = {
        "is_travel_related": True,
        "itinerary": "Day 1: Arrive in Paris\nDay 2: Visit Eiffel Tower"
    }
    result = final_agent(state)

    assert result["messages"][0].content == "Final response with itinerary"
    assert result["llm_calls"] == 1
    # Check that the prompt contains the itinerary
    call_args = mock_llm.invoke.call_args[0][0]
    assert isinstance(call_args[0], HumanMessage)
    prompt = call_args[0].content
    assert "Day 1: Arrive in Paris" in prompt
    assert "Day 2: Visit Eiffel Tower" in prompt