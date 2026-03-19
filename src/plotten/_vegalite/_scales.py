"""Scale → Vega-Lite scale/type/domain/range translation."""

from __future__ import annotations

from typing import Any


def translate_scales(
    scales: tuple[Any, ...],
    encoding: dict[str, Any],
) -> dict[str, Any]:
    """Apply scale info to VL encoding channels. Returns updated encoding."""
    enc = dict(encoding)
    for scale in scales:
        _apply_scale(scale, enc)
    return enc


def _apply_scale(scale: Any, enc: dict[str, Any]) -> None:
    """Apply a single scale to the encoding dict."""
    name = type(scale).__name__
    aes = scale.aesthetic
    channel = _aes_to_channel(aes)
    if channel not in enc:
        # Create minimal encoding if scale references a mapped channel
        return

    ch = dict(enc[channel])

    if name == "ScaleContinuous":
        ch["type"] = "quantitative"
        _apply_limits(ch, scale)
        _apply_breaks(ch, scale)
        _apply_labels(ch, scale)

    elif name == "ScaleDiscrete":
        ch["type"] = "nominal"
        _apply_discrete_labels(ch, scale)

    elif name == "ScaleDateContinuous":
        ch["type"] = "temporal"
        _apply_limits(ch, scale)
        _apply_breaks(ch, scale)

    elif name == "ScaleLog":
        ch.setdefault("scale", {})["type"] = "log"
        if hasattr(scale, "_base") and scale._base != 10:
            ch["scale"]["base"] = scale._base

    elif name == "ScaleSqrt":
        ch.setdefault("scale", {})["type"] = "sqrt"

    elif name == "ScaleReverse":
        ch["sort"] = "descending"

    elif name == "ScaleColorContinuous" or name == "ScaleGreyContinuous":
        ch.setdefault("scale", {})["scheme"] = scale._cmap_name
        _apply_limits(ch, scale)

    elif name == "ScaleColorDiscrete":
        if hasattr(scale, "_manual_values") and scale._manual_values:
            domain = list(scale._manual_values.keys())
            range_ = list(scale._manual_values.values())
            ch.setdefault("scale", {}).update({"domain": domain, "range": range_})

    elif name == "ScaleBrewerDiscrete":
        ch.setdefault("scale", {})["scheme"] = scale._palette_name

    elif name == "ScaleBrewerContinuous":
        ch.setdefault("scale", {})["scheme"] = scale._cmap_name
        _apply_limits(ch, scale)

    elif name == "ScaleGradient":
        ch.setdefault("scale", {})["range"] = [scale._low, scale._high]
        _apply_limits(ch, scale)

    elif name == "ScaleGradient2":
        s = ch.setdefault("scale", {})
        s["range"] = [scale._low, scale._mid, scale._high]
        s["domainMid"] = scale._midpoint
        _apply_limits(ch, scale)

    elif name == "ScaleGradientN":
        ch.setdefault("scale", {})["range"] = list(scale._colors)
        _apply_limits(ch, scale)

    elif name in ("ScaleSizeContinuous", "ScaleAlphaContinuous"):
        ch.setdefault("scale", {})["range"] = list(scale._range)
        _apply_limits(ch, scale)

    enc[channel] = ch


def _get_attr(scale: Any, name: str) -> Any:
    """Get attribute, trying both public and private naming."""
    return getattr(scale, f"_{name}", getattr(scale, name, None))


def _apply_limits(ch: dict[str, Any], scale: Any) -> None:
    limits = _get_attr(scale, "limits")
    if limits is not None:
        ch.setdefault("scale", {})["domain"] = list(limits)


def _apply_breaks(ch: dict[str, Any], scale: Any) -> None:
    breaks = _get_attr(scale, "breaks")
    if breaks is not None and isinstance(breaks, list):
        ch.setdefault("axis", {})["values"] = breaks


def _apply_labels(ch: dict[str, Any], scale: Any) -> None:
    labels = _get_attr(scale, "labels")
    if labels is not None and isinstance(labels, list):
        # Static label list — no easy VL equivalent without labelExpr
        pass


def _apply_discrete_labels(ch: dict[str, Any], scale: Any) -> None:
    labels = _get_attr(scale, "manual_labels")
    if labels is not None and isinstance(labels, dict):
        ch["sort"] = list(labels.keys())


def _aes_to_channel(aes: str) -> str:
    _MAP: dict[str, str] = {
        "x": "x",
        "y": "y",
        "color": "color",
        "fill": "color",
        "size": "size",
        "alpha": "opacity",
        "shape": "shape",
    }
    return _MAP.get(aes, aes)
