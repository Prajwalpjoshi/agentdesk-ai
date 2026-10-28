
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from schemas import TicketRequest


DATA_DIR = Path("data")
TICKETS_FILE = DATA_DIR / "tickets.json"


def check_service_status(service_name: str = "all") -> dict:
    """Check the simulated health status of IT services."""

    services = {
        "authentication": {
            "status": "operational",
            "message": "Login and authentication services are operational."
        },
        "api": {
            "status": "degraded",
            "message": "Elevated API response times are being simulated."
        },
        "database": {
            "status": "operational",
            "message": "Database connectivity is operational."
        },
    }

    name = service_name.strip().lower()

    if name in ("all", "all services"):
        return {"services": services}

    if name not in services:
        return {
            "error": "Unknown service.",
            "available_services": list(services.keys())
        }

    return {"service": name, **services[name]}


def create_support_ticket(ticket_data: dict) -> dict:
    """Validate and save a support ticket to a local JSON file."""

    try:
        ticket = TicketRequest.model_validate(ticket_data)
    except ValidationError as exc:
        return {
            "success": False,
            "error": "Ticket validation failed.",
            "details": exc.errors(include_input=False),
        }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    existing_tickets = []
    if TICKETS_FILE.exists():
        try:
            existing_tickets = json.loads(
                TICKETS_FILE.read_text(encoding="utf-8")
            )
            if not isinstance(existing_tickets, list):
                existing_tickets = []
        except (json.JSONDecodeError, OSError):
            existing_tickets = []

    ticket_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    record = {
        "ticket_id": ticket_id,
        **ticket.model_dump(),
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    existing_tickets.append(record)
    TICKETS_FILE.write_text(
        json.dumps(existing_tickets, indent=2),
        encoding="utf-8",
    )

    return {
        "success": True,
        "ticket": record,
        "message": "Support ticket created successfully.",
    }
