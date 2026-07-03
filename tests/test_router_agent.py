"""
Tests for the router agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage
from main import router_agent

def test_router_agent_travel():
    """Test router agent with travel query"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "TRAVEL"
        mock_llm.invoke.return_value = mock_response
        state = {"user_query": "I want to go to Paris", "messages": []}
        result = router_agent(state)
        assert result["is_travel_related"] == True
        assert result["llm_calls"] == 1

def test_router_agent_non_travel():
    """Test router agent with non-travel query"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "OTHER"
        mock_llm.invoke.return_value = mock_response
        state = {"user_query": "What is 2+2?", "messages": []}
        result = router_agent(state)
        assert result["is_travel_related"] == False
        assert result["llm_calls"] == 1

def test_router_agent_case_insensitive():
    """Test router agent is case insensitive"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "travel"
        mock_llm.invoke.return_value = mock_response
        state = {"user_query": "Travel to London", "messages": []}
        result = router_agent(state)
        assert result["is_travel_related"] == True
        assert result["llm_calls"] == 1