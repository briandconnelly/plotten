from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import narwhals as nw

from plotten._enums import Direction, FacetScales, StripPosition

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class FacetWrap:
    """Wrap panels by a single faceting variable."""

    facets: str
    n_rows: int | None = None
    n_cols: int | None = None
    scales: str | FacetScales = FacetScales.FIXED
    labeller: Callable[[str], str] | None = None
    drop: bool = True
    strip_position: str | StripPosition = StripPosition.TOP
    direction: str | Direction = Direction.HORIZONTAL

    def facet_data(self, data: Any) -> list[tuple[str, Any]]:
        """Split data by faceting column. Returns (label, native_df) pairs."""
        frame = nw.from_native(data)
        levels = sorted(frame.get_column(self.facets).unique().to_list(), key=str)
        result = []
        for level in levels:
            subset = frame.filter(nw.col(self.facets) == level)
            label = self.labeller(str(level)) if self.labeller else str(level)
            result.append((label, nw.to_native(subset)))
        return result

    def layout(self, n_panels: int) -> tuple[int, int]:
        """Compute (n_rows, n_cols) for the grid."""
        if self.n_cols is not None and self.n_rows is not None:
            return (self.n_rows, self.n_cols)
        if self.n_cols is not None:
            nr = math.ceil(n_panels / self.n_cols)
            return (nr, self.n_cols)
        if self.n_rows is not None:
            nc = math.ceil(n_panels / self.n_rows)
            return (self.n_rows, nc)
        nc = math.ceil(math.sqrt(n_panels))
        nr = math.ceil(n_panels / nc)
        return (nr, nc)

    def panel_position(self, idx: int, nrow: int, ncol: int) -> tuple[int, int]:
        """Map panel index to (row, col) grid position.

        When ``direction="h"`` (default), panels fill left-to-right (row-major).
        When ``direction="v"``, panels fill top-to-bottom (column-major).
        """
        if self.direction == "v":
            return (idx % nrow, idx // nrow)
        return divmod(idx, ncol)


def facet_wrap(
    facets: str,
    n_rows: int | None = None,
    n_cols: int | None = None,
    scales: str | FacetScales = FacetScales.FIXED,
    labeller: Callable[[str], str] | None = None,
    drop: bool = True,
    strip_position: str | StripPosition = StripPosition.TOP,
    direction: str | Direction = Direction.HORIZONTAL,
    # Deprecated aliases
    nrow: int | None = None,
    ncol: int | None = None,
) -> FacetWrap:
    """Wrap a one-dimensional sequence of panels into a two-dimensional grid.

    Parameters
    ----------
    facets : str
        Column name whose unique values define the panels.
    n_rows : int or None
        Number of rows in the panel grid.
    n_cols : int or None
        Number of columns in the panel grid.
    scales : str or FacetScales
        Whether axis scales are shared: ``FacetScales.FIXED`` (default),
        ``FacetScales.FREE``, ``FacetScales.FREE_X``, or ``FacetScales.FREE_Y``.
        Plain strings like ``"fixed"`` are also accepted.
    labeller : callable or None
        Function that transforms facet level strings into strip labels.
    drop : bool
        Whether to drop unused factor levels.
    strip_position : str or StripPosition
        Position of strip labels: ``StripPosition.TOP`` (default) or
        ``StripPosition.BOTTOM``. Plain strings are also accepted.
    direction : str or Direction
        Panel fill direction: ``Direction.HORIZONTAL`` (default) for row-major,
        ``Direction.VERTICAL`` for column-major. Plain strings ``"h"``/``"v"``
        are also accepted.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.facets import facet_wrap
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", n_cols=2)
    """
    if nrow is not None:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("nrow is deprecated. Use n_rows instead.")
        n_rows = nrow
    if ncol is not None:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("ncol is deprecated. Use n_cols instead.")
        n_cols = ncol
    return FacetWrap(
        facets=facets,
        n_rows=n_rows,
        n_cols=n_cols,
        scales=scales,
        labeller=labeller,
        drop=drop,
        strip_position=strip_position,
        direction=direction,
    )
