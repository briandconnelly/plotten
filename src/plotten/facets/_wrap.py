from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import narwhals as nw

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class FacetWrap:
    """Wrap panels by a single faceting variable."""

    facets: str
    nrow: int | None = None
    ncol: int | None = None
    scales: str = "fixed"
    labeller: Callable[[str], str] | None = None
    drop: bool = True
    strip_position: str = "top"
    dir: str = "h"

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
        """Compute (nrow, ncol) for the grid."""
        if self.ncol is not None and self.nrow is not None:
            return (self.nrow, self.ncol)
        if self.ncol is not None:
            nrow = math.ceil(n_panels / self.ncol)
            return (nrow, self.ncol)
        if self.nrow is not None:
            ncol = math.ceil(n_panels / self.nrow)
            return (self.nrow, ncol)
        ncol = math.ceil(math.sqrt(n_panels))
        nrow = math.ceil(n_panels / ncol)
        return (nrow, ncol)

    def panel_position(self, idx: int, nrow: int, ncol: int) -> tuple[int, int]:
        """Map panel index to (row, col) grid position.

        When ``dir="h"`` (default), panels fill left-to-right (row-major).
        When ``dir="v"``, panels fill top-to-bottom (column-major).
        """
        if self.dir == "v":
            return (idx % nrow, idx // nrow)
        return divmod(idx, ncol)


def facet_wrap(
    facets: str,
    nrow: int | None = None,
    ncol: int | None = None,
    scales: str = "fixed",
    labeller: Callable[[str], str] | None = None,
    drop: bool = True,
    strip_position: str = "top",
    dir: str = "h",
) -> FacetWrap:
    """Wrap a one-dimensional sequence of panels into a two-dimensional grid.

    Parameters
    ----------
    facets : str
        Column name whose unique values define the panels.
    nrow : int or None
        Number of rows in the panel grid.
    ncol : int or None
        Number of columns in the panel grid.
    scales : str
        Whether axis scales are shared: ``"fixed"`` (default), ``"free"``,
        ``"free_x"``, or ``"free_y"``.
    labeller : callable or None
        Function that transforms facet level strings into strip labels.
    drop : bool
        Whether to drop unused factor levels.
    strip_position : str
        Position of strip labels: ``"top"`` (default) or ``"bottom"``.
    dir : str
        Panel fill direction: ``"h"`` for row-major, ``"v"`` for column-major.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.facets import facet_wrap
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", ncol=2)
    """
    return FacetWrap(
        facets=facets,
        nrow=nrow,
        ncol=ncol,
        scales=scales,
        labeller=labeller,
        drop=drop,
        strip_position=strip_position,
        dir=dir,
    )
