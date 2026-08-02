# This Python file uses the following encoding: utf-8
from __future__ import annotations

from typing import Literal

HubTarget = Literal["train", "switch"]

KNOWN_ROLES: frozenset[str] = frozenset({"train", "switch"})


def resolve_hub_target(role: str | None) -> HubTarget | None:
    """Map hub role string to routing target, or None if unknown."""
    if role is None:
        return None
    normalized = role.strip().lower()
    if normalized in KNOWN_ROLES:
        return normalized  # type: ignore[return-value]
    return None
