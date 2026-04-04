from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Any, Self

from plotten._defaults import MAPPED_AESTHETICS
from plotten._enums import Direction, SizeUnit, TagLevel


@dataclass(frozen=True, slots=True, kw_only=True)
class InsetElement:
    """A plot to be rendered as an inset within another plot."""

    plot: Any
    left: float = 0.6
    bottom: float = 0.6
    width: float = 0.35
    height: float = 0.35


def inset_element(
    plot: Any,
    left: float = 0.6,
    bottom: float = 0.6,
    width: float = 0.35,
    height: float = 0.35,
) -> InsetElement:
    """Create an inset plot element.

    Parameters
    ----------
    plot : Plot
        The plot to embed as an inset.
    left, bottom : float
        Position of the inset's lower-left corner in axes-fraction coordinates (0-1).
    width, height : float
        Size of the inset in axes-fraction coordinates (0-1).
    """
    return InsetElement(plot=plot, left=left, bottom=bottom, width=width, height=height)


@dataclass(frozen=True, slots=True, kw_only=True)
class PlotAnnotation:
    """Shared annotation for a plot grid."""

    title: str | None = None
    subtitle: str | None = None
    caption: str | None = None
    tag_levels: str | TagLevel | None = None


@dataclass(frozen=True, slots=True)
class PlotGrid:
    """A composition of plots arranged horizontally or vertically."""

    plots: tuple = ()
    direction: str | Direction = Direction.HORIZONTAL
    widths: tuple[float, ...] | None = None
    annotation: PlotAnnotation | None = None
    collect_legends: bool = False

    def _replace(self, **kwargs: Any) -> Self:
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
        dpi: int = 300,
        width: float | None = None,
        height: float | None = None,
        units: str | SizeUnit = SizeUnit.INCHES,
        transparent: bool = False,
    ) -> None:
        """Render and save the grid to a file.

        Parameters
        ----------
        path : str
            Output file path. Format is inferred from the extension.
        dpi : int, optional
            Resolution in dots per inch (default 300).
        width, height : float, optional
            Figure dimensions in *units*. If only one is given, the other
            is calculated to preserve the aspect ratio.
        units : str or SizeUnit, optional
            Units for *width* / *height*: ``SizeUnit.INCHES`` (default),
            ``SizeUnit.CM``, ``SizeUnit.MM``, or ``SizeUnit.PX``.
        transparent : bool, optional
            If True, the figure and axes backgrounds are transparent.
        """
        import matplotlib.pyplot as plt

        fig = render_grid(self)
        if width is not None or height is not None:
            match units:
                case SizeUnit.INCHES:
                    factor = 1.0
                case SizeUnit.CM:
                    factor = 1 / 2.54
                case SizeUnit.MM:
                    factor = 1 / 25.4
                case SizeUnit.PX:
                    factor = 1 / dpi
                case _:
                    factor = 1.0
            cur_w, cur_h = fig.get_size_inches()
            aspect = cur_w / cur_h
            if width is not None and height is not None:
                new_w = width * factor
                new_h = height * factor
            elif width is not None:
                new_w = width * factor
                new_h = new_w / aspect
            else:
                # width is None, height must be not None (guarded by outer if)
                new_h = height * factor  # type: ignore[operator]
                new_w = new_h * aspect
            fig.set_size_inches(new_w, new_h)
        if transparent:
            fig.patch.set_alpha(0.0)
            for ax in fig.get_axes():
                ax.patch.set_alpha(0.0)
        fig.savefig(path, dpi=dpi, bbox_inches="tight", transparent=transparent)
        plt.close(fig)

    def _repr_png_(self) -> bytes:
        """Jupyter integration — display as PNG."""
        import matplotlib.pyplot as plt

        fig = render_grid(self)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    def _repr_mimebundle_(
        self, *, include: set[str] | None = None, exclude: set[str] | None = None
    ) -> dict[str, Any]:
        """Jupyter MIME bundle — provide PNG for format negotiation."""
        bundle: dict[str, Any] = {}
        wanted = include or {"image/png"}
        if exclude:
            wanted -= exclude
        if "image/png" in wanted:
            bundle["image/png"] = self._repr_png_()
        return bundle

    def _mime_(self) -> tuple[str, str]:
        """Marimo reactive notebook display protocol.

        Returns a PNG data-URI wrapped in an ``<img>`` tag.
        """
        import base64

        png_bytes = self._repr_png_()
        data_uri = base64.b64encode(png_bytes).decode("ascii")
        return (f'<img src="data:image/png;base64,{data_uri}" />', "text/html")


def plot_annotation(**kwargs: Any) -> PlotAnnotation:
    """Create a PlotAnnotation."""
    return PlotAnnotation(**kwargs)


def plot_grid(
    *plots: Any,
    n_cols: int | None = None,
    n_rows: int | None = None,
    widths: list[float] | None = None,
    heights: list[float] | None = None,
    guides: str | None = None,
    # Deprecated aliases
    ncol: int | None = None,
    nrow: int | None = None,
) -> PlotGrid:
    """Arrange plots into a grid.

    Parameters
    ----------
    n_cols : int or None
        Number of columns in the grid.
    n_rows : int or None
        Number of rows in the grid.
    guides : str | None
        If ``"collect"``, per-plot legends are suppressed and a single shared
        legend is drawn on the right side of the figure.
    """
    import math

    if nrow is not None:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("nrow is deprecated. Use n_rows instead.")
        n_rows = nrow
    if ncol is not None:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("ncol is deprecated. Use n_cols instead.")
        n_cols = ncol

    n = len(plots)
    if n == 0:
        return PlotGrid()

    if n_cols is not None and n_rows is not None:
        pass
    elif n_cols is not None:
        n_rows = math.ceil(n / n_cols)
    elif n_rows is not None:
        n_cols = math.ceil(n / n_rows)
    else:
        n_cols = min(n, 3)
        n_rows = math.ceil(n / n_cols)

    do_collect = guides == "collect"

    # Build rows of HStacks, then VStack them
    rows: list[PlotGrid] = []
    for r in range(n_rows):
        start = r * n_cols
        row_plots = plots[start : start + n_cols]
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
        result = rows[0]
    else:
        result = PlotGrid(plots=tuple(rows), direction="v")

    if do_collect:
        result = result._replace(collect_legends=True)
    return result


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

    ann = grid.annotation
    has_title = ann is not None and ann.title is not None
    has_subtitle = ann is not None and ann.subtitle is not None
    has_caption = ann is not None and ann.caption is not None

    # Determine vertical regions
    regions: list[str] = []
    ratios: list[float] = []

    if has_title or has_subtitle:
        header_h = 0.09 if (has_title and has_subtitle) else 0.06
        regions.append("header")
        ratios.append(header_h)

    regions.append("main")
    ratios.append(1.0)

    if has_caption:
        regions.append("caption")
        ratios.append(0.04)

    # Create figure with constrained_layout
    fig = plt.figure(
        figsize=(6 * min(n_leaves, 3), 5 * max(1, (n_leaves + 2) // 3)),
        layout="constrained",
    )

    if len(regions) == 1:
        main_fig = fig
    else:
        subfigs_raw = fig.subfigures(len(regions), 1, height_ratios=ratios)
        subfigs = list(subfigs_raw.flat) if hasattr(subfigs_raw, "flat") else [subfigs_raw]
        main_fig = subfigs[regions.index("main")]

        # Render header
        if "header" in regions:
            header_subfig = subfigs[regions.index("header")]
            if has_title and has_subtitle and ann is not None:
                header_subfig.suptitle(ann.title, fontsize=14, fontweight="bold", y=0.95, va="top")
                header_subfig.text(
                    0.5,
                    0.25,
                    ann.subtitle,
                    ha="center",
                    va="top",
                    fontsize=11,
                    color="#555555",
                )
            elif has_title and ann is not None:
                header_subfig.suptitle(ann.title, fontsize=14, fontweight="bold")
            elif has_subtitle and ann is not None:
                header_subfig.suptitle(ann.subtitle, fontsize=11, color="#555555")

        # Render caption
        if "caption" in regions and ann is not None and ann.caption is not None:
            caption_subfig = subfigs[regions.index("caption")]
            caption_subfig.text(0.99, 0.5, ann.caption, ha="right", va="center", fontsize=9)

    # Create top-level gridspec in the main region
    gs = GridSpec(1, 1, figure=main_fig)[0]

    # Track leaf axes for tagging
    leaf_axes: list[Any] = []

    _render_node(grid, main_fig, gs, leaf_axes, draw_legend=not grid.collect_legends)

    # Draw shared legend if collect_legends is enabled
    if grid.collect_legends:
        _draw_shared_legend(fig, leaves)

    # Apply tags
    if ann is not None and ann.tag_levels is not None:
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


def _draw_shared_legend(fig: Any, leaves: list[Any]) -> None:
    """Collect unique legend entries from all leaf plots and draw a shared legend."""
    from plotten._render._legend import _draw_discrete_legend
    from plotten._render._resolve import resolve
    from plotten.themes._theme import Theme, theme_get

    # Collect unique legend entries across all leaves
    seen_labels: set[str] = set()
    all_entries: list[Any] = []
    shared_title = ""

    for leaf in leaves:
        resolved = resolve(leaf)
        for aes_name in MAPPED_AESTHETICS:
            if aes_name in resolved.scales:
                scale = resolved.scales[aes_name]
                entries = scale.legend_entries()
                if entries:
                    if not shared_title:
                        labs = resolved.labs
                        shared_title = (
                            getattr(labs, aes_name, None) if labs is not None else None
                        ) or aes_name
                    for entry in entries:
                        if entry.label not in seen_labels:
                            seen_labels.add(entry.label)
                            all_entries.append(entry)

    if not all_entries:
        return

    theme: Theme = theme_get()
    # Make room for legend via constrained_layout rect
    engine = fig.get_layout_engine()
    if engine is not None:
        engine.set(rect=[0, 0, 0.85, 1])

    from plotten._enums import LegendPosition

    _draw_discrete_legend(fig, all_entries, shared_title, LegendPosition.RIGHT, theme)


def _render_node(
    node: Any,
    fig: Any,
    gs_slot: Any,
    leaf_axes: list,
    *,
    draw_legend: bool = True,
) -> None:
    """Recursively render a PlotGrid tree into gridspec slots."""
    from plotten._plot import Plot
    from plotten._render._mpl import render_single
    from plotten._render._resolve import resolve

    if isinstance(node, Plot):
        from plotten.coords._polar import CoordPolar

        polar_kw = {"projection": "polar"} if isinstance(node.coord, CoordPolar) else {}
        ax = fig.add_subplot(gs_slot, **polar_kw)
        resolved = resolve(node)
        render_single(node, resolved, fig, ax, draw_legend=draw_legend)
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
                _render_node(child, fig, sub_gs[0, i], leaf_axes, draw_legend=draw_legend)
        else:  # "v"
            sub_gs = gs_slot.subgridspec(n, 1)
            for i, child in enumerate(node.plots):
                _render_node(child, fig, sub_gs[i, 0], leaf_axes, draw_legend=draw_legend)
