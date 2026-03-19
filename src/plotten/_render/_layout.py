"""Layout engine using constrained_layout for automatic space management.

Replaces hardcoded figure-fraction positioning with matplotlib's
constrained_layout engine, which automatically allocates space for
titles, axis labels, tick labels, strip labels, and legends.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt

from plotten._defaults import (
    DEFAULT_FACET_CELL_HEIGHT,
    DEFAULT_FACET_CELL_WIDTH,
    DEFAULT_FIGSIZE,
    DEFAULT_STRIP_BOX_PAD,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure, SubFigure

    from plotten._render._resolve import ResolvedPlot
    from plotten.themes._theme import Theme


def create_figure(
    resolved: ResolvedPlot,
    theme: Theme,
) -> tuple[Figure, SubFigure, SubFigure | None]:
    """Create a figure with constrained_layout and optional header/caption regions.

    Returns (fig, main_subfig, caption_subfig).
    caption_subfig is None when no caption is present.
    """
    labs = resolved.labs
    has_title = labs is not None and labs.title is not None
    has_subtitle = labs is not None and labs.subtitle is not None
    has_caption = labs is not None and labs.caption is not None

    from plotten.themes._elements import ElementBlank

    if has_title and isinstance(theme.plot_title, ElementBlank):
        has_title = False
    if has_subtitle and isinstance(theme.plot_subtitle, ElementBlank):
        has_subtitle = False
    if has_caption and isinstance(theme.plot_caption, ElementBlank):
        has_caption = False

    # Compute figsize
    figsize = _compute_figsize(resolved)

    fig = plt.figure(figsize=figsize, layout="constrained")
    fig.get_layout_engine().set(h_pad=0.08, w_pad=0.08)  # type: ignore[union-attr]
    fig.patch.set_facecolor(theme.background)

    # Determine layout structure
    regions: list[str] = []
    ratios: list[float] = []

    if has_title or has_subtitle:
        header_h = 0.06
        if has_title and has_subtitle:
            header_h = 0.09
        regions.append("header")
        ratios.append(header_h)

    regions.append("main")
    ratios.append(1.0)

    if has_caption:
        regions.append("caption")
        ratios.append(0.04)

    if len(regions) == 1:
        # No header or caption — main is the whole figure
        return fig, fig, None  # type: ignore[return-value]

    subfigs_raw = fig.subfigures(len(regions), 1, height_ratios=ratios)
    # subfigures returns a numpy array; convert to list for indexing
    subfigs = list(subfigs_raw.flat) if hasattr(subfigs_raw, "flat") else [subfigs_raw]

    main_subfig = subfigs[regions.index("main")]
    caption_subfig = subfigs[regions.index("caption")] if "caption" in regions else None

    # Render header (title + subtitle)
    if "header" in regions:
        header_subfig = subfigs[regions.index("header")]
        _render_header(header_subfig, resolved, theme)

    return fig, main_subfig, caption_subfig


def _compute_figsize(resolved: ResolvedPlot) -> tuple[float, float]:
    """Compute figure size based on whether the plot is faceted."""
    if resolved.facet is not None:
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        return (DEFAULT_FACET_CELL_WIDTH * ncol, DEFAULT_FACET_CELL_HEIGHT * nrow)
    return DEFAULT_FIGSIZE


def _render_header(
    header: SubFigure,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Render title and subtitle into the header subfigure."""
    from plotten.themes._elements import ElementText

    labs = resolved.labs
    if labs is None:
        return

    title_size = theme.title_size
    title_color = theme.title_color
    title_family = theme.font_family

    if isinstance(theme.plot_title, ElementText):
        if theme.plot_title.size is not None:
            title_size = theme.plot_title.size
        if theme.plot_title.color is not None:
            title_color = theme.plot_title.color
        if theme.plot_title.family is not None:
            title_family = theme.plot_title.family

    subtitle_size = theme.subtitle_size or theme.label_size
    subtitle_color = theme.subtitle_color

    if isinstance(theme.plot_subtitle, ElementText):
        if theme.plot_subtitle.size is not None:
            subtitle_size = theme.plot_subtitle.size
        if theme.plot_subtitle.color is not None:
            subtitle_color = theme.plot_subtitle.color

    has_subtitle = labs.subtitle is not None
    has_title = labs.title is not None

    title_text = labs.title
    subtitle_text = labs.subtitle

    if has_title and has_subtitle and title_text is not None and subtitle_text is not None:
        header.suptitle(
            title_text,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
            y=0.95,
            va="top",
        )
        header.text(
            0.5,
            0.25,
            subtitle_text,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
        )
    elif has_title and title_text is not None:
        header.suptitle(
            title_text,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
        )
    elif has_subtitle and subtitle_text is not None:
        header.suptitle(
            subtitle_text,
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
        )


def render_caption(
    caption_subfig: SubFigure | None,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Render caption into the caption subfigure."""
    if caption_subfig is None:
        return
    labs = resolved.labs
    if labs is None or labs.caption is None:
        return

    from plotten.themes._elements import ElementBlank

    if isinstance(theme.plot_caption, ElementBlank):
        return

    caption_subfig.text(
        0.99,
        0.5,
        labs.caption,
        ha="right",
        va="center",
        fontsize=theme.tick_size,
        fontfamily=theme.font_family,
    )


def create_axes(
    main_subfig: Figure | SubFigure,
    resolved: ResolvedPlot,
    theme: Theme,
) -> Any:
    """Create axes within the main subfigure.

    Returns a single Axes for single-panel plots, or a 2D array for faceted.
    """
    from plotten.coords._polar import CoordPolar

    is_polar = isinstance(resolved.coord, CoordPolar)
    subplot_kw = {"projection": "polar"} if is_polar else {}

    if resolved.facet is None:
        ax = main_subfig.subplots(subplot_kw=subplot_kw)
        return ax

    n_panels = len(resolved.panels)
    nrow, ncol = resolved.facet.layout(n_panels)
    axes = main_subfig.subplots(
        nrow,
        ncol,
        squeeze=False,
        subplot_kw=subplot_kw,
    )
    return axes


def apply_facet_decorations(
    main_subfig: Figure | SubFigure,
    axes: Any,
    resolved: ResolvedPlot,
    theme: Theme,
    n_panels: int,
    nrow: int,
    ncol: int,
    panel_pos: Any = None,
) -> None:
    """Apply strip labels, shared axis labels, and hide empty axes for faceted plots."""
    if panel_pos is None:
        panel_pos = lambda idx: divmod(idx, ncol)  # noqa: E731

    strip_bg = theme.strip_background
    strip_text_size = theme.strip_text_size or theme.label_size
    strip_text_color = theme.strip_text_color
    strip_position = getattr(resolved.facet, "strip_position", "top")

    # Track which grid cells are occupied by panels
    occupied: set[tuple[int, int]] = set()

    for idx in range(n_panels):
        r, c = panel_pos(idx)
        occupied.add((r, c))
        ax = axes[r][c]

        if strip_position == "bottom":
            # Use xlabel for bottom strip — constrained_layout handles spacing
            ax.set_title("")
            ax.set_xlabel(
                resolved.panels[idx].label,
                fontsize=strip_text_size,
                color=strip_text_color,
                bbox={
                    "facecolor": strip_bg,
                    "edgecolor": "none",
                    "pad": DEFAULT_STRIP_BOX_PAD,
                },
            )
        else:
            ax.set_title(
                resolved.panels[idx].label,
                fontsize=strip_text_size,
                color=strip_text_color,
                pad=6,
                bbox={
                    "facecolor": strip_bg,
                    "edgecolor": "none",
                    "pad": DEFAULT_STRIP_BOX_PAD,
                },
            )

    # Hide empty axes (cells not occupied by any panel)
    for r in range(nrow):
        for c in range(ncol):
            if (r, c) not in occupied:
                axes[r][c].set_visible(False)

    # Shared axis labels via supxlabel/supylabel — constrained_layout aware
    labs_obj = resolved.labs
    axis_title_x_size = theme.axis_title_x_size or theme.label_size
    axis_title_y_size = theme.axis_title_y_size or theme.label_size

    if labs_obj and labs_obj.x and strip_position != "bottom":
        main_subfig.supxlabel(labs_obj.x, fontsize=axis_title_x_size)
    if labs_obj and labs_obj.y:
        main_subfig.supylabel(labs_obj.y, fontsize=axis_title_y_size)

    # For bottom strips, the xlabel is used for strip labels,
    # so shared x-axis label goes via supxlabel
    if labs_obj and labs_obj.x and strip_position == "bottom":
        main_subfig.supxlabel(labs_obj.x, fontsize=axis_title_x_size)

    # Determine which rows/cols are at the bottom/left edges
    max_row_per_col: dict[int, int] = {}
    for r_val, c_val in occupied:
        if c_val not in max_row_per_col or r_val > max_row_per_col[c_val]:
            max_row_per_col[c_val] = r_val

    # Suppress per-panel labels for non-edge panels
    for idx in range(n_panels):
        r, c = panel_pos(idx)
        ax = axes[r][c]
        is_bottom = r == max_row_per_col.get(c, nrow - 1)

        if strip_position != "bottom":
            # Only edge panels show axis labels
            if not is_bottom:
                ax.set_xlabel("")
                ax.tick_params(axis="x", labelbottom=False)
            else:
                ax.set_xlabel("")  # supxlabel handles the shared label
        else:
            # Bottom strip uses xlabel, non-bottom panels suppress ticks
            if not is_bottom:
                ax.tick_params(axis="x", labelbottom=False)

        if c != 0:
            ax.set_ylabel("")
            ax.tick_params(axis="y", labelleft=False)
        else:
            ax.set_ylabel("")  # supylabel handles the shared label
