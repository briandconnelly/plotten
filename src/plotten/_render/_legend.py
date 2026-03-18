from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from plotten.scales._base import ScaleBase
from plotten.scales._color import ScaleColorContinuous
from plotten.themes._theme import Theme


def draw_legend(
    fig: Figure,
    main_axes: list[Any],
    scales: dict[str, ScaleBase],
    labs: Any,
    theme: Theme,
) -> None:
    """Draw legends for color/fill scales."""
    if theme.legend_position == "none":
        return

    # Collect legend groups from scales that have legend entries
    legend_groups: list[tuple[str, str, ScaleBase]] = []
    for aes_name in ("color", "fill"):
        if aes_name in scales:
            scale = scales[aes_name]
            entries = scale.legend_entries()
            if entries:
                title = (
                    getattr(labs, aes_name, None) if labs is not None else None
                ) or aes_name
                legend_groups.append((aes_name, title, scale))

    if not legend_groups:
        return

    pos = theme.legend_position

    # Shrink main axes to make room for legend
    if pos == "right":
        for ax in main_axes:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    elif pos == "left":
        for ax in main_axes:
            box = ax.get_position()
            ax.set_position(
                [box.x0 + box.width * 0.15, box.y0, box.width * 0.85, box.height]
            )
    elif pos == "top":
        for ax in main_axes:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width, box.height * 0.85])
    elif pos == "bottom":
        for ax in main_axes:
            box = ax.get_position()
            ax.set_position(
                [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
            )

    # Draw each legend group
    for _aes_name, title, scale in legend_groups:
        entries = scale.legend_entries()
        if not entries:
            continue

        if isinstance(scale, ScaleColorContinuous):
            _draw_continuous_legend(fig, entries, title, scale, pos, theme)
        else:
            _draw_discrete_legend(fig, entries, title, pos, theme)


def _draw_discrete_legend(
    fig: Figure,
    entries: list,
    title: str,
    position: str,
    theme: Theme,
) -> None:
    """Draw a discrete legend with colored rectangles and text labels."""
    n_entries = len(entries)
    entry_height = 0.03
    title_height = 0.04
    total_height = title_height + n_entries * entry_height + 0.02
    legend_width = 0.12

    if position == "right":
        x0 = 0.88
        y0 = max(0.5 - total_height / 2, 0.05)
    elif position == "left":
        x0 = 0.01
        y0 = max(0.5 - total_height / 2, 0.05)
    elif position == "top":
        x0 = 0.5 - legend_width / 2
        y0 = 0.88
    else:  # bottom
        x0 = 0.5 - legend_width / 2
        y0 = 0.01

    legend_ax = fig.add_axes([x0, y0, legend_width, total_height])
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 1)
    legend_ax.axis("off")

    # Title
    legend_ax.text(
        0.05,
        0.95,
        title,
        fontsize=theme.label_size,
        fontweight="bold",
        fontfamily=theme.font_family,
        verticalalignment="top",
        transform=legend_ax.transAxes,
    )

    # Entries (top to bottom)
    y_start = 1.0 - title_height / total_height
    step = entry_height / total_height

    for i, entry in enumerate(entries):
        y = y_start - (i + 0.5) * step
        # Colored rectangle
        rect = Rectangle(
            (0.05, y - step * 0.3),
            0.15,
            step * 0.6,
            facecolor=entry.color or "#cccccc",
            edgecolor="none",
            transform=legend_ax.transAxes,
        )
        legend_ax.add_patch(rect)
        # Label
        legend_ax.text(
            0.25,
            y,
            entry.label,
            fontsize=theme.tick_size,
            fontfamily=theme.font_family,
            verticalalignment="center",
            transform=legend_ax.transAxes,
        )


def _draw_continuous_legend(
    fig: Figure,
    entries: list,
    title: str,
    scale: ScaleColorContinuous,
    position: str,
    theme: Theme,
) -> None:
    """Draw a continuous colorbar legend."""
    if position == "right":
        x0, y0, w, h = 0.89, 0.15, 0.03, 0.6
    elif position == "left":
        x0, y0, w, h = 0.02, 0.15, 0.03, 0.6
    elif position == "top":
        x0, y0, w, h = 0.2, 0.92, 0.5, 0.03
    else:  # bottom
        x0, y0, w, h = 0.2, 0.02, 0.5, 0.03

    cbar_ax = fig.add_axes([x0, y0, w, h])

    # Create gradient
    gradient = np.linspace(0, 1, 256).reshape(-1, 1)
    if position in ("top", "bottom"):
        gradient = gradient.reshape(1, -1)

    cbar_ax.imshow(
        gradient if position in ("top", "bottom") else gradient[::-1],
        aspect="auto",
        cmap=scale._cmap,
        extent=[0, 1, 0, 1],
    )

    # Tick labels
    lo, hi = scale.get_limits()
    breaks = scale.get_breaks()
    span = hi - lo if hi != lo else 1.0

    if position in ("right", "left"):
        cbar_ax.set_xticks([])
        tick_positions = [(b - lo) / span for b in breaks]
        cbar_ax.set_yticks(tick_positions)
        cbar_ax.set_yticklabels([f"{b:.3g}" for b in breaks], fontsize=theme.tick_size)
        if position == "left":
            cbar_ax.yaxis.tick_left()
        else:
            cbar_ax.yaxis.tick_right()
    else:
        cbar_ax.set_yticks([])
        tick_positions = [(b - lo) / span for b in breaks]
        cbar_ax.set_xticks(tick_positions)
        cbar_ax.set_xticklabels([f"{b:.3g}" for b in breaks], fontsize=theme.tick_size)

    # Remove spines
    for spine in cbar_ax.spines.values():
        spine.set_visible(False)

    # Title above colorbar
    if position in ("right", "left"):
        cbar_ax.set_title(
            title, fontsize=theme.label_size, fontfamily=theme.font_family, pad=4
        )
    else:
        cbar_ax.set_xlabel(
            title, fontsize=theme.label_size, fontfamily=theme.font_family
        )
