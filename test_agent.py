
from unittest.mock import patch

from agent import AgentDesk


def make_agent():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        return AgentDesk()


def test_empty_question():
    agent = make_agent()
    result = agent.answer_question("   ")
    assert "enter a support question" in result.answer.lower()


def test_unmatched_question():
    agent = make_agent()
    with patch.object(agent.knowledge_base, "search", return_value=[]):
        result = agent.answer_question("What is the best pizza?")
    assert "couldn't find relevant information" in result.answer.lower()


def test_service_status_tool():
    agent = make_agent()
    result = agent.get_service_status("authentication")
    assert "operational" in result.answer
    assert "check_service_status" in result.tools_used


def test_ticket_tool():
    agent = make_agent()
    result = agent.submit_ticket({
        "title": "Cannot access the API",
        "description": "The API returns HTTP 403 for valid credentials.",
        "category": "API Access",
        "priority": "High",
        "requester": "Demo User",
    })
    assert result.ticket_id is not None
    assert result.ticket_id.startswith("INC-")
