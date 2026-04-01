"""Theme → Vega-Lite config translation."""

from __future__ import annotations

from typing import Any


def translate_theme(theme: Any) -> dict[str, Any]:
    """Convert a plotten Theme to a VL config dict."""
    config: dict[str, Any] = {}

    config["background"] = theme.background
    config["font"] = theme.font_family

    # Axis config — shared, then per-axis overrides
    axis: dict[str, Any] = {}
    axis["grid"] = theme.grid_major_x or theme.grid_major_y
    axis["gridColor"] = theme.grid_color
    axis["gridWidth"] = theme.grid_line_width
    axis["tickSize"] = theme.tick_length
    axis["labelFontSize"] = theme.tick_size
    axis["titleFontSize"] = theme.label_size
    config["axis"] = axis

    # Per-axis config (axisX, axisY)
    axis_x: dict[str, Any] = {}
    axis_y: dict[str, Any] = {}

    if theme.axis_text_x_size is not None:
        axis_x["labelFontSize"] = theme.axis_text_x_size
    if theme.axis_text_y_size is not None:
        axis_y["labelFontSize"] = theme.axis_text_y_size
    if theme.axis_text_x_rotation:
        axis_x["labelAngle"] = theme.axis_text_x_rotation
    if theme.axis_text_y_rotation:
        axis_y["labelAngle"] = theme.axis_text_y_rotation
    if theme.axis_title_x_size is not None:
        axis_x["titleFontSize"] = theme.axis_title_x_size
    if theme.axis_title_y_size is not None:
        axis_y["titleFontSize"] = theme.axis_title_y_size

    # Per-axis grid control
    if not theme.grid_major_x and not theme.grid_minor_x:
        axis_x["grid"] = False
    if not theme.grid_major_y and not theme.grid_minor_y:
        axis_y["grid"] = False

    # Axis line visibility
    if not theme.axis_line_x:
        axis_x["domain"] = False
    if not theme.axis_line_y:
        axis_y["domain"] = False

    # Per-axis tick lengths
    if theme.axis_ticks_length_x is not None:
        axis_x["tickSize"] = theme.axis_ticks_length_x
    if theme.axis_ticks_length_y is not None:
        axis_y["tickSize"] = theme.axis_ticks_length_y

    if axis_x:
        config["axisX"] = axis_x
    if axis_y:
        config["axisY"] = axis_y

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
    from plotten.themes._elements import resolve_background

    panel_fill, _, _ = resolve_background(theme.panel_background)
    view: dict[str, Any] = {"fill": panel_fill or "none"}
    config["view"] = view

    # Panel border via view stroke
    if theme.panel_border_color is not None:
        view["stroke"] = theme.panel_border_color
        view["strokeWidth"] = theme.panel_border_width

    # Legend config
    legend_config: dict[str, Any] = {}
    pos = theme.legend_position
    if pos == "none":
        legend_config["disable"] = True
    elif isinstance(pos, str) and pos in ("top", "bottom", "left", "right"):
        legend_config["orient"] = pos
    leg_fill, _, _ = resolve_background(theme.legend_background)
    if leg_fill is not None:
        legend_config["fillColor"] = leg_fill
    if theme.legend_title_size is not None:
        legend_config["titleFontSize"] = theme.legend_title_size
    if theme.legend_text_size is not None:
        legend_config["labelFontSize"] = theme.legend_text_size
    # Legend key size
    if theme.legend_key_size != 20.0:
        legend_config["symbolSize"] = theme.legend_key_size
    if theme.legend_spacing != 4.0:
        legend_config["rowPadding"] = theme.legend_spacing
    if legend_config:
        config["legend"] = legend_config

    # Facet header (strip) config
    header: dict[str, Any] = {}
    if theme.strip_text_size is not None:
        header["labelFontSize"] = theme.strip_text_size
    if theme.strip_text_color != "#000000":
        header["labelColor"] = theme.strip_text_color
    if header:
        config["header"] = header

    # Element overrides
    _apply_element_overrides(config, theme)

    return config


def _apply_element_overrides(config: dict[str, Any], theme: Any) -> None:
    """Apply ElementText/ElementBlank/ElementLine overrides to config."""
    from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, ElementText

    # Panel grid — global
    if isinstance(theme.panel_grid_major, ElementBlank):
        config["axis"]["grid"] = False
    elif isinstance(theme.panel_grid_major, ElementLine):
        if theme.panel_grid_major.color is not None:
            config["axis"]["gridColor"] = theme.panel_grid_major.color
        if theme.panel_grid_major.size is not None:
            config["axis"]["gridWidth"] = theme.panel_grid_major.size

    # Per-axis grid elements
    if isinstance(theme.panel_grid_major_x, ElementBlank):
        config.setdefault("axisX", {})["grid"] = False
    elif isinstance(theme.panel_grid_major_x, ElementLine):
        ax_x = config.setdefault("axisX", {})
        if theme.panel_grid_major_x.color is not None:
            ax_x["gridColor"] = theme.panel_grid_major_x.color
        if theme.panel_grid_major_x.size is not None:
            ax_x["gridWidth"] = theme.panel_grid_major_x.size

    if isinstance(theme.panel_grid_major_y, ElementBlank):
        config.setdefault("axisY", {})["grid"] = False
    elif isinstance(theme.panel_grid_major_y, ElementLine):
        ax_y = config.setdefault("axisY", {})
        if theme.panel_grid_major_y.color is not None:
            ax_y["gridColor"] = theme.panel_grid_major_y.color
        if theme.panel_grid_major_y.size is not None:
            ax_y["gridWidth"] = theme.panel_grid_major_y.size

    # Axis title — global
    if isinstance(theme.axis_title, ElementBlank):
        config["axis"]["titleFontSize"] = 0
    elif isinstance(theme.axis_title, ElementText):
        _apply_text_element(config.setdefault("axis", {}), theme.axis_title, "title")

    # Per-axis title elements
    if isinstance(theme.axis_title_x, ElementBlank):
        config.setdefault("axisX", {})["titleFontSize"] = 0
    elif isinstance(theme.axis_title_x, ElementText):
        _apply_text_element(config.setdefault("axisX", {}), theme.axis_title_x, "title")
    if isinstance(theme.axis_title_y, ElementBlank):
        config.setdefault("axisY", {})["titleFontSize"] = 0
    elif isinstance(theme.axis_title_y, ElementText):
        _apply_text_element(config.setdefault("axisY", {}), theme.axis_title_y, "title")

    # Axis text — global
    if isinstance(theme.axis_text, ElementBlank):
        config["axis"]["labelFontSize"] = 0
    elif isinstance(theme.axis_text, ElementText):
        _apply_text_element(config.setdefault("axis", {}), theme.axis_text, "label")

    # Per-axis text elements
    if isinstance(theme.axis_text_x, ElementBlank):
        config.setdefault("axisX", {})["labelFontSize"] = 0
    elif isinstance(theme.axis_text_x, ElementText):
        _apply_text_element(config.setdefault("axisX", {}), theme.axis_text_x, "label")
    if isinstance(theme.axis_text_y, ElementBlank):
        config.setdefault("axisY", {})["labelFontSize"] = 0
    elif isinstance(theme.axis_text_y, ElementText):
        _apply_text_element(config.setdefault("axisY", {}), theme.axis_text_y, "label")

    # Axis ticks — global
    if isinstance(theme.axis_ticks, ElementBlank):
        config["axis"]["tickSize"] = 0
    elif isinstance(theme.axis_ticks, ElementLine):
        if theme.axis_ticks.color is not None:
            config["axis"]["tickColor"] = theme.axis_ticks.color
        if theme.axis_ticks.size is not None:
            config["axis"]["tickWidth"] = theme.axis_ticks.size

    # Per-axis ticks
    if isinstance(theme.axis_ticks_x, ElementBlank):
        config.setdefault("axisX", {})["tickSize"] = 0
    elif isinstance(theme.axis_ticks_x, ElementLine):
        ax_x = config.setdefault("axisX", {})
        if theme.axis_ticks_x.color is not None:
            ax_x["tickColor"] = theme.axis_ticks_x.color
        if theme.axis_ticks_x.size is not None:
            ax_x["tickWidth"] = theme.axis_ticks_x.size
    if isinstance(theme.axis_ticks_y, ElementBlank):
        config.setdefault("axisY", {})["tickSize"] = 0
    elif isinstance(theme.axis_ticks_y, ElementLine):
        ax_y = config.setdefault("axisY", {})
        if theme.axis_ticks_y.color is not None:
            ax_y["tickColor"] = theme.axis_ticks_y.color
        if theme.axis_ticks_y.size is not None:
            ax_y["tickWidth"] = theme.axis_ticks_y.size

    # Axis line element — global
    if isinstance(theme.axis_line_element, ElementBlank):
        config["axis"]["domain"] = False
    elif isinstance(theme.axis_line_element, ElementLine):
        if theme.axis_line_element.color is not None:
            config["axis"]["domainColor"] = theme.axis_line_element.color
        if theme.axis_line_element.size is not None:
            config["axis"]["domainWidth"] = theme.axis_line_element.size

    # Plot title
    if isinstance(theme.plot_title, ElementBlank):
        config["title"]["fontSize"] = 0
    elif isinstance(theme.plot_title, ElementText):
        tc = config.setdefault("title", {})
        if theme.plot_title.size is not None:
            tc["fontSize"] = theme.plot_title.size
        if theme.plot_title.color is not None:
            tc["color"] = theme.plot_title.color
        if theme.plot_title.family is not None:
            tc["font"] = theme.plot_title.family
        if theme.plot_title.weight is not None:
            tc["fontWeight"] = theme.plot_title.weight

    # Plot subtitle
    if isinstance(theme.plot_subtitle, ElementText):
        tc = config.setdefault("title", {})
        if theme.plot_subtitle.size is not None:
            tc["subtitleFontSize"] = theme.plot_subtitle.size
        if theme.plot_subtitle.color is not None:
            tc["subtitleColor"] = theme.plot_subtitle.color

    # Panel border element
    if isinstance(theme.panel_border, ElementBlank):
        config.setdefault("view", {})["stroke"] = None
    elif isinstance(theme.panel_border, ElementRect):
        vw = config.setdefault("view", {})
        if theme.panel_border.color is not None:
            vw["stroke"] = theme.panel_border.color
        if theme.panel_border.size is not None:
            vw["strokeWidth"] = theme.panel_border.size

    # Strip text element
    if isinstance(theme.strip_text, ElementBlank):
        config.setdefault("header", {})["labelFontSize"] = 0
    elif isinstance(theme.strip_text, ElementText):
        hdr = config.setdefault("header", {})
        if theme.strip_text.size is not None:
            hdr["labelFontSize"] = theme.strip_text.size
        if theme.strip_text.color is not None:
            hdr["labelColor"] = theme.strip_text.color
        if theme.strip_text.family is not None:
            hdr["labelFont"] = theme.strip_text.family

    # Legend title element
    if isinstance(theme.legend_title_element, ElementBlank):
        config.setdefault("legend", {})["titleFontSize"] = 0
    elif isinstance(theme.legend_title_element, ElementText):
        lg = config.setdefault("legend", {})
        if theme.legend_title_element.size is not None:
            lg["titleFontSize"] = theme.legend_title_element.size
        if theme.legend_title_element.color is not None:
            lg["titleColor"] = theme.legend_title_element.color

    # Legend text element
    if isinstance(theme.legend_text_element, ElementBlank):
        config.setdefault("legend", {})["labelFontSize"] = 0
    elif isinstance(theme.legend_text_element, ElementText):
        lg = config.setdefault("legend", {})
        if theme.legend_text_element.size is not None:
            lg["labelFontSize"] = theme.legend_text_element.size
        if theme.legend_text_element.color is not None:
            lg["labelColor"] = theme.legend_text_element.color

    # Legend key element
    if isinstance(theme.legend_key, ElementRect):
        lg = config.setdefault("legend", {})
        if theme.legend_key.fill is not None:
            lg["symbolFillColor"] = theme.legend_key.fill
        if theme.legend_key.color is not None:
            lg["symbolStrokeColor"] = theme.legend_key.color

    # Plot background element
    if isinstance(theme.plot_background, ElementRect) and theme.plot_background.fill is not None:
        config["background"] = theme.plot_background.fill

    # Aspect ratio
    if theme.aspect_ratio is not None:
        vw = config.setdefault("view", {})
        vw["continuousHeight"] = 300
        vw["continuousWidth"] = int(300 / theme.aspect_ratio)


def _apply_text_element(target: dict[str, Any], element: Any, prefix: str) -> None:
    """Apply ElementText properties to a config section."""
    if element.size is not None:
        target[f"{prefix}FontSize"] = element.size
    if element.color is not None:
        target[f"{prefix}Color"] = element.color
    if element.family is not None:
        target[f"{prefix}Font"] = element.family
    if element.weight is not None:
        target[f"{prefix}FontWeight"] = element.weight
    if element.rotation is not None:
        target[f"{prefix}Angle"] = element.rotation
