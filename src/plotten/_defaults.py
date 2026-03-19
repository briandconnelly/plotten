"""Default constants used across the rendering pipeline."""

from __future__ import annotations

# Figure size
DEFAULT_FIGSIZE: tuple[float, float] = (8, 6)
DEFAULT_FACET_CELL_WIDTH: float = 4
DEFAULT_FACET_CELL_HEIGHT: float = 3.5

# Title/subtitle y-positions
TITLE_Y: float = 0.98
SUBTITLE_Y_NORMAL: float = 0.915
SUBTITLE_Y_POLAR: float = 0.88

# Top margin when both title and subtitle are present
TOP_BOTH_NORMAL: float = 0.88
TOP_BOTH_POLAR: float = 0.78

# Top margin when only one of title/subtitle is present
TOP_SINGLE_NORMAL: float = 0.93
TOP_SINGLE_POLAR: float = 0.84

# Extra top-margin reduction when facet strip labels are present
FACET_STRIP_TOP_PAD: float = 0.08

# Caption position
CAPTION_X: float = 0.99
CAPTION_Y: float = 0.005
CAPTION_BOTTOM_PAD: float = 0.03

# Strip (facet panel label) padding
DEFAULT_STRIP_PAD: float = 6
DEFAULT_STRIP_BOX_PAD: float = 3

# Default break counts for scales
DEFAULT_CONTINUOUS_BREAK_COUNT: int = 5
DEFAULT_POSITION_BREAK_COUNT: int = 6
