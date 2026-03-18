from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GeomBase(ABC):
    """Base class for all geoms."""

    required_aes: frozenset[str] = frozenset()

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    @abstractmethod
    def draw(self, data: Any, ax: Any, params: dict) -> None: ...
