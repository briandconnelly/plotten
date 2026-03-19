"""Scale application: limits, breaks, labels, secondary axes, and date formatting."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def apply_scales(ax: Axes, scales: dict, *, polar: bool = False) -> None:
    """Apply scale limits, breaks, and labels to axes."""
    from plotten.scales._date import ScaleDateContinuous
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete
    from plotten.scales._reverse import ScaleReverse
    from plotten.scales._sqrt import ScaleSqrt

    if "x" in scales and not polar:
        x_scale = scales["x"]
        match x_scale:
            case ScaleLog():
                ax.set_xscale("log", base=x_scale._base)
            case ScaleSqrt():
                import numpy as _np

                ax.set_xscale("function", functions=(_np.sqrt, _np.square))
                _apply_continuous_scale(ax, x_scale, axis="x")
            case _ if isinstance(x_scale, ScaleDateContinuous):
                _apply_date_scale(ax, x_scale, axis="x")
            case ScaleReverse():
                _apply_continuous_scale(ax, x_scale, axis="x")
            case ScaleDiscrete():
                ax.set_xlim(x_scale.get_limits())
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
            case ScaleContinuous() if x_scale._breaks is not None or callable(x_scale._labels):
                _apply_continuous_scale(ax, x_scale, axis="x")
            case _:
                ax.set_xlim(x_scale.get_limits())
        ax.set_xlabel("x")
        _apply_sec_axis(ax, x_scale, axis="x")

    if "y" in scales:
        y_scale = scales["y"]
        match y_scale:
            case ScaleLog():
                ax.set_yscale("log", base=y_scale._base)
            case ScaleSqrt():
                import numpy as _np

                ax.set_yscale("function", functions=(_np.sqrt, _np.square))
                _apply_continuous_scale(ax, y_scale, axis="y")
            case _ if isinstance(y_scale, ScaleDateContinuous):
                _apply_date_scale(ax, y_scale, axis="y")
            case ScaleReverse():
                _apply_continuous_scale(ax, y_scale, axis="y")
            case ScaleDiscrete():
                ax.set_ylim(y_scale.get_limits())
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
            case ScaleContinuous() if y_scale._breaks is not None or callable(y_scale._labels):
                _apply_continuous_scale(ax, y_scale, axis="y")
            case _:
                ax.set_ylim(y_scale.get_limits())
        if not polar:
            ax.set_ylabel("y")
        _apply_sec_axis(ax, y_scale, axis="y")


def _apply_sec_axis(ax: Axes, scale: Any, axis: str) -> None:
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
