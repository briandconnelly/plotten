from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._bar import GeomBar
from plotten.geoms._base import GeomBase
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._text import GeomLabel, GeomText


def _extract_aes(params: dict[str, Any]) -> tuple[Aes, dict[str, Any]]:
    """Split params into Aes fields and remaining params."""
    aes_kwargs = {k: params.pop(k) for k in list(params) if hasattr(Aes, k) and isinstance(params[k], str)}
    return Aes(**aes_kwargs), params


def geom_point(**params: Any) -> Layer:
    """Create a point layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPoint(), mapping=mapping, params=params)


def geom_line(**params: Any) -> Layer:
    """Create a line layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomLine(), mapping=mapping, params=params)


def geom_bar(**params: Any) -> Layer:
    """Create a bar layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomBar(), mapping=mapping, params=params)


def geom_histogram(bins: int = 30, **params: Any) -> Layer:
    """Create a histogram layer."""
    from plotten.stats._bin import StatBin
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomHistogram(), stat=StatBin(bins=bins), mapping=mapping, params=params)


def geom_boxplot(**params: Any) -> Layer:
    """Create a boxplot layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomBoxplot(), mapping=mapping, params=params)


def geom_smooth(method: str = "loess", se: bool = True, **params: Any) -> Layer:
    """Create a smooth line layer."""
    mapping, params = _extract_aes(params)
    geom = GeomSmooth(method=method, se=se)
    return Layer(geom=geom, stat=geom.default_stat(), mapping=mapping, params=params)


def geom_text(**params: Any) -> Layer:
    """Create a text layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomText(), mapping=mapping, params=params)


def geom_label(**params: Any) -> Layer:
    """Create a label (text with background box) layer."""
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomLabel(), mapping=mapping, params=params)


__all__ = [
    "GeomBase",
    "GeomBar",
    "GeomBoxplot",
    "GeomHistogram",
    "GeomLabel",
    "GeomLine",
    "GeomPoint",
    "GeomSmooth",
    "GeomText",
    "geom_bar",
    "geom_boxplot",
    "geom_histogram",
    "geom_label",
    "geom_line",
    "geom_point",
    "geom_smooth",
    "geom_text",
]
