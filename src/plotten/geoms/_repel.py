"""Text and label geoms with automatic label repulsion (like ggrepel)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._text_helpers import (
    draw_repel_connectors,
    extract_label_data,
    extract_text_params,
)


def _get_text_extent(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    fontsize: float,
    font_kwargs: dict[str, Any],
) -> tuple[float, float]:
    """Get text bounding box size in display coordinates."""
    renderer = ax.get_figure().canvas.get_renderer()  # type: ignore[union-attr]
    t = ax.text(x, y, text, fontsize=fontsize, **font_kwargs)
    bbox = t.get_window_extent(renderer)
    t.remove()
    return (bbox.width, bbox.height)


def _repel_labels(
    xs: list[float],
    ys: list[float],
    labels: list[str],
    ax: Axes,
    fontsize: float,
    max_iter: int,
    force: float,
    force_pull: float,
    box_padding: float,
    point_padding: float,
    nudge_x: float,
    nudge_y: float,
    seed: int | None,
    font_kwargs: dict[str, Any],
) -> list[tuple[float, float]]:
    """Compute repelled label positions. Returns adjusted (x, y) in data coords."""
    n = len(xs)
    if n == 0:
        return []

    rng = np.random.default_rng(seed)
    transform = ax.transData

    # Get bounding box sizes in display coords
    sizes = np.array(
        [_get_text_extent(ax, xs[i], ys[i], labels[i], fontsize, font_kwargs) for i in range(n)]
    )
    # Add padding (in points)
    pad = box_padding * fontsize
    sizes[:, 0] += pad * 2
    sizes[:, 1] += pad * 2

    # Convert data points to display coords
    origins = np.array([transform.transform((x, y)) for x, y in zip(xs, ys, strict=True)])

    # Apply nudge in display coords
    nudge_display = transform.transform((nudge_x, nudge_y)) - transform.transform((0, 0))
    positions = origins.copy() + nudge_display

    # Add small random jitter to break ties
    positions += rng.uniform(-2, 2, positions.shape)

    point_pad = point_padding * fontsize

    for _iteration in range(max_iter):
        moved = False
        for i in range(n):
            force_vec = np.zeros(2)

            # Repulsion from other labels
            for j in range(n):
                if i == j:
                    continue
                overlap = _box_overlap(positions[i], sizes[i], positions[j], sizes[j])
                if overlap > 0:
                    diff = positions[i] - positions[j]
                    dist = max(np.linalg.norm(diff), 0.01)
                    force_vec += force * diff / dist * (1 + overlap * 0.01)

            # Repulsion from data points
            for j in range(n):
                diff = positions[i] - origins[j]
                dist = np.linalg.norm(diff)
                half_w, half_h = sizes[i][0] / 2, sizes[i][1] / 2
                if dist < max(half_w, half_h) + point_pad:
                    if dist < 0.01:
                        diff = rng.uniform(-1, 1, 2)
                        dist = np.linalg.norm(diff)
                    force_vec += force * diff / dist

            # Attraction back to origin
            pull = origins[i] - positions[i]
            force_vec += force_pull * pull * 0.01

            if np.linalg.norm(force_vec) > 0.5:
                positions[i] += force_vec * 0.2
                moved = True

        if not moved:
            break

    # Convert back to data coords
    inv = transform.inverted()
    return [tuple(inv.transform(p)) for p in positions]


def _box_overlap(
    pos1: np.ndarray,
    size1: np.ndarray,
    pos2: np.ndarray,
    size2: np.ndarray,
) -> float:
    """Compute overlap area between two centered boxes. Returns 0 if no overlap."""
    x_overlap = max(
        0,
        min(pos1[0] + size1[0] / 2, pos2[0] + size2[0] / 2)
        - max(pos1[0] - size1[0] / 2, pos2[0] - size2[0] / 2),
    )
    y_overlap = max(
        0,
        min(pos1[1] + size1[1] / 2, pos2[1] + size2[1] / 2)
        - max(pos1[1] - size1[1] / 2, pos2[1] - size2[1] / 2),
    )
    return x_overlap * y_overlap


class GeomTextRepel:
    """Draw text labels with automatic collision avoidance."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False

    def __init__(
        self,
        *,
        max_iter: int = 500,
        force: float = 1.0,
        force_pull: float = 1.0,
        box_padding: float = 0.25,
        point_padding: float = 0.1,
        nudge_x: float = 0.0,
        nudge_y: float = 0.0,
        segment_color: str = "#666666",
        segment_size: float = 0.5,
        segment_alpha: float = 0.5,
        min_segment_length: float = 5.0,
        seed: int | None = 42,
    ) -> None:
        self.max_iter = max_iter
        self.force = force
        self.force_pull = force_pull
        self.box_padding = box_padding
        self.point_padding = point_padding
        self.nudge_x = nudge_x
        self.nudge_y = nudge_y
        self.segment_color = segment_color
        self.segment_size = segment_size
        self.segment_alpha = segment_alpha
        self.min_segment_length = min_segment_length
        self.seed = seed

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color, fontsize, font_kwargs = extract_text_params(params)
        xs, ys, labels_list = extract_label_data(data)

        fig = ax.get_figure()
        if fig is not None:
            fig.canvas.draw()

        adjusted = _repel_labels(
            xs,
            ys,
            labels_list,
            ax,
            fontsize=fontsize,
            max_iter=self.max_iter,
            force=self.force,
            force_pull=self.force_pull,
            box_padding=self.box_padding,
            point_padding=self.point_padding,
            nudge_x=self.nudge_x,
            nudge_y=self.nudge_y,
            seed=self.seed,
            font_kwargs=font_kwargs,
        )

        draw_repel_connectors(
            ax,
            xs,
            ys,
            adjusted,
            segment_color=self.segment_color,
            segment_size=self.segment_size,
            segment_alpha=self.segment_alpha,
            min_segment_length=self.min_segment_length,
        )

        for i, (adj_x, adj_y) in enumerate(adjusted):
            ax.text(adj_x, adj_y, labels_list[i], color=color, fontsize=fontsize, **font_kwargs)


class GeomLabelRepel:
    """Draw labels with background boxes and automatic collision avoidance."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False

    def __init__(
        self,
        *,
        max_iter: int = 500,
        force: float = 1.0,
        force_pull: float = 1.0,
        box_padding: float = 0.25,
        point_padding: float = 0.1,
        nudge_x: float = 0.0,
        nudge_y: float = 0.0,
        segment_color: str = "#666666",
        segment_size: float = 0.5,
        segment_alpha: float = 0.5,
        min_segment_length: float = 5.0,
        seed: int | None = 42,
        fill: str = "white",
        label_alpha: float = 0.8,
    ) -> None:
        self.max_iter = max_iter
        self.force = force
        self.force_pull = force_pull
        self.box_padding = box_padding
        self.point_padding = point_padding
        self.nudge_x = nudge_x
        self.nudge_y = nudge_y
        self.segment_color = segment_color
        self.segment_size = segment_size
        self.segment_alpha = segment_alpha
        self.min_segment_length = min_segment_length
        self.seed = seed
        self.fill = fill
        self.label_alpha = label_alpha

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color, fontsize, font_kwargs = extract_text_params(params)
        bg_color = params.get("fill", self.fill)
        alpha = params.get("alpha", self.label_alpha)
        xs, ys, labels_list = extract_label_data(data)

        fig = ax.get_figure()
        if fig is not None:
            fig.canvas.draw()

        adjusted = _repel_labels(
            xs,
            ys,
            labels_list,
            ax,
            fontsize=fontsize,
            max_iter=self.max_iter,
            force=self.force,
            force_pull=self.force_pull,
            box_padding=self.box_padding,
            point_padding=self.point_padding,
            nudge_x=self.nudge_x,
            nudge_y=self.nudge_y,
            seed=self.seed,
            font_kwargs=font_kwargs,
        )

        bbox_props = {
            "boxstyle": "round,pad=0.3",
            "facecolor": bg_color,
            "alpha": alpha,
            "edgecolor": color,
        }

        draw_repel_connectors(
            ax,
            xs,
            ys,
            adjusted,
            segment_color=self.segment_color,
            segment_size=self.segment_size,
            segment_alpha=self.segment_alpha,
            min_segment_length=self.min_segment_length,
        )

        for i, (adj_x, adj_y) in enumerate(adjusted):
            ax.text(
                adj_x,
                adj_y,
                labels_list[i],
                color=color,
                fontsize=fontsize,
                bbox=bbox_props,
                **font_kwargs,
            )
