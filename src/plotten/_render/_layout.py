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
from plotten.themes._text_props import text_props

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
    figsize = _compute_figsize(resolved, theme)

    fig = plt.figure(figsize=figsize, layout="constrained")
    h_pad = theme.panel_spacing_y if theme.panel_spacing_y is not None else theme.panel_spacing
    w_pad = theme.panel_spacing_x if theme.panel_spacing_x is not None else theme.panel_spacing
    fig.get_layout_engine().set(h_pad=h_pad, w_pad=w_pad)  # type: ignore[union-attr]
    fig.patch.set_facecolor(theme.background)

    # Plot margin via constrained_layout rect
    if theme.plot_margin is not None:
        top, right, bottom, left = theme.plot_margin
        engine = fig.get_layout_engine()
        if engine is not None:
            engine.set(rect=(left, bottom, 1.0 - left - right, 1.0 - top - bottom))  # type: ignore[arg-type]

    # Plot background element
    from plotten.themes._elements import ElementRect

    if isinstance(theme.plot_background, ElementRect):
        if theme.plot_background.fill is not None:
            fig.patch.set_facecolor(theme.plot_background.fill)
        if theme.plot_background.color is not None:
            fig.patch.set_edgecolor(theme.plot_background.color)
            fig.patch.set_linewidth(theme.plot_background.size or 1.0)

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


def _compute_figsize(resolved: ResolvedPlot, theme: Theme | None = None) -> tuple[float, float]:
    """Compute figure size based on whether the plot is faceted."""
    if resolved.facet is not None:
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        w, h = DEFAULT_FACET_CELL_WIDTH * ncol, DEFAULT_FACET_CELL_HEIGHT * nrow
    else:
        w, h = DEFAULT_FIGSIZE

    # Apply aspect ratio if set
    if theme is not None and theme.aspect_ratio is not None:
        h = w * theme.aspect_ratio
    return (w, h)


def _render_header(
    header: SubFigure,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Render title and subtitle into the header subfigure."""
    labs = resolved.labs
    if labs is None:
        return

    title_kw = text_props(
        theme.plot_title,
        theme,
        default_size=theme.title_size,
        default_color=theme.title_color,
    )
    subtitle_kw = text_props(
        theme.plot_subtitle,
        theme,
        default_size=theme.subtitle_size or theme.label_size,
        default_color=theme.subtitle_color,
    )

    has_subtitle = labs.subtitle is not None
    has_title = labs.title is not None

    title_text = labs.title
    subtitle_text = labs.subtitle

    if has_title and has_subtitle and title_text is not None and subtitle_text is not None:
        header.suptitle(title_text, y=0.95, va="top", **title_kw)
        header.text(
            0.5,
            0.25,
            subtitle_text,
            ha=subtitle_kw.pop("ha", "center"),
            va=subtitle_kw.pop("va", "top"),
            **subtitle_kw,
        )
    elif has_title and title_text is not None:
        header.suptitle(title_text, **title_kw)
    elif has_subtitle and subtitle_text is not None:
        header.suptitle(subtitle_text, **subtitle_kw)


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

    caption_kw = text_props(
        theme.plot_caption,
        theme,
        default_size=theme.tick_size,
        default_color="#000000",
    )
    caption_subfig.text(
        0.99,
        0.5,
        labs.caption,
        ha=caption_kw.pop("ha", "right"),
        va=caption_kw.pop("va", "center"),
        **caption_kw,
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
    strip_kw = text_props(
        theme.strip_text,
        theme,
        default_size=theme.strip_text_size or theme.label_size,
        default_color=theme.strip_text_color,
    )
    strip_position = getattr(resolved.facet, "strip_position", "top")

    # Per-axis strip overrides
    strip_bg_x = theme.strip_background_x or strip_bg
    strip_kw_x = (
        text_props(
            theme.strip_text_x,
            theme,
            default_size=theme.strip_text_size or theme.label_size,
            default_color=theme.strip_text_color,
        )
        if theme.strip_text_x is not None
        else strip_kw
    )

    # Track which grid cells are occupied by panels
    occupied: set[tuple[int, int]] = set()

    for idx in range(n_panels):
        r, c = panel_pos(idx)
        occupied.add((r, c))
        ax = axes[r][c]

        # Strip label kwargs — use per-axis overrides for x (top/bottom) strips
        skw = dict(strip_kw_x)
        skw.pop("ha", None)
        skw.pop("va", None)
        effective_strip_bg = strip_bg_x

        # strip_placement: "inside" puts label inside panel, "outside" is default
        inside = theme.strip_placement == "inside"
        strip_y = 1.0 if not inside else 0.97
        strip_pad = 6 if not inside else -14

        if strip_position == "bottom":
            # Use xlabel for bottom strip — constrained_layout handles spacing
            ax.set_title("")
            ax.set_xlabel(
                resolved.panels[idx].label,
                **skw,
                bbox={
                    "facecolor": effective_strip_bg,
                    "edgecolor": "none",
                    "pad": DEFAULT_STRIP_BOX_PAD,
                },
            )
        else:
            ax.set_title(
                resolved.panels[idx].label,
                pad=strip_pad,
                y=strip_y,
                **skw,
                bbox={
                    "facecolor": effective_strip_bg,
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
    axis_title_kw = text_props(
        theme.axis_title,
        theme,
        default_size=theme.label_size,
        default_color="#000000",
    )
    # Per-axis size overrides
    ax_x_kw = dict(axis_title_kw)
    ax_y_kw = dict(axis_title_kw)
    if theme.axis_title_x_size is not None:
        ax_x_kw["fontsize"] = theme.axis_title_x_size
    if theme.axis_title_y_size is not None:
        ax_y_kw["fontsize"] = theme.axis_title_y_size
    # Remove ha/va — supxlabel/supylabel don't accept them
    for kw in (ax_x_kw, ax_y_kw):
        kw.pop("ha", None)
        kw.pop("va", None)
        kw.pop("rotation", None)

    if labs_obj and labs_obj.x and strip_position != "bottom":
        main_subfig.supxlabel(labs_obj.x, **ax_x_kw)
    if labs_obj and labs_obj.y:
        main_subfig.supylabel(labs_obj.y, **ax_y_kw)

    # For bottom strips, the xlabel is used for strip labels,
    # so shared x-axis label goes via supxlabel
    if labs_obj and labs_obj.x and strip_position == "bottom":
        main_subfig.supxlabel(labs_obj.x, **ax_x_kw)

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
