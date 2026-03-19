"""Configurable arrow styles for segments and annotations."""

from __future__ import annotations

from dataclasses import dataclass

_ARROW_STYLES: dict[str, str] = {
    "open": "->",
    "closed": "-|>",
    "fancy": "fancy",
    "simple": "simple",
    "wedge": "wedge",
}


@dataclass(frozen=True, slots=True)
class Arrow:
    """Configurable arrow style for geom_segment and annotations."""

    style: str = "open"
    size: float = 1.0
    angle: float = 20.0

    def to_arrowstyle(self) -> str:
        """Return a matplotlib arrowstyle string."""
        base = _ARROW_STYLES.get(self.style, "->")
        if self.style in ("open", "closed"):
            return f"{base},head_length={self.size * 0.4},head_width={self.size * 0.2}"
        return base


def arrow(style: str = "open", size: float = 1.0, angle: float = 20.0) -> Arrow:
    """Create an arrow style specification.

    Parameters
    ----------
    style
        One of "open", "closed", "fancy", "simple", "wedge".
    size
        Relative size multiplier for the arrowhead.
    angle
        Arrow head angle in degrees.
    """
    if style not in _ARROW_STYLES:
        msg = f"Unknown arrow style: {style!r}. Valid styles: {sorted(_ARROW_STYLES)}"
        raise ValueError(msg)
    return Arrow(style=style, size=size, angle=angle)
