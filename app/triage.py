"""Simple keyword-based ticket routing."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import TicketPriority, TriageResult


@dataclass(frozen=True, slots=True)
class CategoryInfo:
    category: str
    team: str
    default_priority: TicketPriority
    keywords: tuple[str, ...]


DEFAULT_CATEGORIES = (
    CategoryInfo(
        "access",
        "identity-operations",
        TicketPriority.HIGH,
        (
            "login",
            "password",
            "account",
            "access",
            "mfa",
            "sign",
            "locked",
        ),
    ),
    CategoryInfo(
        "data_pipeline",
        "data-operations",
        TicketPriority.HIGH,
        (
            "file",
            "sftp",
            "etl",
            "pipeline",
            "data",
            "dashboard",
            "export",
            "records",
        ),
    ),
    CategoryInfo(
        "application_incident",
        "application-support",
        TicketPriority.URGENT,
        (
            "application",
            "api",
            "server",
            "error",
            "down",
            "timeout",
            "service",
            "checkout",
        ),
    ),
    CategoryInfo(
        "billing",
        "finance-operations",
        TicketPriority.MEDIUM,
        (
            "invoice",
            "payment",
            "charged",
            "amount",
            "billing",
        ),
    ),
)


class TicketClassifier:
    """Suggest a team by matching words in the ticket."""

    TOKEN_PATTERN = re.compile(r"[a-zA-Z]{2,}")

    def __init__(self, categories: tuple[CategoryInfo, ...] = DEFAULT_CATEGORIES) -> None:
        self.categories = categories

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        return [token.lower() for token in cls.TOKEN_PATTERN.findall(text)]

    def suggest(self, text: str, urgent: bool = False) -> TriageResult:
        tokens = self.tokenize(text)
        scores = {
            category.category: len(set(tokens).intersection(category.keywords))
            for category in self.categories
        }
        if not any(scores.values()):
            priority = TicketPriority.URGENT if urgent else TicketPriority.MEDIUM
            return TriageResult(
                category="general",
                team="support-desk",
                priority=priority,
                match_score=0.0,
                matched_terms=(),
            )
        best_name = max(scores, key=scores.get)
        best_category = next(category for category in self.categories if category.category == best_name)
        matched_terms = tuple(sorted(set(tokens).intersection(best_category.keywords)))
        match_score = scores[best_name] / max(len(best_category.keywords), 1)
        priority = TicketPriority.URGENT if urgent else best_category.default_priority
        return TriageResult(
            category=best_category.category,
            team=best_category.team,
            priority=priority,
            match_score=round(match_score, 2),
            matched_terms=matched_terms,
        )
