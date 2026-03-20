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

    # Per-axis text sizing (scalar shortcuts)
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

    # Grid per-axis control (boolean shortcuts)
    grid_major_x: bool = True
    grid_major_y: bool = True
    grid_minor_x: bool = False
    grid_minor_y: bool = False

    # Axis line visibility (boolean shortcuts)
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

    # Per-axis element overrides (ggplot2: axis.title.x, axis.title.y, etc.)
    axis_title_x: ElementText | ElementBlank | None = None
    axis_title_y: ElementText | ElementBlank | None = None
    axis_text_x: ElementText | ElementBlank | None = None
    axis_text_y: ElementText | ElementBlank | None = None

    # Axis ticks element (ggplot2: axis.ticks, axis.ticks.x, axis.ticks.y)
    axis_ticks: ElementLine | ElementBlank | None = None
    axis_ticks_x: ElementLine | ElementBlank | None = None
    axis_ticks_y: ElementLine | ElementBlank | None = None
    axis_ticks_length_x: float | None = None
    axis_ticks_length_y: float | None = None

    # Axis line element (ggplot2: axis.line)
    axis_line_element: ElementLine | ElementBlank | None = None

    # Per-axis grid elements (ggplot2: panel.grid.major.x, etc.)
    panel_grid_major_x: ElementLine | ElementBlank | None = None
    panel_grid_major_y: ElementLine | ElementBlank | None = None
    panel_grid_minor_x: ElementLine | ElementBlank | None = None
    panel_grid_minor_y: ElementLine | ElementBlank | None = None

    # Panel spacing for facets (ggplot2: panel.spacing)
    panel_spacing: float = 0.08
    panel_spacing_x: float | None = None
    panel_spacing_y: float | None = None

    # Strip per-axis (ggplot2: strip.text.x, strip.text.y, etc.)
    strip_text_x: ElementText | ElementBlank | None = None
    strip_text_y: ElementText | ElementBlank | None = None
    strip_background_x: str | None = None
    strip_background_y: str | None = None
    strip_placement: str = "outside"

    # Legend key (ggplot2: legend.key, legend.key.size, etc.)
    legend_key: ElementRect | ElementBlank | None = None
    legend_key_size: float = 20.0
    legend_key_width: float | None = None
    legend_key_height: float | None = None
    legend_spacing: float = 4.0
    legend_margin: float = 8.0

    # Plot-level (ggplot2: plot.background, plot.margin)
    plot_background: ElementRect | ElementBlank | None = None
    plot_margin: tuple[float, float, float, float] | None = None

    # Aspect ratio (ggplot2: aspect.ratio)
    aspect_ratio: float | None = None

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

    Parameters
    ----------
    **kwargs
        Any valid :class:`Theme` field. Common fields include
        ``title_size``, ``label_size``, ``font_family``,
        ``background``, ``panel_background``, ``legend_position``,
        ``axis_text_x_rotation``, and ``panel_spacing``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, theme
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + theme(title_size=20)
    Plot(...)
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
