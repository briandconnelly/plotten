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
    LAYOUT_CAPTION_H,
    LAYOUT_HEADER_H_TITLE_ONLY,
    LAYOUT_HEADER_H_TITLE_SUBTITLE,
    LAYOUT_LEGEND_TOP_H,
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

    When *legend_position* is ``"top"`` and a header is present, a dedicated
    legend region is inserted between the header and main content so the
    legend renders below the subtitle.
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
        from plotten.themes._elements import Margin

        if isinstance(theme.plot_margin, Margin):
            fig_w, fig_h = fig.get_size_inches()
            top, right, bottom, left = theme.plot_margin.to_npc(fig_w, fig_h)
        else:
            top, right, bottom, left = theme.plot_margin
        engine = fig.get_layout_engine()
        if engine is not None:
            engine.set(rect=(left, bottom, 1.0 - left - right, 1.0 - top - bottom))  # type: ignore[arg-type]

    # Plot background element — inherit from theme.rect
    from plotten.themes._elements import ElementRect, merge_rect

    base_rect = theme.rect if isinstance(theme.rect, ElementRect) else None
    if isinstance(theme.plot_background, ElementRect):
        resolved_bg = merge_rect(theme.plot_background, base_rect)
        if isinstance(resolved_bg, ElementRect):
            if resolved_bg.fill is not None:
                fig.patch.set_facecolor(resolved_bg.fill)
            if resolved_bg.color is not None:
                fig.patch.set_edgecolor(resolved_bg.color)
                fig.patch.set_linewidth(resolved_bg.size or 1.0)

    # Determine layout structure
    regions: list[str] = []
    ratios: list[float] = []

    # Check if legend needs a dedicated top region
    legend_top = isinstance(theme.legend_position, str) and theme.legend_position == "top"

    if has_title or has_subtitle:
        header_h = (
            LAYOUT_HEADER_H_TITLE_SUBTITLE
            if (has_title and has_subtitle)
            else LAYOUT_HEADER_H_TITLE_ONLY
        )
        regions.append("header")
        ratios.append(header_h)

    if legend_top:
        regions.append("legend_top")
        ratios.append(LAYOUT_LEGEND_TOP_H)

    regions.append("main")
    ratios.append(1.0)

    if has_caption:
        regions.append("caption")
        ratios.append(LAYOUT_CAPTION_H)

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

    # Stash legend subfig on the figure for draw_legend to use
    if "legend_top" in regions:
        fig._plotten_legend_subfig = subfigs[regions.index("legend_top")]  # type: ignore[attr-defined]

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
        is_title=True,
    )
    if "fontweight" not in title_kw and theme.title_weight:
        title_kw["fontweight"] = theme.title_weight
    subtitle_kw = text_props(
        theme.plot_subtitle,
        theme,
        default_size=theme.subtitle_size or theme.label_size,
        default_color=theme.subtitle_color,
        is_title=True,
    )

    has_subtitle = labs.subtitle is not None
    has_title = labs.title is not None

    title_text = labs.title
    subtitle_text = labs.subtitle

    # Resolve title x-alignment from plot_title_position
    # "plot" (default) → left-aligned to full plot area (ggplot2 hjust=0)
    # "panel" → centered over panel area
    if theme.plot_title_position == "panel":
        title_ha = "center"
        title_x = 0.5
    else:
        title_ha = "left"
        title_x = 0.0

    if has_title and has_subtitle and title_text is not None and subtitle_text is not None:
        header.suptitle(title_text, x=title_x, ha=title_ha, y=0.95, va="top", **title_kw)
        sub_ha = subtitle_kw.pop("ha", title_ha)
        header.text(
            title_x,
            0.25,
            subtitle_text,
            ha=sub_ha,
            va=subtitle_kw.pop("va", "top"),
            **subtitle_kw,
        )
    elif has_title and title_text is not None:
        header.suptitle(title_text, x=title_x, ha=title_ha, **title_kw)
    elif has_subtitle and subtitle_text is not None:
        header.suptitle(subtitle_text, x=title_x, ha=title_ha, **subtitle_kw)


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
        default_size=theme.base_size if theme.base_size is not None else theme.tick_size,
        default_color="#000000",
    )
    # Resolve caption x-alignment from plot_caption_position
    # "plot" (default) → right-aligned to full plot area (ggplot2 hjust=1)
    # "panel" → right-aligned to panel area (approximated)
    if theme.plot_caption_position == "panel":
        cap_x = 0.99
        cap_ha = "right"
    else:
        cap_x = 1.0
        cap_ha = "right"
    caption_subfig.text(
        cap_x,
        0.5,
        labs.caption,
        ha=caption_kw.pop("ha", cap_ha),
        va=caption_kw.pop("va", "center"),
        **caption_kw,
    )


def render_tag(
    fig: Figure,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Render plot tag (e.g. 'A', 'B') into the figure.

    Positioning follows ``theme.plot_tag_position``:
    - ``"topleft"`` (default), ``"topright"``, ``"bottomleft"``, ``"bottomright"``
    - ``tuple[float, float]`` for custom (x, y) in figure coordinates.

    ``theme.plot_tag_location`` controls whether the tag is placed relative
    to the ``"plot"`` (default) or ``"panel"`` area (currently only "plot").
    """
    labs = resolved.labs
    if labs is None or labs.tag is None:
        return

    from plotten.themes._elements import ElementBlank

    if isinstance(theme.plot_tag, ElementBlank):
        return

    tag_kw = text_props(
        theme.plot_tag,
        theme,
        default_size=theme.title_size,
        default_color=theme.title_color,
        is_title=True,
    )
    tag_kw.setdefault("fontweight", "bold")

    # Determine position
    pos = theme.plot_tag_position or "topleft"
    if isinstance(pos, tuple):
        x, y = pos
        ha = "left"
        va = "top"
    else:
        positions = {
            "topleft": (0.02, 0.98, "left", "top"),
            "topright": (0.98, 0.98, "right", "top"),
            "bottomleft": (0.02, 0.02, "left", "bottom"),
            "bottomright": (0.98, 0.02, "right", "bottom"),
        }
        x, y, ha, va = positions.get(pos, positions["topleft"])

    fig.text(
        x,
        y,
        labs.tag,
        ha=tag_kw.pop("ha", ha),
        va=tag_kw.pop("va", va),
        **tag_kw,
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

    gridspec_kw: dict[str, Any] | None = None
    if theme.panel_widths is not None or theme.panel_heights is not None:
        gridspec_kw = {}
        if theme.panel_widths is not None:
            gridspec_kw["width_ratios"] = list(theme.panel_widths[:ncol])
        if theme.panel_heights is not None:
            gridspec_kw["height_ratios"] = list(theme.panel_heights[:nrow])

    axes = main_subfig.subplots(
        nrow,
        ncol,
        squeeze=False,
        subplot_kw=subplot_kw,
        gridspec_kw=gridspec_kw,
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

        def panel_pos(idx: int) -> tuple[int, int]:
            return divmod(idx, ncol)

    from plotten.themes._elements import resolve_background

    strip_fill, strip_edge, strip_edge_w = resolve_background(theme.strip_background)
    strip_bg_bbox = {
        "facecolor": strip_fill or "none",
        "edgecolor": strip_edge or "none",
        "linewidth": strip_edge_w or 0,
        "pad": DEFAULT_STRIP_BOX_PAD,
    }
    strip_kw = text_props(
        theme.strip_text,
        theme,
        default_size=theme.strip_text_size or theme.label_size,
        default_color=theme.strip_text_color,
        is_title=True,
    )
    if "fontweight" not in strip_kw and theme.strip_text_weight:
        strip_kw["fontweight"] = theme.strip_text_weight
    strip_position = getattr(resolved.facet, "strip_position", "top")

    # Per-axis strip overrides
    if theme.strip_background_x is not None:
        sx_fill, sx_edge, sx_edge_w = resolve_background(theme.strip_background_x)
        strip_bg_bbox_x = {
            "facecolor": sx_fill or "none",
            "edgecolor": sx_edge or "none",
            "linewidth": sx_edge_w or 0,
            "pad": DEFAULT_STRIP_BOX_PAD,
        }
    else:
        strip_bg_bbox_x = strip_bg_bbox
    strip_kw_x = (
        text_props(
            theme.strip_text_x,
            theme,
            default_size=theme.strip_text_size or theme.label_size,
            default_color=theme.strip_text_color,
            is_title=True,
        )
        if theme.strip_text_x is not None
        else strip_kw
    )

    # Per-axis y-strip overrides (row strips on the right side)
    if theme.strip_background_y is not None:
        sy_fill, sy_edge, sy_edge_w = resolve_background(theme.strip_background_y)
        strip_bg_bbox_y = {
            "facecolor": sy_fill or "none",
            "edgecolor": sy_edge or "none",
            "linewidth": sy_edge_w or 0,
            "pad": DEFAULT_STRIP_BOX_PAD,
        }
    else:
        strip_bg_bbox_y = strip_bg_bbox
    strip_kw_y = (
        text_props(
            theme.strip_text_y,
            theme,
            default_size=theme.strip_text_size or theme.label_size,
            default_color=theme.strip_text_color,
            is_title=True,
        )
        if theme.strip_text_y is not None
        else strip_kw
    )

    # Detect whether facet has separate row/col labels
    from plotten.facets._grid import FacetGrid

    has_row_strips = isinstance(resolved.facet, FacetGrid) and resolved.facet.rows is not None
    has_col_strips = not isinstance(resolved.facet, FacetGrid) or resolved.facet.cols is not None

    # Track which grid cells are occupied by panels
    occupied: set[tuple[int, int]] = set()

    # Determine right-edge column for y-strip placement
    max_col_per_row: dict[int, int] = {}

    for idx in range(n_panels):
        r, c = panel_pos(idx)
        occupied.add((r, c))
        if r not in max_col_per_row or c > max_col_per_row[r]:
            max_col_per_row[r] = c

        ax = axes[r][c]
        panel = resolved.panels[idx]

        # Choose x-strip label: use col_label if available, else full label
        x_label = (
            panel.col_label if (has_row_strips and panel.col_label is not None) else panel.label
        )

        # Strip label kwargs — use per-axis overrides for x (top/bottom) strips
        skw = dict(strip_kw_x)
        skw.pop("ha", None)
        skw.pop("va", None)
        effective_bbox = dict(strip_bg_bbox_x)

        # strip_placement: "inside" puts label inside panel, "outside" is default
        inside = theme.strip_placement == "inside"
        strip_y = 1.0 if not inside else 0.97
        strip_pad = 6 if not inside else -14

        # For facet_grid with rows+cols, only show col strip on first row
        show_x_strip = has_col_strips and bool(x_label)
        if has_row_strips and has_col_strips and r > 0:
            show_x_strip = False

        if show_x_strip:
            if strip_position == "bottom":
                ax.set_title("")
                ax.set_xlabel(
                    x_label,
                    **skw,
                    bbox=effective_bbox,
                )
            else:
                ax.set_title(
                    x_label,
                    pad=strip_pad,
                    y=strip_y,
                    **skw,
                    bbox=effective_bbox,
                )
        else:
            ax.set_title("")

    # Y-strips (row labels) on the right edge of each row
    if has_row_strips:
        skw_y = dict(strip_kw_y)
        skw_y.pop("ha", None)
        skw_y.pop("va", None)
        effective_bbox_y = dict(strip_bg_bbox_y)
        # Track which rows already have a y-strip
        rows_with_strip: set[int] = set()
        for idx in range(n_panels):
            r, c = panel_pos(idx)
            if r in rows_with_strip:
                continue
            if c != max_col_per_row.get(r, ncol - 1):
                continue
            row_label = resolved.panels[idx].row_label
            if not row_label:
                continue
            rows_with_strip.add(r)
            ax = axes[r][c]
            ax.annotate(
                row_label,
                xy=(1.0, 0.5),
                xycoords="axes fraction",
                xytext=(6, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                rotation=-90,
                bbox=effective_bbox_y,
                **skw_y,
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
        is_title=True,
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
