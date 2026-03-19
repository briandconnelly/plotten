"""Geom → Vega-Lite mark translation."""

from __future__ import annotations

from typing import Any

from plotten._validation import PlottenError
from plotten._vegalite._unsupported import check_geom


def translate_mark(geom: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Convert a plotten geom to a VL mark spec dict."""
    check_geom(geom)
    name = type(geom).__name__
    mark = _dispatch_mark(geom, name)
    _apply_params(mark, params, geom)
    return mark


def _dispatch_mark(geom: Any, name: str) -> dict[str, Any]:
    """Dispatch to the right VL mark type."""
    dispatch: dict[str, dict[str, Any]] = {
        "GeomPoint": {"type": "point"},
        "GeomLine": {"type": "line"},
        "GeomBar": {"type": "bar"},
        "GeomCol": {"type": "bar"},
        "GeomArea": {"type": "area"},
        "GeomText": {"type": "text"},
        "GeomLabel": {"type": "text"},
        "GeomRect": {"type": "rect"},
        "GeomTile": {"type": "rect"},
        "GeomBoxplot": {"type": "boxplot"},
        "GeomStep": {"type": "line", "interpolate": "step-after"},
        "GeomPath": {"type": "line"},
        "GeomRibbon": {"type": "area"},
        "GeomSegment": {"type": "rule"},
        "GeomErrorbar": {"type": "rule"},
    }
    if name in dispatch:
        return dict(dispatch[name])

    # Composite / special geoms
    if name == "GeomHLine":
        return _hline_mark(geom)
    if name == "GeomVLine":
        return _vline_mark(geom)
    if name == "GeomHistogram":
        return {"type": "bar"}
    if name == "GeomDensity":
        return {"type": "area"}
    if name == "GeomFreqpoly":
        return {"type": "line"}
    if name == "GeomSmooth":
        return {"type": "line"}

    msg = (
        f"{name} is not supported by Vega-Lite export. "
        "Use render() or ggsave() for the matplotlib backend instead."
    )
    raise PlottenError(msg)


def _hline_mark(geom: Any) -> dict[str, Any]:
    return {"type": "rule"}


def _vline_mark(geom: Any) -> dict[str, Any]:
    return {"type": "rule"}


def _apply_params(mark: dict[str, Any], params: dict[str, Any], geom: Any) -> None:
    """Apply geom params as VL mark properties."""
    _PARAM_MAP = {
        "alpha": "opacity",
        "color": "color",
        "fill": "fill",
        "size": "size",
    }
    for p_key, vl_key in _PARAM_MAP.items():
        if p_key in params:
            mark[vl_key] = params[p_key]
    # Pull style kwargs from refline geoms
    if hasattr(geom, "_style"):
        for p_key, vl_key in _PARAM_MAP.items():
            if p_key in geom._style and vl_key not in mark:
                mark[vl_key] = geom._style[p_key]
