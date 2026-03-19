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
    """Create a FacetWrap specification."""
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
