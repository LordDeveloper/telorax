from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class SignupContext:
    msisdn: int
    first_name: str
    last_name: str
    country_iso: str | None
    two_factor_password: str | None
    metadata: dict[str, object]


class SignupAutomation(Protocol):
    """Automates signup on an official Telegram mobile client."""

    async def signup(self, context: SignupContext) -> bytes:
        """Perform signup and return exported Telethon/Pyrogram session bytes."""
        ...
