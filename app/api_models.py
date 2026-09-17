"""The data sent to and from the API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=120, examples=["Nightly sales file is missing"])
    description: str = Field(min_length=10, max_length=2_000)
    requester_email: EmailStr
    priority: TicketPriority | None = None
    team: str | None = Field(default=None, max_length=80)
    urgent: bool = False


class TriagePreviewRequest(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2_000)
    urgent: bool = False


class TriageResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    team: str
    priority: TicketPriority
    match_score: float
    matched_terms: tuple[str, ...]


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    requester_email: EmailStr
    category: str
    team: str
    priority: TicketPriority
    status: TicketStatus
    assignee: str | None
    created_at: datetime
    due_at: datetime
    resolved_at: datetime | None


class StatusUpdate(BaseModel):
    status: TicketStatus


class AssignmentCreate(BaseModel):
    assignee: str = Field(min_length=2, max_length=80, examples=["aisha.sharma"])


class TicketEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    event_type: str
    detail: str
    created_at: datetime


class TicketDetail(TicketRead):
    events: list[TicketEventRead]


class OverviewRead(BaseModel):
    total: int
    open: int
    resolved: int
    overdue: int
    by_status: dict[str, int]
    open_by_team: dict[str, int]
    by_category: dict[str, int]
    average_resolution_hours: float | None


class DailyReportRead(BaseModel):
    report_generated_at: datetime
    headline: str
    metrics: OverviewRead
    next_up: list[TicketRead]
