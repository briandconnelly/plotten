from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.patches import Rectangle

from plotten._defaults import MAPPED_AESTHETICS
from plotten._enums import LegendPosition
from plotten.scales._color import ScaleColorContinuous
from plotten.themes._text_props import text_props

# Legend layout constants (figure-fraction coordinates)
_ENTRY_HEIGHT_BASE = 0.03
_TITLE_HEIGHT = 0.04
_MARGIN_PAD_BASE = 0.02
_LEGEND_GAP = 0.02
_COLORBAR_HEIGHT = 0.6
_MARKER_SIZE_BASE = 30
_LEGEND_RIGHT_X = 0.88
_LEGEND_LEFT_X = 0.01
_LEGEND_WIDTH_PER_COL = 0.12
_SWATCH_LEFT = 0.05
_SWATCH_CENTER = 0.12
_SWATCH_WIDTH = 0.15
_TEXT_LEFT = 0.25

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotten.scales._base import LegendEntry, ScaleBase
    from plotten.themes._theme import Theme


def draw_legend(
    fig: Figure,
    main_axes: list[Axes],
    scales: dict[str, ScaleBase],
    labs: Any,
    theme: Theme,
    guides: dict[str, Any] | None = None,
) -> None:
    """Draw legends for color/fill scales."""
    position = theme.legend_position
    if isinstance(position, str) and position == LegendPosition.NONE:
        return
    pos = position

    guides = guides or {}

    # Collect legend groups from scales that have legend entries
    legend_groups: list[tuple[str, str, ScaleBase]] = []
    for aes_name in MAPPED_AESTHETICS:
        if aes_name in scales:
            scale = scales[aes_name]
            entries = scale.legend_entries()
            if entries:
                # Determine title: guide override > labs > aesthetic name
                guide_spec = guides.get(aes_name)
                if guide_spec is not None and getattr(guide_spec, "title", None) is not None:
                    title = guide_spec.title
                else:
                    title = (
                        getattr(labs, aes_name, None) if labs is not None else None
                    ) or aes_name
                legend_groups.append((aes_name, title, scale))

    if not legend_groups:
        return

    # Compute total height of all legend groups so we can stack them vertically
    group_heights: list[float] = []
    for aes_name, _title, scale in legend_groups:
        entries = scale.legend_entries() or []
        guide_spec = guides.get(aes_name)
        if guide_spec is not None:
            entries = _apply_guide_overrides(entries, guide_spec)
        if isinstance(scale, ScaleColorContinuous):
            group_heights.append(_COLORBAR_HEIGHT)
        else:
            ncol = 1
            if guide_spec is not None:
                ncol = getattr(guide_spec, "ncol", None) or 1
            n_entries = len(entries)
            nrow_legend = -(-n_entries // ncol)
            entry_height = _ENTRY_HEIGHT_BASE * (theme.legend_spacing / 4.0)
            margin_pad = _MARGIN_PAD_BASE * (theme.legend_margin / 8.0)
            group_heights.append(_TITLE_HEIGHT + nrow_legend * entry_height + margin_pad)

    total_all = sum(group_heights) + _LEGEND_GAP * (len(group_heights) - 1)

    # Draw each legend group, stacking vertically
    y_cursor = 0.0  # cumulative offset from the top of the legend stack
    for i, (aes_name, title, scale) in enumerate(legend_groups):
        entries = scale.legend_entries()
        if not entries:
            continue

        guide_spec = guides.get(aes_name)

        # Apply guide overrides to entries
        if guide_spec is not None:
            entries = _apply_guide_overrides(entries, guide_spec)

        if isinstance(scale, ScaleColorContinuous):
            _draw_continuous_legend(
                fig,
                entries,
                title,
                scale,
                pos,
                theme,
                guide_spec,
                main_axes,
                y_offset=y_cursor,
                total_stack_height=total_all,
            )
        else:
            _draw_discrete_legend(
                fig,
                entries,
                title,
                pos,
                theme,
                guide_spec,
                main_axes,
                y_offset=y_cursor,
                total_stack_height=total_all,
            )
        y_cursor += group_heights[i] + _LEGEND_GAP


def _apply_guide_overrides(
    entries: list[LegendEntry],
    guide_spec: Any,
) -> list[LegendEntry]:
    """Apply guide overrides (reverse, override_aes) to legend entries."""
    from dataclasses import replace

    if getattr(guide_spec, "reverse", False):
        entries = list(reversed(entries))

    override_aes = getattr(guide_spec, "override_aes", None)
    if override_aes:
        entries = [replace(e, **override_aes) for e in entries]

    return entries


def _draw_legend_entry(
    legend_ax: Axes,
    entry: Any,
    y: float,
    step: float,
    legend_text_size: float,
    font_family: str,
    text_kw: dict[str, Any] | None = None,
    *,
    key_size: float = 20.0,
) -> None:
    """Draw a single legend entry (swatch + label) at position *y*."""
    marker_s = _MARKER_SIZE_BASE * (key_size / 20.0)
    line_x0 = _SWATCH_LEFT - 0.02  # left edge of line swatch
    line_x1 = _SWATCH_LEFT + _SWATCH_WIDTH  # right edge of line swatch
    if entry.shape is not None:
        legend_ax.scatter(
            [_SWATCH_CENTER],
            [y],
            marker=entry.shape,
            s=marker_s,
            c=entry.color or "black",
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.linetype is not None:
        legend_ax.plot(
            [line_x0, line_x1],
            [y, y],
            linestyle=entry.linetype,
            color=entry.color or "black",
            linewidth=1.5,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.size is not None and entry.color is None and entry.fill is None:
        legend_ax.scatter(
            [_SWATCH_CENTER],
            [y],
            s=entry.size * 5,
            c="black",
            alpha=entry.alpha if entry.alpha is not None else 1.0,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif (
        getattr(entry, "linewidth", None) is not None
        and entry.color is None
        and entry.fill is None
    ):
        legend_ax.plot(
            [line_x0, line_x1],
            [y, y],
            color="black",
            linewidth=entry.linewidth,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif getattr(entry, "hatch", None) is not None:
        rect = Rectangle(
            (_SWATCH_LEFT, y - step * 0.3),
            _SWATCH_WIDTH,
            step * 0.6,
            facecolor=entry.fill or entry.color or "#cccccc",
            edgecolor="black",
            hatch=entry.hatch,
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    elif entry.alpha is not None and entry.color is None and entry.fill is None:
        rect = Rectangle(
            (_SWATCH_LEFT, y - step * 0.3),
            _SWATCH_WIDTH,
            step * 0.6,
            facecolor="black",
            alpha=entry.alpha,
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    elif entry.fill is not None:
        rect = Rectangle(
            (_SWATCH_LEFT, y - step * 0.3),
            _SWATCH_WIDTH,
            step * 0.6,
            facecolor=entry.fill,
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    else:
        rect = Rectangle(
            (_SWATCH_LEFT, y - step * 0.3),
            _SWATCH_WIDTH,
            step * 0.6,
            facecolor=entry.color or "#cccccc",
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)

    kw: dict[str, Any] = {
        "fontsize": legend_text_size,
        "fontfamily": font_family,
        "verticalalignment": "center",
    }
    if text_kw:
        kw.update(text_kw)
    legend_ax.text(
        _TEXT_LEFT,
        y,
        entry.label,
        transform=legend_ax.transAxes,
        **kw,
    )


def _draw_legend_entry_at(
    legend_ax: Axes,
    entry: Any,
    x_offset: float,
    col_width: float,
    y: float,
    step: float,
    legend_text_size: float,
    font_family: str,
    text_kw: dict[str, Any] | None = None,
    *,
    key_size: float = 20.0,
) -> None:
    """Draw a legend entry at a specific column offset for multi-column layout."""
    swatch_x = x_offset + _SWATCH_LEFT * col_width
    swatch_cx = x_offset + _SWATCH_CENTER * col_width
    swatch_w = _SWATCH_WIDTH * col_width
    text_x = x_offset + _TEXT_LEFT * col_width
    marker_s = _MARKER_SIZE_BASE * (key_size / 20.0)

    if entry.shape is not None:
        legend_ax.scatter(
            [swatch_cx],
            [y],
            marker=entry.shape,
            s=marker_s,
            c=entry.color or "black",
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.linetype is not None:
        legend_ax.plot(
            [swatch_x, swatch_x + swatch_w],
            [y, y],
            linestyle=entry.linetype,
            color=entry.color or "black",
            linewidth=1.5,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.fill is not None:
        rect = Rectangle(
            (swatch_x, y - step * 0.3),
            swatch_w,
            step * 0.6,
            facecolor=entry.fill,
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    else:
        rect = Rectangle(
            (swatch_x, y - step * 0.3),
            swatch_w,
            step * 0.6,
            facecolor=entry.color or "#cccccc",
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)

    kw: dict[str, Any] = {
        "fontsize": legend_text_size,
        "fontfamily": font_family,
        "verticalalignment": "center",
    }
    if text_kw:
        kw.update(text_kw)
    legend_ax.text(
        text_x,
        y,
        entry.label,
        transform=legend_ax.transAxes,
        **kw,
    )


def _draw_discrete_legend(
    fig: Figure,
    entries: list,
    title: str,
    position: str | tuple[float, float],
    theme: Theme,
    guide_spec: Any = None,
    main_axes: list[Axes] | None = None,
    y_offset: float = 0.0,
    total_stack_height: float = 0.0,
) -> None:
    """Draw a discrete legend with colored rectangles and text labels."""
    # Determine number of columns from guide spec
    ncol = 1
    if guide_spec is not None:
        ncol = getattr(guide_spec, "ncol", None) or 1

    n_entries = len(entries)
    nrow_legend = -(-n_entries // ncol)  # ceiling division
    entry_height = _ENTRY_HEIGHT_BASE * (theme.legend_spacing / 4.0)
    margin_pad = _MARGIN_PAD_BASE * (theme.legend_margin / 8.0)
    total_height = _TITLE_HEIGHT + nrow_legend * entry_height + margin_pad
    legend_width = _LEGEND_WIDTH_PER_COL * ncol

    # Use total_stack_height for centering when multiple legend groups exist
    effective_height = total_stack_height if total_stack_height > 0 else total_height

    if isinstance(position, tuple):
        # Tuple coords are axes-relative (like ggplot2's c(x, y))
        lx, ly = position
        if main_axes:
            # Convert axes-relative to figure-relative
            ax_bbox = main_axes[0].get_position()
            x0 = ax_bbox.x0 + lx * ax_bbox.width
            y0 = ax_bbox.y0 + ly * ax_bbox.height - total_height - y_offset
        else:
            x0 = lx
            y0 = max(ly - total_height - y_offset, 0.0)
    elif position == LegendPosition.RIGHT:
        x0 = _LEGEND_RIGHT_X
        stack_top = 0.5 + effective_height / 2
        y0 = max(stack_top - y_offset - total_height, 0.05)
    elif position == LegendPosition.LEFT:
        x0 = _LEGEND_LEFT_X
        stack_top = 0.5 + effective_height / 2
        y0 = max(stack_top - y_offset - total_height, 0.05)
    elif position == LegendPosition.TOP:
        from matplotlib.figure import SubFigure

        if isinstance(fig, SubFigure):
            # Drawing in a dedicated legend subfig — fill it
            legend_width = max(legend_width, 0.5)
            x0 = 0.5 - legend_width / 2
            y0 = 0.0
            total_height = 1.0
        else:
            x0 = 0.5 - legend_width / 2
            y0 = _LEGEND_RIGHT_X - y_offset
    else:  # bottom
        x0 = 0.5 - legend_width / 2
        y0 = _LEGEND_LEFT_X + y_offset

    legend_ax = fig.add_axes((x0, y0, legend_width, total_height))
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 1)
    legend_ax.axis("off")

    # Legend background
    legend_bg = theme.legend_background
    if legend_bg is not None:
        legend_ax.set_facecolor(legend_bg)
        legend_ax.patch.set_visible(True)
    else:
        legend_ax.patch.set_visible(False)

    # Legend key background is available via theme.legend_key for future use

    legend_title_size = theme.legend_title_size or theme.label_size
    legend_text_size = theme.legend_text_size or theme.tick_size

    # Build text kwargs from element overrides
    title_kw = text_props(
        theme.legend_title_element,
        theme,
        default_size=legend_title_size,
        default_color="#000000",
        is_title=True,
    )
    title_kw.pop("ha", None)
    title_kw.setdefault("fontweight", "bold")

    entry_text_kw = text_props(
        theme.legend_text_element,
        theme,
        default_size=legend_text_size,
        default_color="#000000",
    )
    # Remove keys that are handled positionally
    for k in ("ha", "va", "fontsize", "fontfamily"):
        entry_text_kw.pop(k, None)
    # Extract overridden size/family for positional args
    lt_kw = text_props(
        theme.legend_text_element,
        theme,
        default_size=legend_text_size,
        default_color="#000000",
    )
    effective_text_size = lt_kw.get("fontsize", legend_text_size)
    effective_text_family = lt_kw.get("fontfamily", theme.font_family)

    # Resolve effective key size (width/height override key_size)
    effective_key_w = theme.legend_key_width or theme.legend_key_size
    effective_key_h = theme.legend_key_height or theme.legend_key_size

    # Resolve legend direction: guide_spec ncol > 1 implies horizontal when
    # theme.legend_direction is "horizontal", but we also support the theme
    # field directly.
    direction = theme.legend_direction or "vertical"

    from matplotlib.figure import SubFigure

    in_subfig = isinstance(fig, SubFigure)

    from matplotlib.figure import SubFigure

    in_subfig = isinstance(fig, SubFigure)

    if in_subfig:
        # In a dedicated legend subfig — single-line layout
        # Title on the left, entries flowing right, all vertically centered
        n = len(entries)
        # Compact centered layout: title + entries together
        # Each entry needs ~8% width, title needs ~15-20%
        entry_w = 0.08
        title_frac = min(max(len(title) * 0.015 + 0.05, 0.10), 0.25)
        total_content_w = title_frac + n * entry_w
        # Center the whole group
        start_x = max(0.5 - total_content_w / 2, 0.02)
        entry_zone_start = start_x + title_frac
        h_col_width = entry_w

        legend_ax.text(
            start_x + title_frac - 0.01,
            0.5,
            title,
            horizontalalignment="right",
            verticalalignment="center",
            transform=legend_ax.transAxes,
            **title_kw,
        )
        for i, entry in enumerate(entries):
            x_offset = entry_zone_start + i * h_col_width
            _draw_legend_entry_at(
                legend_ax,
                entry,
                x_offset,
                h_col_width,
                0.5,
                0.8,  # step for swatch height
                effective_text_size,
                effective_text_family,
                text_kw=entry_text_kw or None,
                key_size=effective_key_w,
            )
        return

    legend_ax.text(
        _SWATCH_LEFT,
        0.95,
        title,
        verticalalignment="top",
        transform=legend_ax.transAxes,
        **title_kw,
    )

    y_start = 1.0 - _TITLE_HEIGHT / total_height
    step = entry_height / total_height
    col_width = 1.0 / ncol

    if direction == "horizontal" and ncol == 1:
        # Horizontal layout: all entries in a single row
        h_col_width = 1.0 / max(len(entries), 1)
        for i, entry in enumerate(entries):
            x_offset = i * h_col_width
            y = y_start - 0.5 * step
            _draw_legend_entry_at(
                legend_ax,
                entry,
                x_offset,
                h_col_width,
                y,
                step,
                effective_text_size,
                effective_text_family,
                text_kw=entry_text_kw or None,
                key_size=effective_key_w,
            )
    else:
        for i, entry in enumerate(entries):
            row_idx = i // ncol
            col_idx = i % ncol
            y = y_start - (row_idx + 0.5) * step
            if ncol > 1:
                x_offset = col_idx * col_width
                _draw_legend_entry_at(
                    legend_ax,
                    entry,
                    x_offset,
                    col_width,
                    y,
                    step,
                    effective_text_size,
                    effective_text_family,
                    text_kw=entry_text_kw or None,
                    key_size=effective_key_w,
                )
            else:
                _draw_legend_entry(
                    legend_ax,
                    entry,
                    y,
                    step,
                    effective_text_size,
                    effective_text_family,
                    text_kw=entry_text_kw or None,
                    key_size=effective_key_h,
                )


def _draw_continuous_legend(
    fig: Figure,
    entries: list,
    title: str,
    scale: ScaleColorContinuous,
    position: str | tuple[float, float],
    theme: Theme,
    guide_spec: Any = None,
    main_axes: list[Axes] | None = None,
    y_offset: float = 0.0,
    total_stack_height: float = 0.0,
) -> None:
    """Draw a continuous colorbar legend."""
    # Determine dimensions from guide spec or defaults
    nbin = 256
    barwidth = None
    barheight = None
    if guide_spec is not None:
        nbin = getattr(guide_spec, "nbin", 256) or 256
        barwidth = getattr(guide_spec, "barwidth", None)
        barheight = getattr(guide_spec, "barheight", None)

    effective_height = total_stack_height if total_stack_height > 0 else _COLORBAR_HEIGHT

    if isinstance(position, tuple):
        lx, ly = position
        if main_axes:
            ax_bbox = main_axes[0].get_position()
            x0 = ax_bbox.x0 + lx * ax_bbox.width
            y0 = ax_bbox.y0 + ly * ax_bbox.height - _COLORBAR_HEIGHT - y_offset
            w, h = 0.03, _COLORBAR_HEIGHT
        else:
            x0, y0, w, h = lx, max(ly - _COLORBAR_HEIGHT - y_offset, 0.0), 0.03, _COLORBAR_HEIGHT
    elif position == LegendPosition.RIGHT:
        stack_top = 0.5 + effective_height / 2
        x0, w, h = 0.89, 0.03, _COLORBAR_HEIGHT
        y0 = max(stack_top - y_offset - h, 0.05)
    elif position == LegendPosition.LEFT:
        stack_top = 0.5 + effective_height / 2
        x0, w, h = _LEGEND_LEFT_X + 0.01, 0.03, _COLORBAR_HEIGHT
        y0 = max(stack_top - y_offset - h, 0.05)
    elif position == LegendPosition.TOP:
        x0, y0, w, h = 0.2, 0.92 - y_offset, 0.5, 0.03
    else:  # bottom
        x0, y0, w, h = 0.2, 0.02 + y_offset, 0.5, 0.03

    if barwidth is not None:
        w = barwidth
    if barheight is not None:
        h = barheight

    cbar_ax = fig.add_axes((x0, y0, w, h))

    # Create gradient
    gradient = np.linspace(0, 1, nbin).reshape(-1, 1)
    if position in ("top", "bottom"):
        gradient = gradient.reshape(1, -1)

    reverse = guide_spec is not None and getattr(guide_spec, "reverse", False)

    display_gradient = gradient if position in ("top", "bottom") else gradient[::-1]
    if reverse and position in ("top", "bottom"):
        display_gradient = display_gradient[:, ::-1]
    elif reverse:
        display_gradient = display_gradient[::-1]

    cbar_ax.imshow(
        display_gradient,
        aspect="auto",
        cmap=scale._cmap,
        extent=(0, 1, 0, 1),
    )

    legend_title_size = theme.legend_title_size or theme.label_size
    legend_text_size = theme.legend_text_size or theme.tick_size

    # Build title kwargs from element override
    cbar_title_kw = text_props(
        theme.legend_title_element,
        theme,
        default_size=legend_title_size,
        default_color="#000000",
        is_title=True,
    )
    for k in ("ha", "va", "rotation"):
        cbar_title_kw.pop(k, None)
    cbar_title_kw.setdefault("fontweight", "bold")

    # Tick labels
    lo, hi = scale.get_limits()
    breaks = scale.get_breaks()
    span = hi - lo if hi != lo else 1.0

    if position in ("right", "left"):
        cbar_ax.set_xticks([])
        tick_positions = [(b - lo) / span for b in breaks]
        cbar_ax.set_yticks(tick_positions)
        cbar_ax.set_yticklabels([f"{b:.3g}" for b in breaks], fontsize=legend_text_size)
        if position == "left":
            cbar_ax.yaxis.tick_left()
        else:
            cbar_ax.yaxis.tick_right()
    else:
        cbar_ax.set_yticks([])
        tick_positions = [(b - lo) / span for b in breaks]
        cbar_ax.set_xticks(tick_positions)
        cbar_ax.set_xticklabels([f"{b:.3g}" for b in breaks], fontsize=legend_text_size)

    # Remove spines
    for spine in cbar_ax.spines.values():
        spine.set_visible(False)

    # Title above colorbar
    if position in ("right", "left"):
        cbar_ax.set_title(title, pad=4, **cbar_title_kw)
    else:
        cbar_ax.set_xlabel(title, **cbar_title_kw)
