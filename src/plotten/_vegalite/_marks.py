"""Geom → Vega-Lite mark translation."""

from __future__ import annotations

from typing import Any

from plotten._validation import PlottenError
from plotten._vegalite._unsupported import check_geom

_PARAM_MAP: dict[str, str] = {
    "alpha": "opacity",
    "color": "color",
    "fill": "fill",
    "size": "size",
}


def translate_mark(geom: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Convert a plotten geom to a VL mark spec dict."""
    check_geom(geom)
    mark = _dispatch_mark(geom)
    _apply_params(mark, params, geom)
    return mark


def _dispatch_mark(geom: Any) -> dict[str, Any]:
    """Dispatch to the right VL mark type."""
    from plotten.geoms._area import GeomArea
    from plotten.geoms._bar import GeomBar
    from plotten.geoms._boxplot import GeomBoxplot
    from plotten.geoms._col import GeomCol
    from plotten.geoms._density import GeomDensity
    from plotten.geoms._errorbar import GeomErrorbar
    from plotten.geoms._freqpoly import GeomFreqpoly
    from plotten.geoms._histogram import GeomHistogram
    from plotten.geoms._line import GeomLine
    from plotten.geoms._path import GeomPath
    from plotten.geoms._point import GeomPoint
    from plotten.geoms._rect import GeomRect
    from plotten.geoms._refline import GeomHLine, GeomVLine
    from plotten.geoms._ribbon import GeomRibbon
    from plotten.geoms._segment import GeomSegment
    from plotten.geoms._smooth import GeomSmooth
    from plotten.geoms._step import GeomStep
    from plotten.geoms._text import GeomLabel, GeomText
    from plotten.geoms._tile import GeomTile

    # Order matters for isinstance with inheritance — check subclasses first
    _MARK_TABLE: list[tuple[type, dict[str, Any]]] = [
        (GeomStep, {"type": "line", "interpolate": "step-after"}),
        (GeomSmooth, {"type": "line"}),
        (GeomFreqpoly, {"type": "line"}),
        (GeomLine, {"type": "line"}),
        (GeomPath, {"type": "line"}),
        (GeomHistogram, {"type": "bar"}),
        (GeomBar, {"type": "bar"}),
        (GeomCol, {"type": "bar"}),
        (GeomPoint, {"type": "point"}),
        (GeomDensity, {"type": "area"}),
        (GeomArea, {"type": "area"}),
        (GeomRibbon, {"type": "area"}),
        (GeomText, {"type": "text"}),
        (GeomLabel, {"type": "text"}),
        (GeomTile, {"type": "rect"}),
        (GeomRect, {"type": "rect"}),
        (GeomBoxplot, {"type": "boxplot"}),
        (GeomHLine, {"type": "rule"}),
        (GeomVLine, {"type": "rule"}),
        (GeomSegment, {"type": "rule"}),
        (GeomErrorbar, {"type": "rule"}),
    ]

    for cls, mark in _MARK_TABLE:
        if isinstance(geom, cls):
            return dict(mark)

    msg = (
        f"{type(geom).__name__} is not supported by Vega-Lite export. "
        "Use render() or ggsave() for the matplotlib backend instead."
    )
    raise PlottenError(msg)


def _apply_params(mark: dict[str, Any], params: dict[str, Any], geom: Any) -> None:
    """Apply geom params as VL mark properties."""
    for p_key, vl_key in _PARAM_MAP.items():
        if p_key in params:
            mark[vl_key] = params[p_key]
    # Pull style kwargs from refline geoms
    if hasattr(geom, "_style"):
        for p_key, vl_key in _PARAM_MAP.items():
            if p_key in geom._style and vl_key not in mark:
                mark[vl_key] = geom._style[p_key]
