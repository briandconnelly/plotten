from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.patches import Rectangle

from plotten._enums import LegendPosition
from plotten.scales._color import ScaleColorContinuous

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
    for aes_name in ("color", "fill", "size", "alpha", "shape", "linetype"):
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

    # Shrink main axes to make room for legend (not needed for tuple positions)
    if not isinstance(pos, tuple):
        match pos:
            case LegendPosition.RIGHT:
                for ax in main_axes:
                    box = ax.get_position()
                    ax.set_position((box.x0, box.y0, box.width * 0.85, box.height))
            case LegendPosition.LEFT:
                for ax in main_axes:
                    box = ax.get_position()
                    ax.set_position(
                        (box.x0 + box.width * 0.15, box.y0, box.width * 0.85, box.height)
                    )
            case LegendPosition.TOP:
                for ax in main_axes:
                    box = ax.get_position()
                    ax.set_position((box.x0, box.y0, box.width, box.height * 0.85))
            case LegendPosition.BOTTOM:
                for ax in main_axes:
                    box = ax.get_position()
                    ax.set_position(
                        (box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85)
                    )

    # Draw each legend group
    for aes_name, title, scale in legend_groups:
        entries = scale.legend_entries()
        if not entries:
            continue

        guide_spec = guides.get(aes_name)

        # Apply guide overrides to entries
        if guide_spec is not None:
            entries = _apply_guide_overrides(entries, guide_spec)

        if isinstance(scale, ScaleColorContinuous):
            _draw_continuous_legend(fig, entries, title, scale, pos, theme, guide_spec)
        else:
            _draw_discrete_legend(fig, entries, title, pos, theme, guide_spec)


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
    legend_ax: Axes, entry: Any, y: float, step: float, legend_text_size: float, font_family: str
) -> None:
    """Draw a single legend entry (swatch + label) at position *y*."""
    if entry.shape is not None:
        legend_ax.scatter(
            [0.12],
            [y],
            marker=entry.shape,
            s=30,
            c=entry.color or "black",
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.linetype is not None:
        legend_ax.plot(
            [0.03, 0.2],
            [y, y],
            linestyle=entry.linetype,
            color=entry.color or "black",
            linewidth=1.5,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.size is not None and entry.color is None and entry.fill is None:
        legend_ax.scatter(
            [0.12],
            [y],
            s=entry.size * 5,
            c="black",
            alpha=entry.alpha if entry.alpha is not None else 1.0,
            transform=legend_ax.transAxes,
            clip_on=False,
        )
    elif entry.alpha is not None and entry.color is None and entry.fill is None:
        rect = Rectangle(
            (0.05, y - step * 0.3),
            0.15,
            step * 0.6,
            facecolor="black",
            alpha=entry.alpha,
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    elif entry.fill is not None:
        rect = Rectangle(
            (0.05, y - step * 0.3),
            0.15,
            step * 0.6,
            facecolor=entry.fill,
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
    else:
        rect = Rectangle(
            (0.05, y - step * 0.3),
            0.15,
            step * 0.6,
            facecolor=entry.color or "#cccccc",
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)

    legend_ax.text(
        0.25,
        y,
        entry.label,
        fontsize=legend_text_size,
        fontfamily=font_family,
        verticalalignment="center",
        transform=legend_ax.transAxes,
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
) -> None:
    """Draw a legend entry at a specific column offset for multi-column layout."""
    swatch_x = x_offset + 0.05 * col_width
    swatch_cx = x_offset + 0.12 * col_width
    swatch_w = 0.15 * col_width
    text_x = x_offset + 0.25 * col_width

    if entry.shape is not None:
        legend_ax.scatter(
            [swatch_cx],
            [y],
            marker=entry.shape,
            s=30,
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

    legend_ax.text(
        text_x,
        y,
        entry.label,
        fontsize=legend_text_size,
        fontfamily=font_family,
        verticalalignment="center",
        transform=legend_ax.transAxes,
    )


def _draw_discrete_legend(
    fig: Figure,
    entries: list,
    title: str,
    position: str | tuple[float, float],
    theme: Theme,
    guide_spec: Any = None,
) -> None:
    """Draw a discrete legend with colored rectangles and text labels."""
    # Determine number of columns from guide spec
    ncol = 1
    if guide_spec is not None:
        ncol = getattr(guide_spec, "ncol", None) or 1

    n_entries = len(entries)
    nrow_legend = -(-n_entries // ncol)  # ceiling division
    entry_height = 0.03
    title_height = 0.04
    total_height = title_height + nrow_legend * entry_height + 0.02
    legend_width = 0.12 * ncol

    if isinstance(position, tuple):
        lx, ly = position
        x0 = lx
        y0 = max(ly - total_height, 0.0)
    elif position == LegendPosition.RIGHT:
        x0 = 0.88
        y0 = max(0.5 - total_height / 2, 0.05)
    elif position == LegendPosition.LEFT:
        x0 = 0.01
        y0 = max(0.5 - total_height / 2, 0.05)
    elif position == LegendPosition.TOP:
        x0 = 0.5 - legend_width / 2
        y0 = 0.88
    else:  # bottom
        x0 = 0.5 - legend_width / 2
        y0 = 0.01

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

    legend_title_size = theme.legend_title_size or theme.label_size
    legend_text_size = theme.legend_text_size or theme.tick_size

    legend_ax.text(
        0.05,
        0.95,
        title,
        fontsize=legend_title_size,
        fontweight="bold",
        fontfamily=theme.font_family,
        verticalalignment="top",
        transform=legend_ax.transAxes,
    )

    y_start = 1.0 - title_height / total_height
    step = entry_height / total_height
    col_width = 1.0 / ncol

    for i, entry in enumerate(entries):
        row_idx = i // ncol
        col_idx = i % ncol
        y = y_start - (row_idx + 0.5) * step
        if ncol > 1:
            # Offset x positions for multi-column layout
            x_offset = col_idx * col_width
            _draw_legend_entry_at(
                legend_ax,
                entry,
                x_offset,
                col_width,
                y,
                step,
                legend_text_size,
                theme.font_family,
            )
        else:
            _draw_legend_entry(legend_ax, entry, y, step, legend_text_size, theme.font_family)


def _draw_continuous_legend(
    fig: Figure,
    entries: list,
    title: str,
    scale: ScaleColorContinuous,
    position: str | tuple[float, float],
    theme: Theme,
    guide_spec: Any = None,
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

    if isinstance(position, tuple):
        lx, ly = position
        x0, y0, w, h = lx, max(ly - 0.6, 0.0), 0.03, 0.6
    elif position == LegendPosition.RIGHT:
        x0, y0, w, h = 0.89, 0.15, 0.03, 0.6
    elif position == LegendPosition.LEFT:
        x0, y0, w, h = 0.02, 0.15, 0.03, 0.6
    elif position == LegendPosition.TOP:
        x0, y0, w, h = 0.2, 0.92, 0.5, 0.03
    else:  # bottom
        x0, y0, w, h = 0.2, 0.02, 0.5, 0.03

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
        cbar_ax.set_title(title, fontsize=legend_title_size, fontfamily=theme.font_family, pad=4)
    else:
        cbar_ax.set_xlabel(title, fontsize=legend_title_size, fontfamily=theme.font_family)
