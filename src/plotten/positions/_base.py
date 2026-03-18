from __future__ import annotations

from abc import ABC, abstractmethod


class PositionBase(ABC):
    """Base class for position adjustments."""

    @abstractmethod
    def adjust(self, data: dict, params: dict) -> dict: ...
