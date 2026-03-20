from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._contour import GeomContour, GeomContourFilled
from plotten.geoms._density import GeomDensity
from plotten.geoms._density_ridges import GeomDensityRidges
from plotten.geoms._dotplot import GeomDotplot
from plotten.geoms._factories import (
    GeomArea,
    GeomBar,
    GeomBoxplot,
    GeomCol,
    GeomCrossbar,
    GeomCurve,
    GeomErrorbar,
    GeomErrorbarH,
    GeomHex,
    GeomLabel,
    GeomLine,
    GeomLinerange,
    GeomPath,
    GeomPoint,
    GeomPointrange,
    GeomPolygon,
    GeomRect,
    GeomRibbon,
    GeomRug,
    GeomSegment,
    GeomSpoke,
    GeomStep,
    GeomText,
    GeomTile,
    GeomViolin,
    _extract_aes,
    geom_area,
    geom_bar,
    geom_boxplot,
    geom_col,
    geom_crossbar,
    geom_curve,
    geom_errorbar,
    geom_errorbarh,
    geom_hex,
    geom_label,
    geom_line,
    geom_linerange,
    geom_path,
    geom_point,
    geom_pointrange,
    geom_polygon,
    geom_rect,
    geom_ribbon,
    geom_rug,
    geom_segment,
    geom_spoke,
    geom_step,
    geom_text,
    geom_tile,
    geom_violin,
)
from plotten.geoms._freqpoly import GeomFreqpoly
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._quantile import GeomQuantile
from plotten.geoms._raster import GeomRaster
from plotten.geoms._refline import GeomAbLine, GeomHLine, GeomVLine
from plotten.geoms._repel import GeomLabelRepel, GeomTextRepel
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._summary import GeomSummary


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


def geom_density(
    fill: bool = True,
    alpha: float = 0.3,
    bw_method: str | float | None = None,
    bw_adjust: float = 1.0,
    **params: Any,
) -> Layer:
    """Create a density curve layer."""
    from plotten.stats._density import StatDensity

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    geom = GeomDensity(fill=fill, alpha=alpha)
    return Layer(
        geom=geom,
        stat=StatDensity(bw_method=bw_method, bw_adjust=bw_adjust),
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


def geom_text_repel(
    max_iter: int = 500,
    force: float = 1.0,
    force_pull: float = 1.0,
    box_padding: float = 0.25,
    point_padding: float = 0.1,
    nudge_x: float = 0.0,
    nudge_y: float = 0.0,
    segment_color: str = "#666666",
    segment_size: float = 0.5,
    seed: int | None = 42,
    **params: Any,
) -> Layer:
    """Create a text layer with automatic label repulsion."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomTextRepel(
            max_iter=max_iter,
            force=force,
            force_pull=force_pull,
            box_padding=box_padding,
            point_padding=point_padding,
            nudge_x=nudge_x,
            nudge_y=nudge_y,
            segment_color=segment_color,
            segment_size=segment_size,
            seed=seed,
        ),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_label_repel(
    max_iter: int = 500,
    force: float = 1.0,
    force_pull: float = 1.0,
    box_padding: float = 0.25,
    point_padding: float = 0.1,
    nudge_x: float = 0.0,
    nudge_y: float = 0.0,
    segment_color: str = "#666666",
    segment_size: float = 0.5,
    seed: int | None = 42,
    fill: str = "white",
    label_alpha: float = 0.8,
    **params: Any,
) -> Layer:
    """Create a label layer with background boxes and automatic label repulsion."""
    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomLabelRepel(
            max_iter=max_iter,
            force=force,
            force_pull=force_pull,
            box_padding=box_padding,
            point_padding=point_padding,
            nudge_x=nudge_x,
            nudge_y=nudge_y,
            segment_color=segment_color,
            segment_size=segment_size,
            seed=seed,
            fill=fill,
            label_alpha=label_alpha,
        ),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_density_ridges(
    bandwidth: float | None = None,
    n_points: int = 128,
    bw_adjust: float = 1.0,
    **params: Any,
) -> Layer:
    """Create a ridge plot (stacked density curves by group)."""
    from plotten.geoms._density_ridges import GeomDensityRidges
    from plotten.stats._density_ridges import StatDensityRidges

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomDensityRidges(),
        stat=StatDensityRidges(bandwidth=bandwidth, n_points=n_points, bw_adjust=bw_adjust),
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
    "GeomLabelRepel",
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
    "GeomTextRepel",
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
    "geom_label_repel",
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
    "geom_text_repel",
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
