from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import narwhals as nw


@dataclass(frozen=True, slots=True)
class FacetGrid:
    """Grid panels by row and/or column variables."""

    rows: str | None = None
    cols: str | None = None
    scales: str = "fixed"

    def facet_data(self, data: Any) -> list[tuple[str, Any]]:
        """Split data by row/col variables. Returns (label, native_df) pairs."""
        frame = nw.from_native(data)
        result = []

        if self.rows is not None and self.cols is not None:
            row_levels = sorted(frame.get_column(self.rows).unique().to_list(), key=str)
            col_levels = sorted(frame.get_column(self.cols).unique().to_list(), key=str)
            for rl in row_levels:
                for cl in col_levels:
                    subset = frame.filter((nw.col(self.rows) == rl) & (nw.col(self.cols) == cl))
                    label = f"{rl} ~ {cl}"
                    result.append((label, nw.to_native(subset)))
        elif self.rows is not None:
            levels = sorted(frame.get_column(self.rows).unique().to_list(), key=str)
            for level in levels:
                subset = frame.filter(nw.col(self.rows) == level)
                result.append((str(level), nw.to_native(subset)))
        elif self.cols is not None:
            levels = sorted(frame.get_column(self.cols).unique().to_list(), key=str)
            for level in levels:
                subset = frame.filter(nw.col(self.cols) == level)
                result.append((str(level), nw.to_native(subset)))

        return result

    def layout(self, n_panels: int) -> tuple[int, int]:
        """Compute (nrow, ncol) for the grid."""
        if self.rows is not None and self.cols is not None:
            # Grid dimensions come from unique levels (n_panels = nrow * ncol)
            ncol = math.ceil(math.sqrt(n_panels))
            nrow = math.ceil(n_panels / ncol)
            return (nrow, ncol)
        if self.rows is not None:
            return (n_panels, 1)
        if self.cols is not None:
            return (1, n_panels)
        return (1, 1)


def facet_grid(
    rows: str | None = None,
    cols: str | None = None,
    scales: str = "fixed",
) -> FacetGrid:
    """Create a FacetGrid specification."""
    return FacetGrid(rows=rows, cols=cols, scales=scales)
