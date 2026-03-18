from __future__ import annotations

from plotten.positions._base import PositionBase


class PositionIdentity(PositionBase):
    """No position adjustment — returns data unchanged."""

    def adjust(self, data: dict, params: dict) -> dict:
        return data


def position_identity() -> PositionIdentity:
    return PositionIdentity()
