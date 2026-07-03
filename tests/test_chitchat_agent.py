"""
Tests for the chitchat agent
"""
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from main import chitchat_agent

def test_chitchat_agent_greeting():
    """Test chitchat agent with a greeting"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help you with your travel plans?"
        mock_llm.invoke.return_value = mock_response

        state = {
            "user_query": "Hi there!",
            "messages": []
        }
        result = chitchat_agent(state)

        assert isinstance(result["messages"][0], AIMessage)
        assert "help you with your travel plans" in result["messages"][0].content
        assert result["llm_calls"] == 1

def test_chitchat_agent_weather():
    """Test chitchat agent with a weather question (non-travel)"""
    with patch('main.llm') as mock_llm:
        mock_response = MagicMock()
        mock_response.content = "I'm not sure about the weather, but I can help you plan a trip!"
        mock_llm.invoke.return_value = mock_response

        state = {
            "user_query": "What's the weather like today?",
            "messages": [HumanMessage(content="Previous chat")]
        }
        result = chitchat_agent(state)

        assert isinstance(result["messages"][0], AIMessage)
        assert "plan a trip" in result["messages"][0].content
        assert result["llm_calls"] == 1