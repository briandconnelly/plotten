from __future__ import annotations

import difflib
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, ElementText


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
    legend_position: str | tuple[float, float] = "right"

    # Per-axis text sizing
    axis_title_x_size: float | None = None
    axis_title_y_size: float | None = None
    axis_text_x_size: float | None = None
    axis_text_y_size: float | None = None
    axis_text_x_rotation: float = 0
    axis_text_y_rotation: float = 0

    # Panel border
    panel_border_color: str | None = None
    panel_border_width: float = 1.0

    # Facet strip
    strip_background: str = "#d9d9d9"
    strip_text_size: float | None = None
    strip_text_color: str = "#000000"

    # Title/subtitle colors
    title_color: str = "#000000"
    subtitle_size: float | None = None
    subtitle_color: str = "#555555"

    # Legend styling
    legend_background: str | None = None
    legend_title_size: float | None = None
    legend_text_size: float | None = None

    # Grid per-axis control
    grid_major_x: bool = True
    grid_major_y: bool = True
    grid_minor_x: bool = False
    grid_minor_y: bool = False

    # Axis line visibility
    axis_line_x: bool = True
    axis_line_y: bool = True

    # Element overrides (take precedence over flat fields)
    axis_title: ElementText | ElementBlank | None = None
    axis_text: ElementText | ElementBlank | None = None
    plot_title: ElementText | ElementBlank | None = None
    plot_subtitle: ElementText | ElementBlank | None = None
    plot_caption: ElementText | ElementBlank | None = None
    panel_grid_major: ElementLine | ElementBlank | None = None
    panel_grid_minor: ElementLine | ElementBlank | None = None
    panel_border: ElementRect | ElementBlank | None = None
    strip_text: ElementText | ElementBlank | None = None
    legend_title_element: ElementText | ElementBlank | None = None
    legend_text_element: ElementText | ElementBlank | None = None

    def __add__(self, other: Theme) -> Self:
        """Layer *other* on top of *self*.

        For each field, if *other*'s value differs from the class default the
        value from *other* is used; otherwise the value from *self* is kept.
        """
        if not isinstance(other, Theme):
            return NotImplemented

        kwargs: dict[str, Any] = {}
        for f in fields(self):
            other_val = getattr(other, f.name)
            if other_val != f.default:
                kwargs[f.name] = other_val
            else:
                kwargs[f.name] = getattr(self, f.name)
        return type(self)(**kwargs)


def theme(**kwargs: Any) -> Theme:
    """Create a partial theme for incremental overrides.

    Validates that all keyword arguments are valid Theme fields,
    then returns a Theme instance suitable for composition via ``+``.

    Usage::

        ggplot(...) + theme_minimal() + theme(title_size=20, axis_text_x_rotation=45)
    """
    valid_fields = {f.name for f in fields(Theme)}
    invalid = set(kwargs) - valid_fields
    if invalid:
        suggestions: list[str] = []
        valid_list = sorted(valid_fields)
        for name in sorted(invalid):
            matches = difflib.get_close_matches(name, valid_list, n=2, cutoff=0.6)
            if matches:
                suggestions.append(f"  '{name}' — did you mean {matches}?")
            else:
                suggestions.append(f"  '{name}'")
        hint = "\n".join(suggestions)
        msg = f"Unknown theme properties:\n{hint}\nValid properties: {valid_list}"
        raise TypeError(msg)
    return Theme(**kwargs)


# Module-level global theme
_global_theme: Theme = Theme()


def theme_set(new_theme: Theme) -> Theme:
    """Set the global default theme, returning the previous one."""
    global _global_theme
    old = _global_theme
    _global_theme = new_theme
    return old


def theme_get() -> Theme:
    """Return the current global default theme."""
    return _global_theme


def theme_update(**kwargs: Any) -> Theme:
    """Update the global default theme with the given overrides.

    Returns the updated theme.
    """
    global _global_theme
    _global_theme = _global_theme + theme(**kwargs)
    return _global_theme
