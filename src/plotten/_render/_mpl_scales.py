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

    if not polar:
        set_label = ax.set_xlabel if axis == "x" else ax.set_ylabel
        set_label(axis)
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
        sec_ax.tick_params(
            labelsize=theme.tick_size,
            length=theme.tick_length,
        )
        tick_labels = sec_ax.get_yticklabels() if axis == "y" else sec_ax.get_xticklabels()
        for label in tick_labels:
            label.set_fontfamily(theme.font_family)
        if axis == "y" and sec.name is not None:
            sec_ax.yaxis.label.set_fontfamily(theme.font_family)
            sec_ax.yaxis.label.set_fontsize(theme.axis_title_y_size or theme.label_size)
        elif axis == "x" and sec.name is not None:
            sec_ax.xaxis.label.set_fontfamily(theme.font_family)
            sec_ax.xaxis.label.set_fontsize(theme.axis_title_x_size or theme.label_size)


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
