"""Count overlapping observations at each (x, y) point."""

from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing


class StatCountOverlap:
    """Count observations at each unique (x, y) position.

    Produces columns: x, y, n (count), plus any passthrough group aesthetics.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        result = frame.group_by("x", "y").agg(nw.len().alias("n")).sort("x", "y")
        return nw.to_native(result)
