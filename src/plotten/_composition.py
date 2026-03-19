from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class PlotAnnotation:
    """Shared annotation for a plot grid."""

    title: str | None = None
    subtitle: str | None = None
    caption: str | None = None
    tag_levels: str | None = None  # "A", "a", "1", "i"


@dataclass(frozen=True, slots=True)
class PlotGrid:
    """A composition of plots arranged horizontally or vertically."""

    plots: tuple = ()
    direction: str = "h"  # "h" or "v"
    widths: tuple[float, ...] | None = None
    annotation: PlotAnnotation | None = None

    def _replace(self, **kwargs: Any) -> PlotGrid:
        from dataclasses import fields as dc_fields

        vals = {f.name: getattr(self, f.name) for f in dc_fields(self)}
        vals.update(kwargs)
        return type(self)(**vals)

    def __or__(self, other: Any) -> PlotGrid:
        from plotten._plot import Plot

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="h")
        return NotImplemented

    def __truediv__(self, other: Any) -> PlotGrid:
        from plotten._plot import Plot

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="v")
        return NotImplemented

    def __add__(self, other: Any) -> PlotGrid:
        if isinstance(other, PlotAnnotation):
            return self._replace(annotation=other)
        return NotImplemented

    def show(self) -> None:
        """Render and display the grid."""
        fig = render_grid(self)
        fig.show()

    def save(
        self,
        path: str,
        dpi: int = 150,
        width: float | None = None,
        height: float | None = None,
    ) -> None:
        """Render and save the grid to a file."""
        import matplotlib.pyplot as plt

        fig = render_grid(self)
        if width is not None or height is not None:
            cur_w, cur_h = fig.get_size_inches()
            new_w = width if width is not None else cur_w
            new_h = height if height is not None else cur_h
            fig.set_size_inches(new_w, new_h)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)

    def _repr_png_(self) -> bytes:
        """Jupyter integration — display as PNG."""
        import matplotlib.pyplot as plt

        fig = render_grid(self)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()


def plot_annotation(**kwargs: Any) -> PlotAnnotation:
    """Create a PlotAnnotation."""
    return PlotAnnotation(**kwargs)


def plot_grid(
    *plots: Any,
    ncol: int | None = None,
    nrow: int | None = None,
    widths: list[float] | None = None,
    heights: list[float] | None = None,
) -> PlotGrid:
    """Arrange plots into a grid."""
    import math

    n = len(plots)
    if n == 0:
        return PlotGrid()

    if ncol is None and nrow is None:
        ncol = min(n, 3)
    if ncol is None:
        assert nrow is not None
        ncol = math.ceil(n / nrow)
    if nrow is None:
        nrow = math.ceil(n / ncol)

    # Build rows of HStacks, then VStack them
    rows: list[PlotGrid] = []
    for r in range(nrow):
        start = r * ncol
        row_plots = plots[start : start + ncol]
        if not row_plots:
            continue
        if len(row_plots) == 1:
            rows.append(
                row_plots[0]
                if isinstance(row_plots[0], PlotGrid)
                else PlotGrid(plots=row_plots, direction="h")
            )
        else:
            row_widths = tuple(widths) if widths else None
            rows.append(PlotGrid(plots=tuple(row_plots), direction="h", widths=row_widths))

    if len(rows) == 1:
        return rows[0]

    return PlotGrid(plots=tuple(rows), direction="v")


def _flatten_leaves(node: Any) -> list[Any]:
    """Collect leaf Plot objects from a PlotGrid tree."""
    from plotten._plot import Plot

    if isinstance(node, Plot):
        return [node]
    if isinstance(node, PlotGrid):
        leaves = []
        for child in node.plots:
            leaves.extend(_flatten_leaves(child))
        return leaves
    return []


def _tag_label(index: int, levels: str) -> str:
    """Generate a tag label for a panel."""
    match levels:
        case "A":
            return chr(ord("A") + index)
        case "a":
            return chr(ord("a") + index)
        case "1":
            return str(index + 1)
        case "i":
            romans = [
                "i",
                "ii",
                "iii",
                "iv",
                "v",
                "vi",
                "vii",
                "viii",
                "ix",
                "x",
                "xi",
                "xii",
                "xiii",
                "xiv",
                "xv",
                "xvi",
                "xvii",
                "xviii",
                "xix",
                "xx",
            ]
            return romans[index] if index < len(romans) else str(index + 1)
        case _:
            return chr(ord("A") + index)


def render_grid(grid: PlotGrid) -> Any:
    """Render a PlotGrid to a matplotlib Figure."""
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    # Count total leaves to size the figure
    leaves = _flatten_leaves(grid)
    n_leaves = max(len(leaves), 1)

    # Create figure
    fig = plt.figure(figsize=(6 * min(n_leaves, 3), 5 * max(1, (n_leaves + 2) // 3)))

    # Create top-level gridspec
    gs = GridSpec(1, 1, figure=fig)[0]

    # Track leaf axes for tagging
    leaf_axes: list[Any] = []

    _render_node(grid, fig, gs, leaf_axes)

    fig.tight_layout()

    # Apply annotation after tight_layout so we can adjust top properly
    ann = grid.annotation
    if ann is not None:
        has_title = ann.title is not None
        has_subtitle = ann.subtitle is not None

        # Check if any leaf plots have their own titles
        has_panel_titles = any(
            getattr(p, "labs", None) is not None and getattr(p.labs, "title", None) is not None
            for p in leaves
        )
        # Need more room when panel titles exist below the grid annotation
        extra = 0.06 if has_panel_titles else 0.0

        if has_title and has_subtitle:
            assert ann.title is not None
            assert ann.subtitle is not None
            fig.suptitle(ann.title, fontsize=14, fontweight="bold", y=0.98)
            fig.text(
                0.5,
                0.915,
                ann.subtitle,
                ha="center",
                va="top",
                fontsize=11,
                color="#555555",
                transform=fig.transFigure,
            )
            fig.subplots_adjust(top=0.88 - extra)
        elif has_title:
            assert ann.title is not None
            fig.suptitle(ann.title, fontsize=14, fontweight="bold")
            fig.subplots_adjust(top=0.93 - extra)
        elif has_subtitle:
            assert ann.subtitle is not None
            fig.suptitle(ann.subtitle, fontsize=11, color="#555555")
            fig.subplots_adjust(top=0.93 - extra)

        if ann.caption is not None:
            cur_bottom = fig.subplotpars.bottom
            fig.subplots_adjust(bottom=cur_bottom + 0.03)
            fig.text(0.99, 0.005, ann.caption, ha="right", va="bottom", fontsize=9)
        if ann.tag_levels is not None:
            for i, ax in enumerate(leaf_axes):
                tag = _tag_label(i, ann.tag_levels)
                ax.text(
                    0.02,
                    0.98,
                    tag,
                    transform=ax.transAxes,
                    fontsize=12,
                    fontweight="bold",
                    va="top",
                    ha="left",
                )

    return fig


def _render_node(node: Any, fig: Any, gs_slot: Any, leaf_axes: list) -> None:
    """Recursively render a PlotGrid tree into gridspec slots."""
    from plotten._plot import Plot
    from plotten._render._mpl import render_single
    from plotten._render._resolve import resolve

    if isinstance(node, Plot):
        from plotten.coords._polar import CoordPolar

        polar_kw = {"projection": "polar"} if isinstance(node.coord, CoordPolar) else {}
        ax = fig.add_subplot(gs_slot, **polar_kw)
        resolved = resolve(node)
        render_single(node, resolved, fig, ax)
        leaf_axes.append(ax)
        return

    if isinstance(node, PlotGrid):
        n = len(node.plots)
        if n == 0:
            return

        if node.direction == "h":
            if node.widths:
                ratios = list(node.widths[:n])
                while len(ratios) < n:
                    ratios.append(1.0)
            else:
                ratios = [1.0] * n
            sub_gs = gs_slot.subgridspec(1, n, width_ratios=ratios)
            for i, child in enumerate(node.plots):
                _render_node(child, fig, sub_gs[0, i], leaf_axes)
        else:  # "v"
            sub_gs = gs_slot.subgridspec(n, 1)
            for i, child in enumerate(node.plots):
                _render_node(child, fig, sub_gs[i, 0], leaf_axes)
