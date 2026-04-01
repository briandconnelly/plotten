from __future__ import annotations

import difflib
from dataclasses import MISSING, dataclass, field, fields
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from plotten.themes._elements import (
        ElementBlank,
        ElementLine,
        ElementRect,
        ElementText,
        Margin,
    )


def _default_plot_caption() -> ElementText:
    """Default plot.caption element: rel(0.8) size, matching ggplot2."""
    from plotten.themes._elements import ElementText, Rel

    return ElementText(size=Rel(0.8))


@dataclass(frozen=True, slots=True, kw_only=True)
class Theme:
    """Visual theme controlling the appearance of a plot."""

    # Text — when base_size is set, scalar sizes are derived from it
    # using ggplot2 multipliers (title 1.2x, subtitle 0.9x, label 1.0x,
    # tick 0.8x).  Explicit scalar overrides still win.
    base_size: float | None = None
    title_size: float = 16
    label_size: float = 11
    tick_size: float = 10
    font_family: str = "sans-serif"

    # Colors
    background: str = "#ffffff"
    panel_background: str | ElementRect = "#ffffff"
    grid_color: str = "#e0e0e0"

    # Lines
    axis_line_width: float = 0.5
    grid_line_width: float = 0.3
    tick_length: float = 0.0

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
    strip_background: str | ElementRect = "none"
    strip_text_size: float | None = None
    strip_text_color: str = "#000000"
    strip_text_weight: str = "semibold"

    # Title/subtitle colors and weight
    title_color: str = "#1a1a1a"
    title_weight: str = "bold"
    subtitle_size: float | None = 12
    subtitle_color: str = "#666666"

    # Legend styling
    legend_background: str | ElementRect | None = None
    legend_title_size: float | None = None
    legend_text_size: float | None = None

    # Grid per-axis control (boolean shortcuts)
    grid_major_x: bool = True
    grid_major_y: bool = True
    grid_minor_x: bool = False
    grid_minor_y: bool = False

    # Axis line visibility (boolean shortcuts)
    axis_line_x: bool = False
    axis_line_y: bool = False

    # Element overrides (take precedence over flat fields)
    axis_title: ElementText | ElementBlank | None = None
    axis_text: ElementText | ElementBlank | None = None
    plot_title: ElementText | ElementBlank | None = None
    plot_subtitle: ElementText | ElementBlank | None = None
    plot_caption: ElementText | ElementBlank | None = field(
        default_factory=lambda: _default_plot_caption(),
    )
    panel_grid: ElementLine | ElementBlank | None = None
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
    strip_background_x: str | ElementRect | None = None
    strip_background_y: str | ElementRect | None = None
    strip_placement: str = "outside"

    # Legend key (ggplot2: legend.key, legend.key.size, etc.)
    legend_key: ElementRect | ElementBlank | None = None
    legend_key_size: float = 20.0
    legend_key_width: float | None = None
    legend_key_height: float | None = None
    legend_spacing: float = 4.0
    legend_spacing_x: float | None = None
    legend_spacing_y: float | None = None
    legend_margin: float | Margin | tuple[float, float, float, float] = 8.0

    # Plot-level (ggplot2: plot.background, plot.margin)
    plot_background: ElementRect | ElementBlank | None = None
    plot_margin: Margin | tuple[float, float, float, float] | None = None

    # Aspect ratio (ggplot2: aspect.ratio)
    aspect_ratio: float | None = None

    # --- Per-position axis variants (ggplot2: axis.title.x.top, etc.) ---
    axis_title_x_top: ElementText | ElementBlank | None = None
    axis_title_x_bottom: ElementText | ElementBlank | None = None
    axis_title_y_left: ElementText | ElementBlank | None = None
    axis_title_y_right: ElementText | ElementBlank | None = None
    axis_text_x_top: ElementText | ElementBlank | None = None
    axis_text_x_bottom: ElementText | ElementBlank | None = None
    axis_text_y_left: ElementText | ElementBlank | None = None
    axis_text_y_right: ElementText | ElementBlank | None = None
    axis_ticks_x_top: ElementLine | ElementBlank | None = None
    axis_ticks_x_bottom: ElementLine | ElementBlank | None = None
    axis_ticks_y_left: ElementLine | ElementBlank | None = None
    axis_ticks_y_right: ElementLine | ElementBlank | None = None
    axis_ticks_length: float | None = None
    axis_ticks_length_x_top: float | None = None
    axis_ticks_length_x_bottom: float | None = None
    axis_ticks_length_y_left: float | None = None
    axis_ticks_length_y_right: float | None = None
    axis_line_x_element: ElementLine | ElementBlank | None = None
    axis_line_y_element: ElementLine | ElementBlank | None = None
    axis_line_x_top: ElementLine | ElementBlank | None = None
    axis_line_x_bottom: ElementLine | ElementBlank | None = None
    axis_line_y_left: ElementLine | ElementBlank | None = None
    axis_line_y_right: ElementLine | ElementBlank | None = None

    # --- Polar axis (ggplot2: axis.text.theta, etc.) ---
    axis_text_theta: ElementText | ElementBlank | None = None
    axis_text_r: ElementText | ElementBlank | None = None
    axis_ticks_theta: ElementLine | ElementBlank | None = None
    axis_ticks_r: ElementLine | ElementBlank | None = None
    axis_line_theta: ElementLine | ElementBlank | None = None
    axis_line_r: ElementLine | ElementBlank | None = None
    axis_ticks_length_theta: float | None = None
    axis_ticks_length_r: float | None = None

    # --- Minor ticks (ggplot2: axis.minor.ticks, etc.) ---
    axis_minor_ticks: ElementLine | ElementBlank | None = None
    axis_minor_ticks_x: ElementLine | ElementBlank | None = None
    axis_minor_ticks_y: ElementLine | ElementBlank | None = None
    axis_minor_ticks_x_top: ElementLine | ElementBlank | None = None
    axis_minor_ticks_x_bottom: ElementLine | ElementBlank | None = None
    axis_minor_ticks_y_left: ElementLine | ElementBlank | None = None
    axis_minor_ticks_y_right: ElementLine | ElementBlank | None = None
    axis_minor_ticks_theta: ElementLine | ElementBlank | None = None
    axis_minor_ticks_r: ElementLine | ElementBlank | None = None
    axis_minor_ticks_length: float | None = None
    axis_minor_ticks_length_x: float | None = None
    axis_minor_ticks_length_x_top: float | None = None
    axis_minor_ticks_length_x_bottom: float | None = None
    axis_minor_ticks_length_y: float | None = None
    axis_minor_ticks_length_y_left: float | None = None
    axis_minor_ticks_length_y_right: float | None = None
    axis_minor_ticks_length_theta: float | None = None
    axis_minor_ticks_length_r: float | None = None

    # --- Legend layout (ggplot2: legend.direction, etc.) ---
    legend_direction: str | None = None
    legend_byrow: bool = False
    legend_justification: str | tuple[float, float] | None = None
    legend_justification_top: str | tuple[float, float] | None = None
    legend_justification_bottom: str | tuple[float, float] | None = None
    legend_justification_left: str | tuple[float, float] | None = None
    legend_justification_right: str | tuple[float, float] | None = None
    legend_justification_inside: str | tuple[float, float] | None = None
    legend_position_inside: tuple[float, float] | None = None
    legend_box: str | None = None
    legend_box_just: str | None = None
    legend_box_margin: Margin | tuple[float, float, float, float] | None = None
    legend_box_background: ElementRect | ElementBlank | None = None
    legend_box_spacing: float | None = None
    legend_location: str | None = None
    legend_text_position: str | None = None
    legend_title_position: str | None = None
    legend_frame: ElementRect | ElementBlank | None = None
    legend_ticks: ElementLine | ElementBlank | None = None
    legend_ticks_length: float | None = None
    legend_axis_line: ElementLine | ElementBlank | None = None
    legend_key_justification: str | tuple[float, float] | None = None
    legend_key_spacing: float | None = None
    legend_key_spacing_x: float | None = None
    legend_key_spacing_y: float | None = None

    # --- Plot tags (ggplot2: plot.tag, etc.) ---
    plot_tag: ElementText | ElementBlank | None = None
    plot_tag_position: str | tuple[float, float] | None = None
    plot_tag_location: str | None = None

    # --- Plot title/caption position (ggplot2: plot.title.position, etc.) ---
    # "plot" = align to full plot area (ggplot2 ≥3.5 default);
    # "panel" = align to panel area.
    plot_title_position: str | None = "plot"
    plot_caption_position: str | None = "plot"

    # --- Panel control (ggplot2: panel.ontop, etc.) ---
    panel_ontop: bool = False
    panel_widths: tuple[float, ...] | None = None
    panel_heights: tuple[float, ...] | None = None

    # --- Strip refinements (ggplot2: strip.clip, etc.) ---
    strip_clip: str = "inherit"
    strip_text_x_top: ElementText | ElementBlank | None = None
    strip_text_x_bottom: ElementText | ElementBlank | None = None
    strip_text_y_left: ElementText | ElementBlank | None = None
    strip_text_y_right: ElementText | ElementBlank | None = None
    strip_switch_pad_grid: float | None = None
    strip_switch_pad_wrap: float | None = None

    # --- Base element inheritance (ggplot2: line, rect, text, title) ---
    line: ElementLine | None = None
    rect: ElementRect | None = None
    text: ElementText | None = None
    title: ElementText | None = None
    spacing: float | None = None
    margins: Margin | None = None

    # --- Function control (ggplot2: complete, validate) ---
    complete: bool = False
    validate: bool = True

    def __post_init__(self) -> None:
        if self.base_size is not None:
            bs = self.base_size
            # Derive scalar sizes from base_size when they still equal the
            # class defaults (i.e. the caller didn't explicitly override them).
            defs = _FIELD_DEFAULTS
            if self.title_size == defs["title_size"]:
                object.__setattr__(self, "title_size", bs * 1.2)
            if self.label_size == defs["label_size"]:
                object.__setattr__(self, "label_size", bs)
            if self.tick_size == defs["tick_size"]:
                object.__setattr__(self, "tick_size", bs * 0.8)
            if self.subtitle_size == defs["subtitle_size"]:
                object.__setattr__(self, "subtitle_size", bs * 0.9)

    def __add__(self, other: Theme) -> Self:
        """Layer *other* on top of *self*.

        For each field, if *other*'s value differs from the class default the
        value from *other* is used; otherwise the value from *self* is kept.

        If *other* is a complete theme (``complete=True``), it replaces *self*
        entirely rather than merging.
        """
        if not isinstance(other, Theme):
            return NotImplemented

        if other.complete:
            return other  # type: ignore[return-value]

        kwargs: dict[str, Any] = {}
        for f in fields(self):
            other_val = getattr(other, f.name)
            # Determine the class default for this field
            if f.default is not MISSING:
                default = f.default
            elif f.default_factory is not MISSING:
                default = f.default_factory()
            else:
                # No default — always take other_val
                kwargs[f.name] = other_val
                continue
            if other_val != default:
                kwargs[f.name] = other_val
            else:
                kwargs[f.name] = getattr(self, f.name)
        return type(self)(**kwargs)


# Cache field defaults so __post_init__ can compare without hardcoded literals.
_FIELD_DEFAULTS = {f.name: f.default for f in fields(Theme) if f.default is not MISSING}


def theme(**kwargs: Any) -> Theme:
    """Create a partial theme for incremental overrides.

    Validates that all keyword arguments are valid Theme fields,
    then returns a Theme instance suitable for composition via ``+``.

    Parameters
    ----------
    **kwargs
        Any valid :class:`Theme` field. Common fields include
        ``base_size``, ``title_size``, ``label_size``, ``font_family``,
        ``background``, ``panel_background``, ``legend_position``,
        ``axis_text_x_rotation``, and ``panel_spacing``.

    Raises
    ------
    ConfigError
        If any keyword argument is not a valid Theme field.
        Includes typo suggestions via ``difflib``.

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
        from plotten._validation import ConfigError

        msg = f"Unknown theme properties:\n{hint}\nValid properties: {valid_list}"
        raise ConfigError(msg)
    return Theme(**kwargs)


# Module-level global theme
_global_theme: Theme = Theme()


def theme_set(new_theme: Theme) -> Theme:
    """Set the global default theme.

    Parameters
    ----------
    new_theme : Theme
        The theme to set as the global default.

    Returns
    -------
    Theme
        The previous global default theme, so it can be restored later.
    """
    global _global_theme
    old = _global_theme
    _global_theme = new_theme
    return old


def theme_get() -> Theme:
    """Return the current global default theme."""
    return _global_theme


def theme_update(**kwargs: Any) -> Theme:
    """Update the global default theme with the given overrides.

    Accepts the same keyword arguments as :func:`theme`.

    Parameters
    ----------
    **kwargs
        Theme fields to override (e.g. ``title_size=20``).

    Returns
    -------
    Theme
        The updated global default theme.

    Raises
    ------
    ConfigError
        If any keyword argument is not a valid Theme field.
    """
    global _global_theme
    _global_theme = _global_theme + theme(**kwargs)
    return _global_theme
