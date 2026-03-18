from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.stats._base import StatBase


class StatCount(StatBase):
    """Group by x and count rows to produce y."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        result = frame.group_by("x").agg(nw.len().alias("y")).sort("x")
        return nw.to_native(result)
