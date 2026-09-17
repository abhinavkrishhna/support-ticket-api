"""The API routes for the support ticket app."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse

from app.api_models import (
    AssignmentCreate,
    DailyReportRead,
    OverviewRead,
    StatusUpdate,
    TicketCreate,
    TicketDetail,
    TicketRead,
    TriagePreviewRequest,
    TriageResultResponse,
)
from app.config import Settings
from app.database import Database
from app.models import TicketStatus
from app.ticket_repository import TicketNotFoundError, TicketRepository
from app.ticket_service import InvalidStatusChangeError, TicketService


def create_app(database_path: str | None = None) -> FastAPI:
    settings = Settings.from_environment()
    database = Database(database_path or settings.database_path)
    repository = TicketRepository(database)
    service = TicketService(repository)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        yield

    app = FastAPI(
        title="Support Ticket API",
        version="0.1.0",
        description="Create support tickets, set priorities, and see simple reports.",
        lifespan=lifespan,
    )

    @app.exception_handler(TicketNotFoundError)
    async def ticket_not_found_handler(_, error: TicketNotFoundError) -> JSONResponse:
        return _error_response(404, str(error))

    @app.exception_handler(InvalidStatusChangeError)
    async def invalid_status_handler(_, error: InvalidStatusChangeError) -> JSONResponse:
        return _error_response(409, str(error))

    @app.get("/health", tags=["platform"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/tickets/triage-preview",
        response_model=TriageResultResponse,
        tags=["triage"],
    )
    def triage_preview(payload: TriagePreviewRequest) -> object:
        return service.preview_triage(payload.title, payload.description, payload.urgent)

    @app.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED, tags=["tickets"])
    def create_ticket(payload: TicketCreate) -> object:
        return service.create_ticket(**payload.model_dump())

    @app.get("/tickets", response_model=list[TicketRead], tags=["tickets"])
    def list_tickets(
        ticket_status: TicketStatus | None = Query(default=None, alias="status"),
        team: str | None = Query(default=None, max_length=80),
        limit: int = Query(default=100, ge=1, le=500),
    ) -> object:
        return repository.list(status=ticket_status, team=team, limit=limit)

    @app.get("/tickets/{ticket_id}", response_model=TicketDetail, tags=["tickets"])
    def get_ticket(ticket_id: int) -> object:
        ticket = repository.get(ticket_id)
        return {**TicketRead.model_validate(ticket).model_dump(), "events": repository.events_for(ticket_id)}

    @app.patch("/tickets/{ticket_id}/status", response_model=TicketRead, tags=["tickets"])
    def update_ticket_status(ticket_id: int, payload: StatusUpdate) -> object:
        return service.change_status(ticket_id, payload.status)

    @app.post("/tickets/{ticket_id}/assign", response_model=TicketRead, tags=["tickets"])
    def assign_ticket(ticket_id: int, payload: AssignmentCreate) -> object:
        return service.assign(ticket_id, payload.assignee)

    @app.get("/analytics/overview", response_model=OverviewRead, tags=["analytics"])
    def overview() -> object:
        return service.overview()

    @app.get("/analytics/sla-queue", response_model=list[TicketRead], tags=["analytics"])
    def sla_queue(limit: int = Query(default=10, ge=1, le=100)) -> object:
        return service.sla_queue(limit)

    @app.get("/reports/daily", response_model=DailyReportRead, tags=["analytics"])
    def daily_report() -> object:
        return service.daily_report()

    return app


def _error_response(status_code: int, detail: str) -> JSONResponse:
    """Send a simple error response."""
    return JSONResponse(status_code=status_code, content={"detail": detail})


app = create_app()
