"""Default constants used across the rendering pipeline."""

from __future__ import annotations

from typing import Literal

# Aesthetics that support scale mapping and legend entries
MAPPED_AESTHETICS: tuple[str, ...] = (
    "color",
    "fill",
    "size",
    "alpha",
    "shape",
    "linetype",
    "linewidth",
    "hatch",
)

# Figure size
DEFAULT_FIGSIZE: tuple[float, float] = (8, 6)
DEFAULT_FACET_CELL_WIDTH: float = 4
DEFAULT_FACET_CELL_HEIGHT: float = 3.5

# Strip (facet panel label) padding
DEFAULT_STRIP_BOX_PAD: float = 3

# Default break counts for scales
DEFAULT_CONTINUOUS_BREAK_COUNT: int = 5
DEFAULT_POSITION_BREAK_COUNT: int = 6

# Layout region height ratios (figure-fraction)
LAYOUT_HEADER_H_TITLE_ONLY: float = 0.06
LAYOUT_HEADER_H_TITLE_SUBTITLE: float = 0.09
LAYOUT_LEGEND_TOP_H: float = 0.05
LAYOUT_CAPTION_H: float = 0.04

# Legend layout rects keyed by position string
LEGEND_LAYOUT_RECTS: dict[str, list[float]] = {
    "right": [0, 0, 0.85, 1],
    "left": [0.15, 0, 1, 1],
    "top": [0, 0, 1, 0.85],
    "bottom": [0, 0.15, 1, 1],
}

# Default geom colors
DEFAULT_GEOM_COLOR = "#333333"
DEFAULT_GEOM_FILL = "#4C72B0"

# Default geom sizes (matplotlib scatter `s` units = area in points²)
DEFAULT_POINT_SIZE: float = 20


def detect_backend() -> Literal["polars", "pandas"]:
    """Return the first available dataframe backend name."""
    try:
        import polars as _  # noqa: F401

        return "polars"
    except ImportError:
        return "pandas"
