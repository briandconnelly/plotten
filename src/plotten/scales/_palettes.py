"""Built-in qualitative color palettes.

Palettes are registered as matplotlib ListedColormaps on first import so
they can be referenced by name in any scale that accepts a palette string.
"""

from __future__ import annotations

import matplotlib
from matplotlib.colors import ListedColormap

# Okabe-Ito (colorblind-safe)
# Source: https://jfly.uni-koeln.de/color/
OKABE_ITO: list[str] = [
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#999999",  # grey
]

# Paul Tol "bright" qualitative palette
# Source: https://personal.sron.nl/~pault/
TOL_BRIGHT: list[str] = [
    "#4477AA",  # blue
    "#EE6677",  # red
    "#228833",  # green
    "#CCBB44",  # yellow
    "#66CCEE",  # cyan
    "#AA3377",  # purple
    "#BBBBBB",  # grey
]

# Default discrete palette name
DEFAULT_DISCRETE_PALETTE: str = "okabe_ito"


def _register_palettes() -> None:
    """Register custom palettes with matplotlib's colormap registry."""
    _palettes = {
        "okabe_ito": OKABE_ITO,
        "tol_bright": TOL_BRIGHT,
    }
    for name, colors in _palettes.items():
        if name not in matplotlib.colormaps:
            matplotlib.colormaps.register(ListedColormap(colors, name=name), name=name)


_register_palettes()
