from __future__ import annotations


class PositionIdentity:
    """No position adjustment — returns data unchanged."""

    def adjust(self, data: dict, params: dict) -> dict:
        return data


def position_identity() -> PositionIdentity:
    return PositionIdentity()
