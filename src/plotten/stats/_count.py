from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing


class StatCount:
    """Group by x and count rows to produce y."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        result = frame.group_by("x").agg(nw.len().alias("y")).sort("x")

        # Add count and prop columns
        count_col = result.get_column("y")
        total = count_col.sum()
        result = result.with_columns(
            count_col.alias("count"),
            (count_col / total).alias("prop"),
        )

        return nw.to_native(result)
