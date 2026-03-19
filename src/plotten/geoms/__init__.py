from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._col import GeomCol
from plotten.geoms._contour import GeomContour, GeomContourFilled
from plotten.geoms._crossbar import GeomCrossbar
from plotten.geoms._curve import GeomCurve
from plotten.geoms._density import GeomDensity
from plotten.geoms._density_ridges import GeomDensityRidges
from plotten.geoms._dotplot import GeomDotplot
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._errorbarh import GeomErrorbarH
from plotten.geoms._freqpoly import GeomFreqpoly
from plotten.geoms._hex import GeomHex
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._line import GeomLine
from plotten.geoms._linerange import GeomLinerange
from plotten.geoms._path import GeomPath
from plotten.geoms._point import GeomPoint
from plotten.geoms._pointrange import GeomPointrange
from plotten.geoms._polygon import GeomPolygon
from plotten.geoms._quantile import GeomQuantile
from plotten.geoms._raster import GeomRaster
from plotten.geoms._rect import GeomRect
from plotten.geoms._refline import GeomAbLine, GeomHLine, GeomVLine
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._rug import GeomRug
from plotten.geoms._segment import GeomSegment
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._spoke import GeomSpoke
from plotten.geoms._step import GeomStep
from plotten.geoms._summary import GeomSummary
from plotten.geoms._text import GeomLabel, GeomText
from plotten.geoms._tile import GeomTile
from plotten.geoms._violin import GeomViolin


def _extract_aes(params: dict[str, Any]) -> tuple[Aes, dict[str, Any]]:
    """Split params into Aes fields and remaining params."""
    from plotten._computed import AfterScale, AfterStat

    aes_kwargs = {
        k: params.pop(k)
        for k in list(params)
        if hasattr(Aes, k) and isinstance(params[k], str | AfterStat | AfterScale)
    }
    return Aes(**aes_kwargs), params


def _make_geom_factory(geom_cls: type, doc: str):
    """Generate a standard geom factory: pop position, extract aes, return Layer."""

    def factory(**params: Any) -> Layer:
        position = params.pop("position", None)
        data = params.pop("data", None)
        mapping, params = _extract_aes(params)
        return Layer(geom=geom_cls(), mapping=mapping, params=params, position=position, data=data)

    factory.__doc__ = doc
    factory.__qualname__ = f"geom_{geom_cls.__name__}"
    return factory


# --- Standard factories (generated) ---
geom_point = _make_geom_factory(GeomPoint, "Create a point layer.")
geom_line = _make_geom_factory(GeomLine, "Create a line layer.")
geom_bar = _make_geom_factory(GeomBar, "Create a bar layer.")
geom_boxplot = _make_geom_factory(GeomBoxplot, "Create a boxplot layer.")
geom_text = _make_geom_factory(GeomText, "Create a text layer.")
geom_label = _make_geom_factory(GeomLabel, "Create a label (text with background box) layer.")
geom_area = _make_geom_factory(GeomArea, "Create a filled area layer.")
geom_ribbon = _make_geom_factory(GeomRibbon, "Create a ribbon (filled band) layer.")
geom_tile = _make_geom_factory(GeomTile, "Create a tile (heatmap) layer.")
geom_errorbar = _make_geom_factory(GeomErrorbar, "Create an errorbar layer.")
geom_errorbarh = _make_geom_factory(GeomErrorbarH, "Create a horizontal errorbar layer.")
geom_col = _make_geom_factory(GeomCol, "Create a column (pre-counted bar) layer.")
geom_violin = _make_geom_factory(GeomViolin, "Create a violin plot layer.")
geom_segment = _make_geom_factory(GeomSegment, "Create a segment layer.")
geom_rect = _make_geom_factory(GeomRect, "Create a rectangle layer.")
geom_step = _make_geom_factory(GeomStep, "Create a step line layer.")
geom_rug = _make_geom_factory(GeomRug, "Create a rug layer.")
geom_path = _make_geom_factory(GeomPath, "Create a path layer (connects points in data order).")
geom_polygon = _make_geom_factory(GeomPolygon, "Create a polygon layer.")
geom_crossbar = _make_geom_factory(GeomCrossbar, "Create a crossbar layer.")
geom_pointrange = _make_geom_factory(GeomPointrange, "Create a pointrange layer.")
geom_linerange = _make_geom_factory(GeomLinerange, "Create a linerange layer.")
geom_hex = _make_geom_factory(GeomHex, "Create a hexagonal binning layer.")
geom_curve = _make_geom_factory(GeomCurve, "Create a curved line segment layer.")
geom_spoke = _make_geom_factory(GeomSpoke, "Create a spoke (radial segment) layer.")


# --- Non-standard factories (hand-written) ---
def geom_freqpoly(bins: int = 30, **params: Any) -> Layer:
    """Create a frequency polygon layer (line through bin midpoints)."""
    from plotten.stats._bin import StatBin

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomFreqpoly(),
        stat=StatBin(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


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


def geom_smooth(method: str = "loess", se: bool = True, degree: int = 2, **params: Any) -> Layer:
    """Create a smooth line layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    geom = GeomSmooth(method=method, se=se, degree=degree)
    return Layer(
        geom=geom,
        stat=geom.default_stat(),
        mapping=mapping,
        params=params,
        position=position,
    )


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


def geom_jitter(
    width: float = 0.4, height: float = 0.0, seed: int | None = None, **params: Any
) -> Layer:
    """Create a jittered point layer."""
    from plotten.positions._jitter import PositionJitter

    position = PositionJitter(width=width, height=height, seed=seed)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPoint(), mapping=mapping, params=params, position=position)


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
    fun_data: str | Any = None,
    **params: Any,
) -> Layer:
    """Create a summary layer (point + error bars)."""
    from plotten.stats._summary import StatSummary

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomSummary(),
        stat=StatSummary(fun_y=fun_y, fun_ymin=fun_ymin, fun_ymax=fun_ymax, fun_data=fun_data),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_function(fun: Any, n: int = 101, xlim: Any = None, **params: Any) -> Layer:
    """Create a layer that plots y = f(x)."""
    import narwhals as nw

    from plotten.stats._function import StatFunction

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    for _backend in ("polars", "pandas"):
        try:
            dummy = nw.to_native(nw.from_dict({"x": [0]}, backend=_backend))
            break
        except ImportError:
            continue
    else:
        msg = "Either polars or pandas must be installed"
        raise ImportError(msg)
    return Layer(
        geom=GeomLine(),
        stat=StatFunction(fun=fun, n=n, xlim=xlim),
        mapping=mapping,
        params=params,
        position=position,
        data=dummy,
    )


def geom_contour(**params: Any) -> Layer:
    """Create a contour line layer."""
    from plotten.stats._contour import StatContour

    bins = params.pop("bins", 10)
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomContour(),
        stat=StatContour(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_contour_filled(**params: Any) -> Layer:
    """Create a filled contour layer."""
    from plotten.stats._contour import StatContour

    bins = params.pop("bins", 10)
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomContourFilled(),
        stat=StatContour(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_raster(**params: Any) -> Layer:
    """Create a raster layer."""
    from plotten.stats._identity import StatIdentity

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomRaster(),
        stat=StatIdentity(),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_density_2d(**params: Any) -> Layer:
    """Create a 2D density contour layer."""
    from plotten.stats._density2d import StatDensity2d

    n = params.pop("n", 100)
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomContour(),
        stat=StatDensity2d(n=n),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_dotplot(bins: int = 30, **params: Any) -> Layer:
    """Create a dotplot layer (stacked dots replacing histograms)."""
    from plotten.stats._dotplot import StatDotplot

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomDotplot(),
        stat=StatDotplot(bins=bins),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_summary_bin(
    bins: int = 30,
    fun_y: str = "mean",
    fun_ymin: str = "mean_se_lower",
    fun_ymax: str = "mean_se_upper",
    **params: Any,
) -> Layer:
    """Create a binned summary layer (point + error bars)."""
    from plotten.stats._summary_bin import StatSummaryBin

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomSummary(),
        stat=StatSummaryBin(bins=bins, fun_y=fun_y, fun_ymin=fun_ymin, fun_ymax=fun_ymax),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_ellipse(level: float = 0.95, segments: int = 51, **params: Any) -> Layer:
    """Draw a confidence ellipse around bivariate data."""
    from plotten.stats._ellipse import StatEllipse

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomPolygon(),
        stat=StatEllipse(level=level, segments=segments),
        mapping=mapping,
        params={**params, "fill": params.get("fill", "none")},
        position=position,
    )


def stat_density_2d_filled(**params: Any) -> Layer:
    """Create a filled 2D density contour layer."""
    from plotten.stats._density2d import StatDensity2d

    n = params.pop("n", 100)
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomContourFilled(),
        stat=StatDensity2d(n=n),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_cor(
    method: str = "pearson",
    label_x: float = 0.1,
    label_y: float = 0.9,
    digits: int = 2,
    **params: Any,
) -> Layer:
    """Overlay correlation coefficient and p-value text."""
    from plotten.stats._cor import StatCor

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomText(),
        stat=StatCor(method=method, label_x=label_x, label_y=label_y, digits=digits),
        mapping=mapping,
        params=params,
        position=position,
    )


def stat_poly_eq(
    degree: int = 1, label_x: float = 0.05, label_y: float = 0.95, **params: Any
) -> Layer:
    """Overlay polynomial equation and R² text."""
    from plotten.stats._poly_eq import StatPolyEq

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomText(),
        stat=StatPolyEq(degree=degree, label_x=label_x, label_y=label_y),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_count(**params: Any) -> Layer:
    """Count overlapping points and map count to size."""
    from plotten._computed import AfterStat
    from plotten.stats._count_overlap import StatCountOverlap

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)

    # Default: map size to after_stat("n") unless user explicitly set size
    default_mapping = Aes(size=AfterStat("n"))
    combined = default_mapping | mapping

    return Layer(
        geom=GeomPoint(),
        stat=StatCountOverlap(),
        mapping=combined,
        params=params,
        position=position,
    )


def stat_sum(**params: Any) -> Layer:
    """Alias for geom_count -- count overlapping observations."""
    return geom_count(**params)


def geom_quantile(
    quantiles: list[float] | None = None, n_points: int = 100, **params: Any
) -> Layer:
    """Create a quantile regression line layer."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    _quantiles = quantiles if quantiles is not None else [0.25, 0.5, 0.75]
    geom = GeomQuantile(quantiles=_quantiles, n_points=n_points)
    return Layer(
        geom=geom,
        stat=geom.default_stat(),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_density_ridges(
    bandwidth: float | None = None, n_points: int = 128, **params: Any
) -> Layer:
    """Create a ridge plot (stacked density curves by group)."""
    from plotten.geoms._density_ridges import GeomDensityRidges
    from plotten.stats._density_ridges import StatDensityRidges

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomDensityRidges(),
        stat=StatDensityRidges(bandwidth=bandwidth, n_points=n_points),
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
    "GeomContour",
    "GeomContourFilled",
    "GeomCrossbar",
    "GeomCurve",
    "GeomDensity",
    "GeomDensityRidges",
    "GeomDotplot",
    "GeomErrorbar",
    "GeomErrorbarH",
    "GeomFreqpoly",
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
    "GeomQuantile",
    "GeomRaster",
    "GeomRect",
    "GeomRibbon",
    "GeomRug",
    "GeomSegment",
    "GeomSmooth",
    "GeomSpoke",
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
    "geom_contour",
    "geom_contour_filled",
    "geom_count",
    "geom_crossbar",
    "geom_curve",
    "geom_density",
    "geom_density_ridges",
    "geom_dotplot",
    "geom_errorbar",
    "geom_errorbarh",
    "geom_freqpoly",
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
    "geom_quantile",
    "geom_raster",
    "geom_rect",
    "geom_ribbon",
    "geom_rug",
    "geom_segment",
    "geom_smooth",
    "geom_spoke",
    "geom_step",
    "geom_text",
    "geom_tile",
    "geom_violin",
    "geom_vline",
    "stat_cor",
    "stat_density_2d",
    "stat_density_2d_filled",
    "stat_ecdf",
    "stat_ellipse",
    "stat_function",
    "stat_poly_eq",
    "stat_sum",
    "stat_summary",
    "stat_summary_bin",
]
