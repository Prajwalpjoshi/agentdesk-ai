
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class TicketRequest(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=1000)
    category: Literal[
        "Authentication",
        "API Access",
        "Service Outage",
        "General IT"
    ] = "General IT"
    priority: Literal["Low", "Medium", "High"] = "Medium"
    requester: str = Field(min_length=2, max_length=100)

    @field_validator("title", "description", "requester")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip()


class AgentResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    ticket_id: str | None = None
