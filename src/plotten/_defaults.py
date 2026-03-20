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

# Default geom colors
DEFAULT_GEOM_COLOR = "#333333"
DEFAULT_GEOM_FILL = "#4C72B0"


def detect_backend() -> Literal["polars", "pandas"]:
    """Return the first available dataframe backend name."""
    try:
        import polars as _  # noqa: F401

        return "polars"
    except ImportError:
        return "pandas"
