from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._col import GeomCol
from plotten.geoms._density import GeomDensity
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.geoms._refline import GeomAbLine, GeomHLine, GeomVLine
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._summary import GeomSummary
from plotten.geoms._text import GeomLabel, GeomText
from plotten.geoms._tile import GeomTile
from plotten.geoms._violin import GeomViolin


def _extract_aes(params: dict[str, Any]) -> tuple[Aes, dict[str, Any]]:
    """Split params into Aes fields and remaining params."""
    aes_kwargs = {
        k: params.pop(k) for k in list(params) if hasattr(Aes, k) and isinstance(params[k], str)
    }
    return Aes(**aes_kwargs), params


def geom_point(**params: Any) -> Layer:
    """Create a point layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPoint(), mapping=mapping, params=params, position=position)


def geom_line(**params: Any) -> Layer:
    """Create a line layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomLine(), mapping=mapping, params=params, position=position)


def geom_bar(**params: Any) -> Layer:
    """Create a bar layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomBar(), mapping=mapping, params=params, position=position)


def geom_histogram(bins: int = 30, **params: Any) -> Layer:
    """Create a histogram layer."""
    from plotten.stats._bin import StatBin

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomHistogram(),
        stat=StatBin(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_boxplot(**params: Any) -> Layer:
    """Create a boxplot layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomBoxplot(), mapping=mapping, params=params, position=position)


def geom_smooth(method: str = "loess", se: bool = True, **params: Any) -> Layer:
    """Create a smooth line layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    geom = GeomSmooth(method=method, se=se)
    return Layer(
        geom=geom,
        stat=geom.default_stat(),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_text(**params: Any) -> Layer:
    """Create a text layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomText(), mapping=mapping, params=params, position=position)


def geom_label(**params: Any) -> Layer:
    """Create a label (text with background box) layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomLabel(), mapping=mapping, params=params, position=position)


def geom_hline(yintercept: float, **params: Any) -> Layer:
    """Create a horizontal reference line layer."""
    position = params.pop("position", None)
    return Layer(
        geom=GeomHLine(yintercept, **params),
        mapping=Aes(),
        params=params,
        position=position,
    )


def geom_vline(xintercept: float, **params: Any) -> Layer:
    """Create a vertical reference line layer."""
    position = params.pop("position", None)
    return Layer(
        geom=GeomVLine(xintercept, **params),
        mapping=Aes(),
        params=params,
        position=position,
    )


def geom_abline(slope: float, intercept: float, **params: Any) -> Layer:
    """Create an arbitrary reference line layer."""
    position = params.pop("position", None)
    return Layer(
        geom=GeomAbLine(slope, intercept, **params),
        mapping=Aes(),
        params=params,
        position=position,
    )


def geom_area(**params: Any) -> Layer:
    """Create a filled area layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomArea(), mapping=mapping, params=params, position=position)


def geom_ribbon(**params: Any) -> Layer:
    """Create a ribbon (filled band) layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomRibbon(), mapping=mapping, params=params, position=position)


def geom_tile(**params: Any) -> Layer:
    """Create a tile (heatmap) layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomTile(), mapping=mapping, params=params, position=position)


def geom_errorbar(**params: Any) -> Layer:
    """Create an errorbar layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomErrorbar(), mapping=mapping, params=params, position=position)


def geom_col(**params: Any) -> Layer:
    """Create a column (pre-counted bar) layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomCol(), mapping=mapping, params=params, position=position)


def geom_density(fill: bool = True, alpha: float = 0.3, **params: Any) -> Layer:
    """Create a density curve layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    geom = GeomDensity(fill=fill, alpha=alpha)
    return Layer(
        geom=geom,
        stat=geom.default_stat(),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_violin(**params: Any) -> Layer:
    """Create a violin plot layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomViolin(), mapping=mapping, params=params, position=position)


def stat_summary(
    fun_y: str = "mean",
    fun_ymin: str = "mean_se_lower",
    fun_ymax: str = "mean_se_upper",
    **params: Any,
) -> Layer:
    """Create a summary layer (point + error bars)."""
    from plotten.stats._summary import StatSummary

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomSummary(),
        stat=StatSummary(fun_y=fun_y, fun_ymin=fun_ymin, fun_ymax=fun_ymax),
        mapping=mapping,
        params=params,
        position=position,
    )


__all__ = [
    "GeomAbLine",
    "GeomArea",
    "GeomBar",
    "GeomBoxplot",
    "GeomCol",
    "GeomDensity",
    "GeomErrorbar",
    "GeomHLine",
    "GeomHistogram",
    "GeomLabel",
    "GeomLine",
    "GeomPoint",
    "GeomRibbon",
    "GeomSmooth",
    "GeomSummary",
    "GeomText",
    "GeomTile",
    "GeomVLine",
    "GeomViolin",
    "geom_abline",
    "geom_area",
    "geom_bar",
    "geom_boxplot",
    "geom_col",
    "geom_density",
    "geom_errorbar",
    "geom_histogram",
    "geom_hline",
    "geom_label",
    "geom_line",
    "geom_point",
    "geom_ribbon",
    "geom_smooth",
    "geom_text",
    "geom_tile",
    "geom_violin",
    "geom_vline",
    "stat_summary",
]
