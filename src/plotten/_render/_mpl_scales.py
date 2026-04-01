"""Scale application: limits, breaks, labels, secondary axes, and date formatting."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _apply_axis_scale(ax: Axes, scale: Any, axis: str, *, polar: bool, theme: Any = None) -> None:
    """Apply a single axis scale (limits, breaks, labels, secondary axis)."""
    from plotten.scales._date import ScaleDateContinuous
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete
    from plotten.scales._reverse import ScaleReverse
    from plotten.scales._sqrt import ScaleSqrt

    set_scale = ax.set_xscale if axis == "x" else ax.set_yscale
    set_lim = ax.set_xlim if axis == "x" else ax.set_ylim
    set_ticks = ax.set_xticks if axis == "x" else ax.set_yticks
    set_ticklabels = ax.set_xticklabels if axis == "x" else ax.set_yticklabels

    match scale:
        case ScaleLog():
            set_scale("log", base=scale._base)
        case ScaleSqrt():
            import numpy as _np

            set_scale("function", functions=(_np.sqrt, _np.square))
            _apply_continuous_scale(ax, scale, axis=axis)
        case _ if isinstance(scale, ScaleDateContinuous):
            _apply_date_scale(ax, scale, axis=axis)
        case ScaleReverse():
            _apply_continuous_scale(ax, scale, axis=axis)
        case ScaleDiscrete():
            set_lim(scale.get_limits())
            set_ticks(scale.get_breaks())
            set_ticklabels(scale.get_labels())
        case ScaleContinuous() if scale._breaks is not None or callable(scale._labels):
            _apply_continuous_scale(ax, scale, axis=axis)
        case _:
            set_lim(scale.get_limits())

    _apply_sec_axis(ax, scale, axis=axis, theme=theme)


def apply_scales(ax: Axes, scales: dict, *, polar: bool = False, theme: Any = None) -> None:
    """Apply scale limits, breaks, and labels to axes."""
    if "x" in scales and not polar:
        _apply_axis_scale(ax, scales["x"], "x", polar=polar, theme=theme)
    if "y" in scales:
        _apply_axis_scale(ax, scales["y"], "y", polar=polar, theme=theme)


def _apply_sec_axis(
    ax: Axes,
    scale: Any,
    axis: str,
    *,
    theme: Any = None,
) -> None:
    """Apply a secondary axis if the scale has one configured."""
    sec = getattr(scale, "_sec_axis", None)
    if sec is None:
        return
    if axis == "y":
        sec_ax = ax.secondary_yaxis("right", functions=(sec.trans, sec.inverse))
    else:
        sec_ax = ax.secondary_xaxis("top", functions=(sec.trans, sec.inverse))
    if sec.name is not None:
        sec_ax.set_label(sec.name) if axis == "x" else sec_ax.set_ylabel(sec.name)
    if sec.breaks is not None:
        if axis == "y":
            sec_ax.set_yticks(sec.breaks)
        else:
            sec_ax.set_xticks(sec.breaks)
    if sec.labels is not None:
        if axis == "y":
            sec_ax.set_yticklabels(sec.labels)
        else:
            sec_ax.set_xticklabels(sec.labels)

    # Apply theme styling to secondary axis
    if theme is not None:
        _style_sec_axis(sec_ax, axis=axis, theme=theme, name=sec.name)


def _style_sec_axis(sec_ax: Any, *, axis: str, theme: Any, name: str | None) -> None:
    """Apply per-position theme fields to a secondary axis."""
    from plotten.themes._elements import ElementBlank, ElementLine, ElementText

    # Determine which per-position fields apply
    if axis == "y":
        text_el = theme.axis_text_y_right
        title_el = theme.axis_title_y_right
        ticks_el = theme.axis_ticks_y_right
        ticks_len = theme.axis_ticks_length_y_right
        line_el = theme.axis_line_y_right
        # Cascade: per-position → per-axis → global
        text_parent = theme.axis_text_y
        title_parent = theme.axis_title_y
        ticks_parent = theme.axis_ticks_y
        ticks_len_parent = theme.axis_ticks_length_y
    else:
        text_el = theme.axis_text_x_top
        title_el = theme.axis_title_x_top
        ticks_el = theme.axis_ticks_x_top
        ticks_len = theme.axis_ticks_length_x_top
        line_el = theme.axis_line_x_top
        text_parent = theme.axis_text_x
        title_parent = theme.axis_title_x
        ticks_parent = theme.axis_ticks_x
        ticks_len_parent = theme.axis_ticks_length_x

    # --- Tick label styling ---
    effective_text = text_el or text_parent
    tick_size = theme.tick_size
    tick_color = "#000000"
    tick_rotation = 0.0
    tick_family = theme.font_family

    if isinstance(effective_text, ElementBlank):
        tick_size = 0
    elif isinstance(effective_text, ElementText):
        if effective_text.size is not None:
            tick_size = effective_text.size
        if effective_text.color is not None:
            tick_color = effective_text.color
        if effective_text.rotation is not None:
            tick_rotation = effective_text.rotation
        if effective_text.family is not None:
            tick_family = effective_text.family

    # --- Tick mark styling ---
    effective_ticks = ticks_el or ticks_parent or theme.axis_ticks
    show_ticks = not isinstance(effective_ticks, ElementBlank)
    tick_mark_color = tick_color
    tick_mark_width = theme.axis_line_width
    effective_length = ticks_len or ticks_len_parent or theme.tick_length
    if isinstance(effective_ticks, ElementLine):
        if effective_ticks.color is not None:
            tick_mark_color = effective_ticks.color
        if effective_ticks.size is not None:
            tick_mark_width = effective_ticks.size

    sec_ax.tick_params(
        labelsize=tick_size,
        labelcolor=tick_color,
        labelrotation=tick_rotation,
        length=effective_length if show_ticks else 0,
        width=tick_mark_width,
        color=tick_mark_color,
    )
    tick_labels = sec_ax.get_yticklabels() if axis == "y" else sec_ax.get_xticklabels()
    for label in tick_labels:
        label.set_fontfamily(tick_family)

    # --- Axis line (spine) styling ---
    effective_line = line_el
    if axis == "y":
        spine_name = "right"
    else:
        spine_name = "top"
    if isinstance(effective_line, ElementBlank):
        sec_ax.spines[spine_name].set_visible(False)
    elif isinstance(effective_line, ElementLine):
        sec_ax.spines[spine_name].set_visible(True)
        if effective_line.color is not None:
            sec_ax.spines[spine_name].set_edgecolor(effective_line.color)
        if effective_line.size is not None:
            sec_ax.spines[spine_name].set_linewidth(effective_line.size)

    # --- Title styling ---
    if name is not None:
        effective_title = title_el or title_parent or theme.axis_title
        title_size = theme.label_size
        title_family = theme.font_family
        if axis == "y":
            title_size = theme.axis_title_y_size or title_size
        else:
            title_size = theme.axis_title_x_size or title_size

        if isinstance(effective_title, ElementBlank):
            if axis == "y":
                sec_ax.set_ylabel("")
            else:
                sec_ax.set_xlabel("")
        elif isinstance(effective_title, ElementText):
            if effective_title.size is not None:
                title_size = effective_title.size
            if effective_title.family is not None:
                title_family = effective_title.family
            label_obj = sec_ax.yaxis.label if axis == "y" else sec_ax.xaxis.label
            label_obj.set_fontfamily(title_family)
            label_obj.set_fontsize(title_size)
            if effective_title.color is not None:
                label_obj.set_color(effective_title.color)
            if effective_title.weight is not None:
                label_obj.set_fontweight(effective_title.weight)
            if effective_title.style is not None:
                label_obj.set_fontstyle(effective_title.style)
        else:
            label_obj = sec_ax.yaxis.label if axis == "y" else sec_ax.xaxis.label
            label_obj.set_fontfamily(title_family)
            label_obj.set_fontsize(title_size)


def _apply_continuous_scale(ax: Axes, scale: Any, axis: str) -> None:
    """Apply limits, breaks, and labels for a continuous scale."""
    limits = scale.get_limits()
    if axis == "x":
        ax.set_xlim(limits)
        ax.set_xticks(scale.get_breaks())
        ax.set_xticklabels(scale.get_labels())
    else:
        ax.set_ylim(limits)
        ax.set_yticks(scale.get_breaks())
        ax.set_yticklabels(scale.get_labels())


def _apply_date_scale(ax: Axes, scale: Any, axis: str) -> None:
    import matplotlib.dates as mdates

    locator = mdates.AutoDateLocator()
    formatter = mdates.AutoDateFormatter(locator)

    match axis:
        case "x":
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            ax.set_xlim(scale.get_limits())
            ax.figure.autofmt_xdate()
        case "y":
            ax.yaxis.set_major_locator(locator)
            ax.yaxis.set_major_formatter(formatter)
            ax.set_ylim(scale.get_limits())
