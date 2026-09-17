"""App settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: str

    @classmethod
    def from_environment(cls) -> Settings:
        default_path = Path("data") / "support_tickets.db"
        return cls(database_path=os.getenv("SUPPORT_TICKET_DB_PATH", str(default_path)))
