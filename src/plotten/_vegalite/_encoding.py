"""Aes → Vega-Lite encoding channel translation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._computed import AfterScale, AfterStat
from plotten._interaction import Interaction
from plotten._validation import PlottenError

if TYPE_CHECKING:
    from plotten._aes import Aes

# Map plotten aesthetic names to VL encoding channel names.
_AES_TO_CHANNEL: dict[str, str] = {
    "x": "x",
    "y": "y",
    "color": "color",
    "fill": "color",
    "size": "size",
    "alpha": "opacity",
    "shape": "shape",
    "label": "text",
    "linetype": "strokeDash",
    "group": "detail",
    "ymin": "y",
    "ymax": "y2",
    "xmin": "x",
    "xmax": "x2",
    "xend": "x2",
    "yend": "y2",
}


def _infer_vl_type(aes_name: str, scales: tuple[Any, ...]) -> str | None:
    """Infer VL data type from scale information, or return None."""
    from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
    from plotten.scales._date import ScaleDateContinuous
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete

    for scale in scales:
        if scale.aesthetic != aes_name:
            continue
        if isinstance(scale, ScaleDateContinuous):
            return "temporal"
        if isinstance(scale, (ScaleContinuous, ScaleColorContinuous)):
            return "quantitative"
        if isinstance(scale, (ScaleDiscrete, ScaleColorDiscrete)):
            return "nominal"
    return None


def translate_aes(
    mapping: Aes,
    scales: tuple[Any, ...],
    *,
    is_text_mark: bool = False,
    has_both_color_fill: bool = False,
) -> dict[str, Any]:
    """Convert an Aes to a VL encoding dict."""
    encoding: dict[str, Any] = {}
    for aes_name, value in _iter_aes(mapping):
        if value is None:
            continue
        if isinstance(value, (AfterStat, AfterScale)):
            msg = (
                f"AfterStat/AfterScale mapping on '{aes_name}' cannot be directly "
                "exported to Vega-Lite. Use a stat with a native VL equivalent or "
                "the matplotlib backend."
            )
            raise PlottenError(msg)
        if isinstance(value, Interaction):
            # Use first column as detail
            if value.columns:
                channel = "detail"
                enc: dict[str, Any] = {"field": value.columns[0]}
                encoding[channel] = enc
            continue

        channel = _resolve_channel(aes_name, is_text_mark, has_both_color_fill)
        if channel is None:
            continue

        enc = {"field": str(value)}
        vl_type = _infer_vl_type(aes_name, scales)
        if vl_type is not None:
            enc["type"] = vl_type
        encoding[channel] = enc
    return encoding


def _resolve_channel(aes_name: str, is_text_mark: bool, has_both_color_fill: bool) -> str | None:
    """Resolve the VL channel for a given aesthetic name."""
    if aes_name == "label" and not is_text_mark:
        return None
    if aes_name == "color" and has_both_color_fill:
        return "stroke"
    if aes_name == "fill" and has_both_color_fill:
        return "fill"
    return _AES_TO_CHANNEL.get(aes_name)


def _iter_aes(mapping: Aes) -> list[tuple[str, Any]]:
    """Iterate over non-None Aes fields."""
    fields = [
        "x",
        "y",
        "color",
        "fill",
        "size",
        "alpha",
        "linetype",
        "shape",
        "label",
        "ymin",
        "ymax",
        "group",
        "xend",
        "yend",
        "xmin",
        "xmax",
        "z",
        "angle",
        "radius",
    ]
    return [(f, getattr(mapping, f, None)) for f in fields]
