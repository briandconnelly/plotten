from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._col import GeomCol
from plotten.geoms._crossbar import GeomCrossbar
from plotten.geoms._density import GeomDensity
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._hex import GeomHex
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._line import GeomLine
from plotten.geoms._linerange import GeomLinerange
from plotten.geoms._path import GeomPath
from plotten.geoms._point import GeomPoint
from plotten.geoms._pointrange import GeomPointrange
from plotten.geoms._polygon import GeomPolygon
from plotten.geoms._rect import GeomRect
from plotten.geoms._refline import GeomAbLine, GeomHLine, GeomVLine
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._rug import GeomRug
from plotten.geoms._segment import GeomSegment
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._step import GeomStep
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


def geom_segment(**params: Any) -> Layer:
    """Create a segment layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomSegment(), mapping=mapping, params=params, position=position)


def geom_rect(**params: Any) -> Layer:
    """Create a rectangle layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomRect(), mapping=mapping, params=params, position=position)


def geom_step(**params: Any) -> Layer:
    """Create a step line layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomStep(), mapping=mapping, params=params, position=position)


def geom_rug(**params: Any) -> Layer:
    """Create a rug layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomRug(), mapping=mapping, params=params, position=position)


def geom_jitter(
    width: float = 0.4, height: float = 0.0, seed: int | None = None, **params: Any
) -> Layer:
    """Create a jittered point layer."""
    from plotten.positions._jitter import PositionJitter

    position = PositionJitter(width=width, height=height, seed=seed)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPoint(), mapping=mapping, params=params, position=position)


def geom_path(**params: Any) -> Layer:
    """Create a path layer (connects points in data order)."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPath(), mapping=mapping, params=params, position=position)


def geom_polygon(**params: Any) -> Layer:
    """Create a polygon layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPolygon(), mapping=mapping, params=params, position=position)


def geom_crossbar(**params: Any) -> Layer:
    """Create a crossbar layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomCrossbar(), mapping=mapping, params=params, position=position)


def geom_pointrange(**params: Any) -> Layer:
    """Create a pointrange layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPointrange(), mapping=mapping, params=params, position=position)


def geom_linerange(**params: Any) -> Layer:
    """Create a linerange layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomLinerange(), mapping=mapping, params=params, position=position)


def geom_hex(**params: Any) -> Layer:
    """Create a hexagonal binning layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomHex(), mapping=mapping, params=params, position=position)


def geom_bin2d(bins: int | tuple[int, int] = 30, **params: Any) -> Layer:
    """Create a 2D bin (rectangular heatmap) layer."""
    from plotten.stats._bin2d import StatBin2d

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomTile(),
        stat=StatBin2d(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_ecdf(**params: Any) -> Layer:
    """Create an ECDF (empirical CDF) layer."""
    from plotten.stats._ecdf import StatECDF

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomStep(),
        stat=StatECDF(),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_qq(**params: Any) -> Layer:
    """Create a QQ plot layer."""
    from plotten.stats._qq import StatQQ

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomPoint(),
        stat=StatQQ(),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_qq_line(**params: Any) -> Layer:
    """Create a QQ reference line layer."""
    from plotten.stats._qq import StatQQLine

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomLine(),
        stat=StatQQLine(),
        mapping=mapping,
        params=params,
        position=position,
    )


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
    "GeomCrossbar",
    "GeomDensity",
    "GeomErrorbar",
    "GeomHLine",
    "GeomHex",
    "GeomHistogram",
    "GeomLabel",
    "GeomLine",
    "GeomLinerange",
    "GeomPath",
    "GeomPoint",
    "GeomPointrange",
    "GeomPolygon",
    "GeomRect",
    "GeomRibbon",
    "GeomRug",
    "GeomSegment",
    "GeomSmooth",
    "GeomStep",
    "GeomSummary",
    "GeomText",
    "GeomTile",
    "GeomVLine",
    "GeomViolin",
    "geom_abline",
    "geom_area",
    "geom_bar",
    "geom_bin2d",
    "geom_boxplot",
    "geom_col",
    "geom_crossbar",
    "geom_density",
    "geom_errorbar",
    "geom_hex",
    "geom_histogram",
    "geom_hline",
    "geom_jitter",
    "geom_label",
    "geom_line",
    "geom_linerange",
    "geom_path",
    "geom_point",
    "geom_pointrange",
    "geom_polygon",
    "geom_qq",
    "geom_qq_line",
    "geom_rect",
    "geom_ribbon",
    "geom_rug",
    "geom_segment",
    "geom_smooth",
    "geom_step",
    "geom_text",
    "geom_tile",
    "geom_violin",
    "geom_vline",
    "stat_ecdf",
    "stat_summary",
]
