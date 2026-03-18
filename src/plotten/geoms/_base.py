from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GeomBase(ABC):
    """Base class for all geoms."""

    required_aes: frozenset[str] = frozenset()
    default_stat: type = None  # type: ignore[assignment]

    @abstractmethod
    def draw(self, data: Any, ax: Any, params: dict) -> None: ...
