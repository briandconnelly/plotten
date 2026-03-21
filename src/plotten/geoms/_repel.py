"""Text and label geoms with automatic label repulsion (like ggrepel)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib.artist import Artist

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._text_helpers import extract_label_data, extract_text_params


def _get_text_extent(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    fontsize: float,
    font_kwargs: dict[str, Any],
    renderer: Any,
    bbox_props: dict[str, Any] | None = None,
) -> tuple[float, float]:
    """Get text bounding box size in display coordinates using the given renderer."""
    kwargs: dict[str, Any] = {"fontsize": fontsize, **font_kwargs}
    if bbox_props is not None:
        kwargs["bbox"] = bbox_props
    t = ax.text(x, y, text, **kwargs)
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
    renderer: Any,
    bbox_props: dict[str, Any] | None = None,
) -> list[tuple[float, float]]:
    """Compute repelled label positions. Returns adjusted (x, y) in data coords.

    ``renderer`` should be the actual renderer used for the final output so that
    text extents are measured at the correct DPI.
    """
    n = len(xs)
    if n == 0:
        return []

    rng = np.random.default_rng(seed)
    transform = ax.transData

    # Get bounding box sizes in display coords, including the frame for label geoms
    sizes = np.array(
        [
            _get_text_extent(ax, xs[i], ys[i], labels[i], fontsize, font_kwargs, renderer, bbox_props)
            for i in range(n)
        ]
    )
    pad = box_padding * fontsize
    sizes[:, 0] += pad * 2
    sizes[:, 1] += pad * 2
    half = sizes / 2

    # Convert data points to display coords
    origins = np.array([transform.transform((x, y)) for x, y in zip(xs, ys, strict=True)])

    # Initial positions: at the data point + nudge + tiny jitter to break ties
    nudge_display = transform.transform((nudge_x, nudge_y)) - transform.transform((0, 0))
    positions = origins.copy() + nudge_display
    positions += rng.uniform(-1.0, 1.0, positions.shape)

    point_pad_px = point_padding * fontsize

    # Clip labels to axis bounds, matching ggrepel's default (xlim/ylim = plot area).
    # This prevents bbox_inches="tight" from cropping labels at the figure edge.
    ax_bbox = ax.get_window_extent(renderer)
    x_lo, x_hi = ax_bbox.x0, ax_bbox.x1
    y_lo, y_hi = ax_bbox.y0, ax_bbox.y1

    forces = np.zeros((n, 2))

    for iteration in range(max_iter):
        # Simulated annealing: step shrinks from force → 0.1 * force
        step = force * max(0.1, 1.0 - iteration / max_iter)
        forces[:] = 0.0
        total_overlap = 0.0

        for i in range(n):
            # --- Repulsion from other label boxes ---
            for j in range(n):
                if i == j:
                    continue
                dx = positions[i, 0] - positions[j, 0]
                dy = positions[i, 1] - positions[j, 1]
                x_pen = half[i, 0] + half[j, 0] - abs(dx)
                y_pen = half[i, 1] + half[j, 1] - abs(dy)
                if x_pen > 0 and y_pen > 0:
                    total_overlap += x_pen * y_pen
                    # Apply force on both axes to avoid symmetry deadlocks in tight
                    # clusters (single-axis AMP can cancel for 3+ stacked labels).
                    sx = np.sign(dx) if abs(dx) > 1e-6 else rng.choice([-1.0, 1.0])
                    sy = np.sign(dy) if abs(dy) > 1e-6 else rng.choice([-1.0, 1.0])
                    forces[i, 0] += sx * x_pen
                    forces[i, 1] += sy * y_pen

            # --- Repulsion from data points ---
            for j in range(n):
                dx = positions[i, 0] - origins[j, 0]
                dy = positions[i, 1] - origins[j, 1]
                x_pen = half[i, 0] + point_pad_px - abs(dx)
                y_pen = half[i, 1] + point_pad_px - abs(dy)
                if x_pen > 0 and y_pen > 0:
                    sx = np.sign(dx) if abs(dx) > 1e-6 else rng.choice([-1.0, 1.0])
                    sy = np.sign(dy) if abs(dy) > 1e-6 else rng.choice([-1.0, 1.0])
                    forces[i, 0] += sx * x_pen * 0.5
                    forces[i, 1] += sy * y_pen * 0.5

            # --- Gentle attraction back toward origin ---
            forces[i, 0] += force_pull * (origins[i, 0] - positions[i, 0]) * 0.005
            forces[i, 1] += force_pull * (origins[i, 1] - positions[i, 1]) * 0.005

        if total_overlap == 0.0:
            break

        # Apply all forces at once (avoids order-dependent oscillation)
        delta = np.clip(forces * step, -50.0, 50.0)
        positions += delta

        # Keep labels inside the figure bounds
        positions[:, 0] = np.clip(positions[:, 0], x_lo + half[:, 0], x_hi - half[:, 0])
        positions[:, 1] = np.clip(positions[:, 1], y_lo + half[:, 1], y_hi - half[:, 1])

    # Unconditional clip: handles the early-exit case where labels don't overlap
    # each other (loop breaks before the per-iteration clip runs), but nudge or
    # jitter has pushed a label outside the axis bounds.
    positions[:, 0] = np.clip(positions[:, 0], x_lo + half[:, 0], x_hi - half[:, 0])
    positions[:, 1] = np.clip(positions[:, 1], y_lo + half[:, 1], y_hi - half[:, 1])

    # Convert back to data coords
    inv = transform.inverted()
    return [tuple(inv.transform(p)) for p in positions]


class _RepelArtist(Artist):
    """Deferred repulsion artist: positions are computed at actual draw time.

    By deferring to ``draw(renderer)``, text extents are measured at the correct
    DPI (the final output DPI), not the interactive display DPI.  This avoids the
    2× mismatch that occurs on macOS Retina where the interactive figure uses
    200 DPI but ``savefig(dpi=150)`` renders at 150 DPI.
    """

    def __init__(
        self,
        ax: Axes,
        xs: list[float],
        ys: list[float],
        labels: list[str],
        color: str,
        fontsize: float,
        font_kwargs: dict[str, Any],
        max_iter: int,
        force: float,
        force_pull: float,
        box_padding: float,
        point_padding: float,
        nudge_x: float,
        nudge_y: float,
        seed: int | None,
        segment_color: str,
        segment_size: float,
        segment_alpha: float,
        min_segment_length: float,
        bbox_props: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self.ax = ax
        self.xs = xs
        self.ys = ys
        self.labels = labels
        self.color = color
        self.fontsize = fontsize
        self.font_kwargs = font_kwargs
        self.max_iter = max_iter
        self.force = force
        self.force_pull = force_pull
        self.box_padding = box_padding
        self.point_padding = point_padding
        self.nudge_x = nudge_x
        self.nudge_y = nudge_y
        self.seed = seed
        self.segment_color = segment_color
        self.segment_size = segment_size
        self.segment_alpha = segment_alpha
        self.min_segment_length = min_segment_length
        self.bbox_props = bbox_props

    def get_window_extent(self, renderer: Any = None) -> Any:  # type: ignore[override]
        from matplotlib.transforms import Bbox

        return Bbox.null()

    def draw(self, renderer: Any) -> None:  # type: ignore[override]
        adjusted = _repel_labels(
            self.xs,
            self.ys,
            self.labels,
            self.ax,
            fontsize=self.fontsize,
            max_iter=self.max_iter,
            force=self.force,
            force_pull=self.force_pull,
            box_padding=self.box_padding,
            point_padding=self.point_padding,
            nudge_x=self.nudge_x,
            nudge_y=self.nudge_y,
            seed=self.seed,
            font_kwargs=self.font_kwargs,
            renderer=renderer,
            bbox_props=self.bbox_props,
        )

        from matplotlib.lines import Line2D
        from matplotlib.text import Text as MplText

        fig = self.ax.get_figure()
        transform = self.ax.transData

        # Draw connector segments — create Line2D directly, no add to ax
        for i, (adj_x, adj_y) in enumerate(adjusted):
            orig = transform.transform((self.xs[i], self.ys[i]))
            dest = transform.transform((adj_x, adj_y))
            seg_len = float(np.linalg.norm(np.array(orig) - np.array(dest)))
            if seg_len > self.min_segment_length:
                line = Line2D(
                    [self.xs[i], adj_x],
                    [self.ys[i], adj_y],
                    transform=transform,
                    color=self.segment_color,
                    linewidth=self.segment_size,
                    alpha=self.segment_alpha,
                    zorder=1,
                )
                line.set_figure(fig)
                line.draw(renderer)

        # Draw labels — create Text directly, no add to ax
        for i, (adj_x, adj_y) in enumerate(adjusted):
            kwargs: dict[str, Any] = {
                "transform": transform,
                "color": self.color,
                "fontsize": self.fontsize,
                **self.font_kwargs,
            }
            if self.bbox_props is not None:
                kwargs["bbox"] = self.bbox_props
            t = MplText(adj_x, adj_y, self.labels[i], **kwargs)
            t.set_figure(fig)
            t.draw(renderer)



class GeomTextRepel:
    """Draw text labels with automatic collision avoidance."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset(
        {"color", "alpha", "size", "fontsize", "ha", "va", "family"}
    )

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

        artist = _RepelArtist(
            ax=ax,
            xs=xs,
            ys=ys,
            labels=labels_list,
            color=color,
            fontsize=fontsize,
            font_kwargs=font_kwargs,
            max_iter=self.max_iter,
            force=self.force,
            force_pull=self.force_pull,
            box_padding=self.box_padding,
            point_padding=self.point_padding,
            nudge_x=self.nudge_x,
            nudge_y=self.nudge_y,
            seed=self.seed,
            segment_color=self.segment_color,
            segment_size=self.segment_size,
            segment_alpha=self.segment_alpha,
            min_segment_length=self.min_segment_length,
        )
        artist.set_figure(ax.get_figure())
        ax.add_artist(artist)


class GeomLabelRepel:
    """Draw labels with background boxes and automatic collision avoidance."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset(
        {"fill", "color", "alpha", "size", "fontsize", "ha", "va", "family"}
    )

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

        bbox_props = {
            "boxstyle": "round,pad=0.3",
            "facecolor": bg_color,
            "alpha": alpha,
            "edgecolor": color,
        }

        artist = _RepelArtist(
            ax=ax,
            xs=xs,
            ys=ys,
            labels=labels_list,
            color=color,
            fontsize=fontsize,
            font_kwargs=font_kwargs,
            max_iter=self.max_iter,
            force=self.force,
            force_pull=self.force_pull,
            box_padding=self.box_padding,
            point_padding=self.point_padding,
            nudge_x=self.nudge_x,
            nudge_y=self.nudge_y,
            seed=self.seed,
            segment_color=self.segment_color,
            segment_size=self.segment_size,
            segment_alpha=self.segment_alpha,
            min_segment_length=self.min_segment_length,
            bbox_props=bbox_props,
        )
        artist.set_figure(ax.get_figure())
        ax.add_artist(artist)
