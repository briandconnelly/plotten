from __future__ import annotations

from typing import Any


class StatIdentity:
    """Passthrough stat — returns data unchanged."""

    required_aes: frozenset[str] = frozenset()

    def compute(self, df: Any) -> Any:
        return df
