from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Self


@dataclass(frozen=True, slots=True, kw_only=True)
class Theme:
    """Visual theme controlling the appearance of a plot."""

    # Text
    title_size: float = 14
    label_size: float = 12
    tick_size: float = 10
    font_family: str = "sans-serif"

    # Colors
    background: str = "#ffffff"
    panel_background: str = "#ebebeb"
    grid_color: str = "#ffffff"

    # Lines
    axis_line_width: float = 0.5
    grid_line_width: float = 0.5
    tick_length: float = 4.0

    # Spacing
    margin: float = 0.1
    legend_position: str = "right"

    def __add__(self, other: Theme) -> Self:
        """Layer *other* on top of *self*.

        For each field, if *other*'s value differs from the class default the
        value from *other* is used; otherwise the value from *self* is kept.
        """
        if not isinstance(other, Theme):
            return NotImplemented

        kwargs: dict[str, object] = {}
        for f in fields(self):
            other_val = getattr(other, f.name)
            if other_val != f.default:
                kwargs[f.name] = other_val
            else:
                kwargs[f.name] = getattr(self, f.name)
        return type(self)(**kwargs)
