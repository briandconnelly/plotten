"""Count overlapping observations at each (x, y) point."""

from __future__ import annotations

from collections import Counter
from typing import Any

import narwhals as nw


class StatCountOverlap:
    """Count observations at each unique (x, y) position.

    Produces columns: x, y, n (count), plus any passthrough group aesthetics.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_vals = frame.get_column("x").to_list()
        y_vals = frame.get_column("y").to_list()

        counts = Counter(zip(x_vals, y_vals, strict=True))

        result_x = []
        result_y = []
        result_n = []
        for (x, y), n in sorted(counts.items()):
            result_x.append(x)
            result_y.append(y)
            result_n.append(n)

        result = {"x": result_x, "y": result_y, "n": result_n}
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
