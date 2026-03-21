"""ggplot2-compatible linetype specification.

Supports three forms:
1. Numeric codes 0-6 (ggplot2 linetype numbers)
2. String names like "solid", "dashed", "longdash", "twodash"
3. Hex dash pattern strings (pairs of hex digits for on/off lengths)

Matplotlib accepts linestyle as a string ("solid", "dashed", etc.) or
a (offset, (on, off, ...)) tuple for custom dash patterns.
"""

from __future__ import annotations

from typing import Any

# ggplot2 numeric linetype codes -> matplotlib linestyle
_GGPLOT2_LINETYPES: dict[int, Any] = {
    0: "none",  # blank
    1: "solid",  # solid
    2: "dashed",  # dashed
    3: "dotted",  # dotted
    4: "dashdot",  # dotdash
    5: (0, (10, 3)),  # longdash
    6: (0, (8, 3, 2, 3)),  # twodash
}

# ggplot2 string names -> matplotlib linestyle
_LINETYPE_NAMES: dict[str, Any] = {
    "blank": "none",
    "solid": "solid",
    "dashed": "dashed",
    "dotted": "dotted",
    "dotdash": "dashdot",
    "longdash": (0, (10, 3)),
    "twodash": (0, (8, 3, 2, 3)),
    # matplotlib aliases (pass through)
    "dashdot": "dashdot",
    "none": "none",
}

# Short aliases commonly used in ggplot2 code
_SHORT_ALIASES: dict[str, Any] = {
    "--": "dashed",
    "..": "dotted",
    "-.": "dashdot",
    "-": "solid",
}


def _parse_hex_dash(pattern: str) -> tuple[int, tuple[float, ...]]:
    """Parse a ggplot2 hex dash pattern string.

    Each pair of hex digits specifies on/off lengths.
    E.g., "33" -> (0, (3, 3)), "3313" -> (0, (3, 3, 1, 3)).
    """
    segments = [int(c, 16) for c in pattern]
    return (0, tuple(float(s) for s in segments))


def resolve_linetype(value: str | int | None) -> Any:
    """Translate a ggplot2 linetype spec to a matplotlib linestyle.

    Parameters
    ----------
    value
        A ggplot2 numeric code (0-6), a ggplot2 string name (e.g. "longdash"),
        a hex dash pattern (e.g. "33"), or a matplotlib linestyle string
        (passed through as-is).

    Returns
    -------
    str or tuple
        A matplotlib linestyle string or (offset, dash) tuple.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return "solid"

    if isinstance(value, int):
        return _GGPLOT2_LINETYPES.get(value, "solid")

    if not isinstance(value, str):
        return value

    # Try as a numeric string
    if value.isdigit() and len(value) == 1:
        return _GGPLOT2_LINETYPES.get(int(value), "solid")

    # Try as a ggplot2 name (case-insensitive)
    lower = value.lower().strip()
    if lower in _LINETYPE_NAMES:
        return _LINETYPE_NAMES[lower]

    # Try short aliases
    if value in _SHORT_ALIASES:
        return _SHORT_ALIASES[value]

    # Try as hex dash pattern (all hex digits, even length)
    if len(value) >= 2 and all(c in "0123456789abcdefABCDEF" for c in value):
        return _parse_hex_dash(value)

    # Pass through as matplotlib linestyle
    return value
