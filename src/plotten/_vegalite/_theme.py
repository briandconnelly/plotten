"""Theme → Vega-Lite config translation."""

from __future__ import annotations

from typing import Any


def translate_theme(theme: Any) -> dict[str, Any]:
    """Convert a plotten Theme to a VL config dict."""
    config: dict[str, Any] = {}

    config["background"] = theme.background
    config["font"] = theme.font_family

    # Axis config
    axis: dict[str, Any] = {}
    axis["grid"] = theme.grid_major_x or theme.grid_major_y
    axis["gridColor"] = theme.grid_color
    axis["gridWidth"] = theme.grid_line_width
    axis["tickSize"] = theme.tick_length
    axis["labelFontSize"] = theme.tick_size
    axis["titleFontSize"] = theme.label_size
    config["axis"] = axis

    # Title config
    title_config: dict[str, Any] = {}
    title_config["fontSize"] = theme.title_size
    title_config["color"] = theme.title_color
    if theme.subtitle_size is not None:
        title_config["subtitleFontSize"] = theme.subtitle_size
    if theme.subtitle_color:
        title_config["subtitleColor"] = theme.subtitle_color
    config["title"] = title_config

    # View config
    view: dict[str, Any] = {"fill": theme.panel_background}
    config["view"] = view

    # Legend config
    legend_config: dict[str, Any] = {}
    pos = theme.legend_position
    if pos == "none":
        legend_config["disable"] = True
    elif isinstance(pos, str) and pos in ("top", "bottom", "left", "right"):
        legend_config["orient"] = pos
    if theme.legend_background is not None:
        legend_config["fillColor"] = theme.legend_background
    if theme.legend_title_size is not None:
        legend_config["titleFontSize"] = theme.legend_title_size
    if theme.legend_text_size is not None:
        legend_config["labelFontSize"] = theme.legend_text_size
    if legend_config:
        config["legend"] = legend_config

    # Element overrides
    _apply_element_overrides(config, theme)

    return config


def _apply_element_overrides(config: dict[str, Any], theme: Any) -> None:
    """Apply ElementText/ElementBlank overrides to config."""
    from plotten.themes._elements import ElementBlank, ElementText

    # Panel grid
    if isinstance(theme.panel_grid_major, ElementBlank):
        config["axis"]["grid"] = False
    elif hasattr(theme, "panel_grid_major") and isinstance(theme.panel_grid_major, type(None)):
        pass

    # Axis title
    if isinstance(theme.axis_title, ElementBlank):
        config["axis"]["titleFontSize"] = 0
    elif isinstance(theme.axis_title, ElementText):
        _apply_text_element(config.setdefault("axis", {}), theme.axis_title, "title")

    # Axis text
    if isinstance(theme.axis_text, ElementBlank):
        config["axis"]["labelFontSize"] = 0
    elif isinstance(theme.axis_text, ElementText):
        _apply_text_element(config.setdefault("axis", {}), theme.axis_text, "label")

    # Plot title
    if isinstance(theme.plot_title, ElementBlank):
        config["title"]["fontSize"] = 0
    elif isinstance(theme.plot_title, ElementText):
        tc = config.setdefault("title", {})
        if theme.plot_title.size is not None:
            tc["fontSize"] = theme.plot_title.size
        if theme.plot_title.color is not None:
            tc["color"] = theme.plot_title.color


def _apply_text_element(target: dict[str, Any], element: Any, prefix: str) -> None:
    """Apply ElementText properties to a config section."""
    if element.size is not None:
        target[f"{prefix}FontSize"] = element.size
    if element.color is not None:
        target[f"{prefix}Color"] = element.color
    if element.family is not None:
        target[f"{prefix}Font"] = element.family
