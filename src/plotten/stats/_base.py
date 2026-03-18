from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StatBase(ABC):
    """Base class for statistical transformations."""

    required_aes: frozenset[str] = frozenset()

    @abstractmethod
    def compute(self, df: Any) -> Any:
        """Transform a narwhals DataFrame, returning a narwhals DataFrame."""
        ...
