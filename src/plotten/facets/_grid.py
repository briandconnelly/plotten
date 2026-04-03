from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import narwhals as nw

from plotten._enums import FacetScales

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class FacetGrid:
    """Grid panels by row and/or column variables."""

    rows: str | None = None
    cols: str | None = None
    scales: str | FacetScales = FacetScales.FIXED
    labeller: Callable[[str], str] | None = None

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
                    rl_label = self.labeller(str(rl)) if self.labeller else str(rl)
                    cl_label = self.labeller(str(cl)) if self.labeller else str(cl)
                    label = f"{rl_label} ~ {cl_label}"
                    result.append((label, nw.to_native(subset)))
        elif self.rows is not None:
            levels = sorted(frame.get_column(self.rows).unique().to_list(), key=str)
            for level in levels:
                subset = frame.filter(nw.col(self.rows) == level)
                label = self.labeller(str(level)) if self.labeller else str(level)
                result.append((label, nw.to_native(subset)))
        elif self.cols is not None:
            levels = sorted(frame.get_column(self.cols).unique().to_list(), key=str)
            for level in levels:
                subset = frame.filter(nw.col(self.cols) == level)
                label = self.labeller(str(level)) if self.labeller else str(level)
                result.append((label, nw.to_native(subset)))

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
    scales: str | FacetScales = FacetScales.FIXED,
    labeller: Callable[[str], str] | None = None,
) -> FacetGrid:
    """Create a grid of panels defined by row and/or column variables.

    Parameters
    ----------
    rows : str or None
        Column name whose unique values define the panel rows.
    cols : str or None
        Column name whose unique values define the panel columns.
    scales : str or FacetScales
        Whether axis scales are shared: ``FacetScales.FIXED`` (default),
        ``FacetScales.FREE``, ``FacetScales.FREE_X``, or ``FacetScales.FREE_Y``.
        Plain strings like ``"fixed"`` are also accepted.
    labeller : callable or None
        Function that transforms facet level strings into strip labels.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.facets import facet_grid
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "r": ["a", "a", "b", "b"], "c": ["x", "y", "x", "y"]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(rows="r", cols="c")
    """
    return FacetGrid(rows=rows, cols=cols, scales=scales, labeller=labeller)
