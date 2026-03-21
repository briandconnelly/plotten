"""ggplot2-compatible shape specification.

Supports three forms:
1. Numeric codes 0-25 (ggplot2 shape numbers)
2. String names like "circle", "triangle", "square"
3. Matplotlib marker strings passed through as-is

Shapes 0-20 are outline-only or solid markers.
Shapes 21-25 are filled markers with separate border (color) and fill aesthetics --
these are mapped to their matplotlib equivalents but fill/border distinction
requires geom-level support.
"""

from __future__ import annotations

# ggplot2 numeric shape codes → matplotlib marker strings
# Reference: https://ggplot2.tidyverse.org/articles/ggplot2-specs.html#point
_GGPLOT2_SHAPES: dict[int, str] = {
    0: "s",  # square (open)
    1: "o",  # circle (open)
    2: "^",  # triangle up (open)
    3: "+",  # plus
    4: "x",  # cross
    5: "D",  # diamond (open)
    6: "v",  # triangle down (open)
    7: "s",  # square with cross -- approximate as square
    8: "*",  # asterisk
    9: "D",  # diamond with plus -- approximate as diamond
    10: "o",  # circle with plus -- approximate as circle
    11: "h",  # six-pointed star -- approximate as hexagon
    12: "s",  # square with plus -- approximate as square
    13: "o",  # circle with cross -- approximate as circle
    14: "^",  # square with triangle -- approximate as triangle
    15: ".",  # filled square (small) -- point
    16: "o",  # filled circle
    17: "^",  # filled triangle up
    18: "D",  # filled diamond
    19: "o",  # solid circle (larger)
    20: "o",  # bullet (small circle)
    # 21-25: filled shapes with separate border/fill
    21: "o",  # filled circle (border + fill)
    22: "s",  # filled square (border + fill)
    23: "D",  # filled diamond (border + fill)
    24: "^",  # filled triangle up (border + fill)
    25: "v",  # filled triangle down (border + fill)
}

# ggplot2 string names → matplotlib marker strings
_SHAPE_NAMES: dict[str, str] = {
    "circle": "o",
    "circle open": "o",
    "circle filled": "o",
    "circle cross": "o",
    "circle plus": "o",
    "circle small": ".",
    "square": "s",
    "square open": "s",
    "square filled": "s",
    "square cross": "s",
    "square plus": "s",
    "square triangle": "s",
    "diamond": "D",
    "diamond open": "D",
    "diamond filled": "D",
    "diamond plus": "D",
    "triangle": "^",
    "triangle open": "^",
    "triangle filled": "^",
    "triangle down": "v",
    "triangle down open": "v",
    "triangle down filled": "v",
    "plus": "+",
    "cross": "x",
    "asterisk": "*",
    "star": "*",
    "hexagon": "h",
    "pentagon": "p",
    "bullet": ".",
    "point": ".",
}


def resolve_shape(value: str | int) -> str:
    """Translate a ggplot2 shape spec to a matplotlib marker string.

    Parameters
    ----------
    value
        A ggplot2 numeric code (0-25), a ggplot2 string name (e.g. "circle"),
        or a matplotlib marker string (passed through as-is).

    Returns
    -------
    str
        A matplotlib marker string.
    """
    if isinstance(value, int):
        return _GGPLOT2_SHAPES.get(value, "o")

    # Try as a numeric string
    if isinstance(value, str) and value.isdigit():
        return _GGPLOT2_SHAPES.get(int(value), "o")

    # Try as a ggplot2 name (case-insensitive)
    if isinstance(value, str):
        lower = value.lower().strip()
        if lower in _SHAPE_NAMES:
            return _SHAPE_NAMES[lower]

    # Pass through as matplotlib marker
    return str(value)
