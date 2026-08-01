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


def route_device_by_role(role: str | None, train_devices, switch_devices, device):
    """Append device to TrainDevices or SwitchDevices based on role.

    Returns the target name ('train'/'switch'), or None if role is unknown
    (device is not appended).
    """
    target = resolve_hub_target(role)
    if target == "train":
        train_devices.append(device)
        return target
    if target == "switch":
        switch_devices.append(device)
        return target
    return None
