
from tools import check_service_status, create_support_ticket


def test_service_status():
    result = check_service_status("authentication")
    assert result["status"] == "operational"


def test_unknown_service():
    result = check_service_status("unknown-service")
    assert "error" in result


def test_ticket_creation():
    result = create_support_ticket({
        "title": "Unable to access the API",
        "description": "The API returns HTTP 403 for valid credentials.",
        "category": "API Access",
        "priority": "High",
        "requester": "Demo User",
    })
    assert result["success"] is True
    assert result["ticket"]["ticket_id"].startswith("INC-")


def test_invalid_ticket():
    result = create_support_ticket({
        "title": "x",
        "description": "short",
        "category": "API Access",
        "priority": "High",
        "requester": "Demo User",
    })
    assert result["success"] is False
