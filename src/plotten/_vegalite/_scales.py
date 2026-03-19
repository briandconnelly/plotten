"""Scale → Vega-Lite scale/type/domain/range translation."""

from __future__ import annotations

from typing import Any

from plotten._vegalite._encoding import AES_TO_CHANNEL


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
    from plotten.scales._alpha import ScaleAlphaContinuous
    from plotten.scales._brewer import ScaleBrewerContinuous, ScaleBrewerDiscrete
    from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
    from plotten.scales._date import ScaleDateContinuous
    from plotten.scales._gradient import ScaleGradient, ScaleGradient2, ScaleGradientN
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete
    from plotten.scales._reverse import ScaleReverse
    from plotten.scales._size import ScaleSizeContinuous
    from plotten.scales._sqrt import ScaleSqrt

    channel = _aes_to_channel(scale.aesthetic)
    if channel not in enc:
        return

    ch = dict(enc[channel])

    # Order matters: check subclasses before parent classes.
    if isinstance(scale, ScaleLog):
        ch.setdefault("scale", {})["type"] = "log"
        if scale._base != 10:
            ch["scale"]["base"] = scale._base

    elif isinstance(scale, ScaleSqrt):
        ch.setdefault("scale", {})["type"] = "sqrt"

    elif isinstance(scale, ScaleReverse):
        ch["sort"] = "descending"

    elif isinstance(scale, ScaleDateContinuous):
        ch["type"] = "temporal"
        _apply_limits(ch, scale)
        _apply_breaks(ch, scale)

    elif isinstance(scale, ScaleGradient2):
        s = ch.setdefault("scale", {})
        s["range"] = [scale._low, scale._mid, scale._high]
        s["domainMid"] = scale._midpoint
        _apply_limits(ch, scale)

    elif isinstance(scale, ScaleGradient):
        ch.setdefault("scale", {})["range"] = [scale._low, scale._high]
        _apply_limits(ch, scale)

    elif isinstance(scale, ScaleGradientN):
        ch.setdefault("scale", {})["range"] = list(scale._colors)
        _apply_limits(ch, scale)

    elif isinstance(scale, ScaleBrewerDiscrete):
        ch.setdefault("scale", {})["scheme"] = scale._palette_name

    elif isinstance(scale, ScaleBrewerContinuous):
        ch.setdefault("scale", {})["scheme"] = scale._cmap_name
        _apply_limits(ch, scale)

    elif isinstance(scale, ScaleColorDiscrete):
        if hasattr(scale, "_manual_values") and scale._manual_values:
            domain = list(scale._manual_values.keys())
            range_ = list(scale._manual_values.values())
            ch.setdefault("scale", {}).update({"domain": domain, "range": range_})

    elif isinstance(scale, ScaleColorContinuous):
        ch.setdefault("scale", {})["scheme"] = scale._cmap_name
        _apply_limits(ch, scale)

    elif isinstance(scale, (ScaleSizeContinuous, ScaleAlphaContinuous)):
        ch.setdefault("scale", {})["range"] = list(scale._range)
        _apply_limits(ch, scale)

    elif isinstance(scale, ScaleContinuous):
        ch["type"] = "quantitative"
        _apply_limits(ch, scale)
        _apply_breaks(ch, scale)

    elif isinstance(scale, ScaleDiscrete):
        ch["type"] = "nominal"
        _apply_discrete_labels(ch, scale)

    enc[channel] = ch


def _apply_limits(ch: dict[str, Any], scale: Any) -> None:
    limits = getattr(scale, "_limits", None)
    if limits is not None:
        ch.setdefault("scale", {})["domain"] = list(limits)


def _apply_breaks(ch: dict[str, Any], scale: Any) -> None:
    breaks = getattr(scale, "_breaks", None)
    if breaks is not None and isinstance(breaks, list):
        ch.setdefault("axis", {})["values"] = breaks


def _apply_discrete_labels(ch: dict[str, Any], scale: Any) -> None:
    labels = getattr(scale, "_manual_labels", None)
    if labels is not None and isinstance(labels, dict):
        ch["sort"] = list(labels.keys())


def _aes_to_channel(aes: str) -> str:
    return AES_TO_CHANNEL.get(aes, aes)
