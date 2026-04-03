from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._enums import SmoothMethod
from plotten._layer import Layer
from plotten.geoms._blank import GeomBlank
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
from plotten.geoms._signif import GeomSignif
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._summary import GeomSummary


# --- Non-standard factories (hand-written) ---
def geom_freqpoly(bins: int = 30, **params: Any) -> Layer:
    """Create a frequency polygon layer (line through bin midpoints).

    Parameters
    ----------
    bins : int, optional
        Number of bins (default 30).
    **params
        Aesthetic mappings and fixed visual properties such as ``color``
        and ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_freqpoly
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
    >>> p = ggplot(df, aes(x="x")) + geom_freqpoly(bins=5)
    """
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
    """Create a histogram layer.

    Parameters
    ----------
    bins : int, optional
        Number of bins (default 30).
    **params
        Aesthetic mappings and fixed visual properties such as ``fill``
        and ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_histogram
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
    >>> p = ggplot(df, aes(x="x")) + geom_histogram(bins=10, fill="steelblue")
    """
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


def geom_smooth(
    method: str | SmoothMethod = SmoothMethod.LOESS,
    se: bool = True,
    degree: int = 2,
    **params: Any,
) -> Layer:
    """Create a smooth trend line layer.

    Parameters
    ----------
    method : str or SmoothMethod, optional
        Smoothing method: ``SmoothMethod.LOESS`` (default), ``SmoothMethod.OLS``
        (linear), ``SmoothMethod.POLY``, or ``SmoothMethod.MOVING_AVERAGE``.
        Plain strings like ``"loess"`` and ``"lm"`` are also accepted.
    se : bool, optional
        Whether to draw the confidence interval band (default ``True``).
    degree : int, optional
        Polynomial degree for the fit (default 2).
    **params
        Aesthetic mappings and fixed visual properties such as ``color``.

    Raises
    ------
    StatError
        If *method* is not a recognized smoothing method.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_smooth
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 4, 2, 5]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_smooth(method="lm")
    """
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
    """Create a horizontal reference line layer.

    Parameters
    ----------
    yintercept : float
        The y-axis value where the line is drawn.
    **params
        Fixed visual properties such as ``color``, ``linetype``, and
        ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_hline
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 3]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_hline(yintercept=3, linetype="dashed")
    """
    position = params.pop("position", None)
    return Layer(
        geom=GeomHLine(yintercept, **params),
        mapping=Aes(),
        params=params,
        position=position,
    )


def geom_vline(xintercept: float, **params: Any) -> Layer:
    """Create a vertical reference line layer.

    Parameters
    ----------
    xintercept : float
        The x-axis value where the line is drawn.
    **params
        Fixed visual properties such as ``color``, ``linetype``, and
        ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_vline
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 3]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_vline(xintercept=2, color="red")
    """
    position = params.pop("position", None)
    return Layer(
        geom=GeomVLine(xintercept, **params),
        mapping=Aes(),
        params=params,
        position=position,
    )


def geom_abline(slope: float, intercept: float, **params: Any) -> Layer:
    """Create an arbitrary reference line layer.

    Parameters
    ----------
    slope : float
        Slope of the line.
    intercept : float
        Y-intercept of the line.
    **params
        Fixed visual properties such as ``color``, ``linetype``, and
        ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_abline
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_abline(slope=2, intercept=0)
    """
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
    """Create a density curve layer.

    Parameters
    ----------
    fill : bool, optional
        Whether to fill the area under the curve (default ``True``).
    alpha : float, optional
        Opacity from 0 (transparent) to 1 (default 0.3).
    bw_method : str or float or None, optional
        Bandwidth estimation method passed to the kernel density estimator.
    bw_adjust : float, optional
        Multiplicative adjustment to the bandwidth (default 1.0).
    **params
        Aesthetic mappings and fixed visual properties such as ``color``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_density
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4]})
    >>> p = ggplot(df, aes(x="x")) + geom_density(fill=True, alpha=0.4)
    """
    from plotten.stats._density import StatDensity

    position = params.pop("position", None)
    data = params.pop("data", None)
    mapping, params = _extract_aes(params)
    geom = GeomDensity(fill=fill, alpha=alpha)
    return Layer(
        geom=geom,
        stat=StatDensity(bw_method=bw_method, bw_adjust=bw_adjust),
        mapping=mapping,
        params=params,
        position=position,
        data=data,
    )


def geom_jitter(
    width: float = 0.4, height: float = 0.0, seed: int | None = None, **params: Any
) -> Layer:
    """Create a jittered point layer.

    Parameters
    ----------
    width : float, optional
        Amount of horizontal jitter (default 0.4).
    height : float, optional
        Amount of vertical jitter (default 0.0).
    seed : int or None, optional
        Random seed for reproducible jitter.
    **params
        Aesthetic mappings and fixed visual properties such as ``color``
        and ``size``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_jitter
    >>> df = pd.DataFrame({"g": ["a", "a", "b", "b"], "v": [1, 1, 2, 2]})
    >>> p = ggplot(df, aes(x="g", y="v")) + geom_jitter(width=0.2, seed=42)
    """
    from plotten.positions._jitter import PositionJitter

    position = PositionJitter(width=width, height=height, seed=seed)
    mapping, params = _extract_aes(params)
    return Layer(geom=GeomPoint(), mapping=mapping, params=params, position=position)


def geom_bin2d(bins: int | tuple[int, int] = 30, **params: Any) -> Layer:
    """Create a 2D bin (rectangular heatmap) layer.

    Parameters
    ----------
    bins : int or tuple of int, optional
        Number of bins in x and y directions (default 30).
    **params
        Aesthetic mappings and fixed visual properties such as ``fill``
        and ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_bin2d
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3], "y": [1, 1, 2, 3]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_bin2d(bins=10)
    """
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
    """Create an ECDF (empirical cumulative distribution function) layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``color``) and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_ecdf
    >>> df = pd.DataFrame({"x": [1, 3, 2, 5, 4]})
    >>> p = ggplot(df, aes(x="x")) + stat_ecdf()
    """
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
    """Create a QQ plot layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``sample``) and fixed visual properties such
        as ``color`` and ``size``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_qq
    >>> df = pd.DataFrame({"val": [1, 2, 3, 4, 5]})
    >>> p = ggplot(df, aes(sample="val")) + geom_qq()
    """
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
    """Create a QQ reference line layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``sample``) and fixed visual properties such
        as ``color`` and ``linetype``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_qq, geom_qq_line
    >>> df = pd.DataFrame({"val": [1, 2, 3, 4, 5]})
    >>> p = ggplot(df, aes(sample="val")) + geom_qq() + geom_qq_line()
    """
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
    """Create a summary layer (point with error bars).

    Parameters
    ----------
    fun_y : str, optional
        Summary function for the center point (default ``"mean"``).
    fun_ymin : str, optional
        Summary function for the lower bar (default ``"mean_se_lower"``).
    fun_ymax : str, optional
        Summary function for the upper bar (default ``"mean_se_upper"``).
    fun_data : str or callable or None, optional
        A single function returning y, ymin, ymax together.
    **params
        Aesthetic mappings and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_summary
    >>> df = pd.DataFrame({"g": ["a"]*4 + ["b"]*4, "v": [1, 2, 3, 4, 3, 4, 5, 6]})
    >>> p = ggplot(df, aes(x="g", y="v")) + stat_summary(fun_y="mean")
    """
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
    """Create a layer that plots y = f(x).

    Parameters
    ----------
    fun : callable
        A function accepting a numeric array and returning y values.
    n : int, optional
        Number of evaluation points (default 101).
    xlim : tuple of float or None, optional
        Range ``(xmin, xmax)`` over which to evaluate the function.
    **params
        Aesthetic mappings and fixed visual properties such as ``color``.

    Examples
    --------
    >>> import math
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_function
    >>> p = ggplot() + stat_function(fun=math.sin, xlim=(-3.14, 3.14))
    """
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
    """Create a contour line layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``, ``z``) and fixed visual
        properties.  Pass ``bins`` to control the number of contour
        levels (default 10).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_contour
    >>> df = pd.DataFrame({"x": [0, 1, 0, 1], "y": [0, 0, 1, 1], "z": [1, 2, 3, 4]})
    >>> p = ggplot(df, aes(x="x", y="y", z="z")) + geom_contour()
    """
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
    """Create a filled contour layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``, ``z``) and fixed visual
        properties.  Pass ``bins`` to control the number of contour
        levels (default 10).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_contour_filled
    >>> df = pd.DataFrame({"x": [0, 1, 0, 1], "y": [0, 0, 1, 1], "z": [1, 2, 3, 4]})
    >>> p = ggplot(df, aes(x="x", y="y", z="z")) + geom_contour_filled()
    """
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
    """Create a raster layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``, ``fill``) and fixed visual
        properties such as ``alpha``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_raster
    >>> df = pd.DataFrame({"x": [0, 1, 0, 1], "y": [0, 0, 1, 1], "v": [1, 2, 3, 4]})
    >>> p = ggplot(df, aes(x="x", y="y", fill="v")) + geom_raster()
    """
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
    """Create a 2D density contour layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``) and fixed visual properties.
        Pass ``n`` to control the density grid resolution (default 100).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_density_2d
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3], "y": [1, 1, 2, 3]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_density_2d()
    """
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
    """Create a dotplot layer (stacked dots replacing histograms).

    Parameters
    ----------
    bins : int, optional
        Number of bins (default 30).
    **params
        Aesthetic mappings and fixed visual properties such as ``fill``
        and ``color``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_dotplot
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
    >>> p = ggplot(df, aes(x="x")) + geom_dotplot(bins=10)
    """
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
    """Create a binned summary layer (point with error bars per bin).

    Parameters
    ----------
    bins : int, optional
        Number of bins (default 30).
    fun_y : str, optional
        Summary function for the center point (default ``"mean"``).
    fun_ymin : str, optional
        Summary function for the lower bar (default ``"mean_se_lower"``).
    fun_ymax : str, optional
        Summary function for the upper bar (default ``"mean_se_upper"``).
    **params
        Aesthetic mappings and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_summary_bin
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 5, 4]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_summary_bin(bins=3)
    """
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
    """Draw a confidence ellipse around bivariate data.

    Parameters
    ----------
    level : float, optional
        Confidence level for the ellipse (default 0.95).
    segments : int, optional
        Number of line segments used to approximate the ellipse
        (default 51).
    **params
        Aesthetic mappings (``x``, ``y``, ``color``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_ellipse
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 3, 5, 4]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_ellipse(level=0.9)
    """
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
    """Create a filled 2D density contour layer.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``) and fixed visual properties.
        Pass ``n`` to control the density grid resolution (default 100).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_density_2d_filled
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3], "y": [1, 1, 2, 3]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_density_2d_filled()
    """
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
    """Overlay correlation coefficient and p-value text.

    Parameters
    ----------
    method : str, optional
        Correlation method: ``"pearson"`` (default), ``"spearman"``, or
        ``"kendall"``.
    label_x : float, optional
        Relative x position of the label (default 0.1).
    label_y : float, optional
        Relative y position of the label (default 0.9).
    digits : int, optional
        Number of decimal digits (default 2).
    **params
        Aesthetic mappings and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_cor
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 5, 8]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_cor(method="pearson")
    """
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
    """Overlay polynomial equation and R-squared text.

    Parameters
    ----------
    degree : int, optional
        Degree of the polynomial fit (default 1).
    label_x : float, optional
        Relative x position of the label (default 0.05).
    label_y : float, optional
        Relative y position of the label (default 0.95).
    **params
        Aesthetic mappings and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_poly_eq
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 5, 8]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_poly_eq(degree=1)
    """
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
    """Count overlapping points and map count to size.

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``, ``color``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_count
    >>> df = pd.DataFrame({"x": [1, 1, 2, 2, 2], "y": [1, 1, 2, 2, 2]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_count()
    """
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
    """Count overlapping observations (alias for ``geom_count``).

    Parameters
    ----------
    **params
        Aesthetic mappings (``x``, ``y``, ``color``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_sum
    >>> df = pd.DataFrame({"x": [1, 1, 2, 2, 2], "y": [1, 1, 2, 2, 2]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_sum()
    """
    return geom_count(**params)


def geom_quantile(
    quantiles: list[float] | None = None, n_points: int = 100, **params: Any
) -> Layer:
    """Create a quantile regression line layer.

    Parameters
    ----------
    quantiles : list of float or None, optional
        Quantiles to estimate (default ``[0.25, 0.5, 0.75]``).
    n_points : int, optional
        Number of evaluation points per quantile line (default 100).
    **params
        Aesthetic mappings and fixed visual properties such as ``color``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_quantile
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 5, 4]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_quantile()
    """
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
    """Create a text layer with automatic label repulsion.

    Parameters
    ----------
    max_iter : int, optional
        Maximum repulsion iterations (default 500).
    force : float, optional
        Repulsion force strength (default 1.0).
    force_pull : float, optional
        Pull-back force toward the original position (default 1.0).
    box_padding : float, optional
        Padding around label bounding boxes (default 0.25).
    point_padding : float, optional
        Padding around data points (default 0.1).
    nudge_x : float, optional
        Initial horizontal offset (default 0.0).
    nudge_y : float, optional
        Initial vertical offset (default 0.0).
    segment_color : str, optional
        Color of the connector segments (default ``"#666666"``).
    segment_size : float, optional
        Width of the connector segments (default 0.5).
    seed : int or None, optional
        Random seed for reproducibility (default 42).
    **params
        Aesthetic mappings (``x``, ``y``, ``label``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_text_repel
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2], "lbl": ["A", "B", "C"]})
    >>> p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_text_repel()
    """
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
    """Create a label layer with background boxes and automatic label repulsion.

    Parameters
    ----------
    max_iter : int, optional
        Maximum repulsion iterations (default 500).
    force : float, optional
        Repulsion force strength (default 1.0).
    force_pull : float, optional
        Pull-back force toward the original position (default 1.0).
    box_padding : float, optional
        Padding around label bounding boxes (default 0.25).
    point_padding : float, optional
        Padding around data points (default 0.1).
    nudge_x : float, optional
        Initial horizontal offset (default 0.0).
    nudge_y : float, optional
        Initial vertical offset (default 0.0).
    segment_color : str, optional
        Color of the connector segments (default ``"#666666"``).
    segment_size : float, optional
        Width of the connector segments (default 0.5).
    seed : int or None, optional
        Random seed for reproducibility (default 42).
    fill : str, optional
        Background box fill color (default ``"white"``).
    label_alpha : float, optional
        Background box opacity (default 0.8).
    **params
        Aesthetic mappings (``x``, ``y``, ``label``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_label_repel
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2], "lbl": ["A", "B", "C"]})
    >>> p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_label_repel()
    """
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
    """Create a ridge plot (stacked density curves by group).

    Parameters
    ----------
    bandwidth : float or None, optional
        Fixed bandwidth for the kernel density estimate.
    n_points : int, optional
        Number of evaluation points per ridge (default 128).
    bw_adjust : float, optional
        Multiplicative adjustment to the bandwidth (default 1.0).
    **params
        Aesthetic mappings (``x``, ``y``, ``fill``) and fixed visual
        properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_density_ridges
    >>> df = pd.DataFrame({"x": [1, 2, 3, 2, 3, 4], "g": ["a"]*3 + ["b"]*3})
    >>> p = ggplot(df, aes(x="x", y="g")) + geom_density_ridges()
    """
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


def geom_signif(
    comparisons: list[tuple[str, str]],
    test: str = "t-test",
    step_increase: float = 0.1,
    tip_length: float = 0.02,
    text_format: str = "stars",
    p_adjust: str | None = None,
    **params: Any,
) -> Layer:
    """Add significance brackets with p-value annotations.

    Parameters
    ----------
    comparisons : list of tuple of str
        Pairs of group names to compare, e.g. ``[("a", "b"), ("b", "c")]``.
    test : str, optional
        Statistical test: ``"t-test"`` (default), ``"wilcoxon"``, or
        ``"mann-whitney"``.
    step_increase : float, optional
        Fraction of the y-range to offset successive brackets (default 0.1).
    tip_length : float, optional
        Length of bracket tips as a fraction of y-range (default 0.02).
    text_format : str, optional
        ``"stars"`` (default) shows ``*``/``**``/``***``/``ns``, or
        ``"p-value"`` shows the numeric p-value.
    p_adjust : str or None, optional
        Multiple testing correction: ``"bonferroni"``, ``"holm"``,
        ``"fdr"``, or ``None`` (default).
    **params
        Additional visual properties such as ``color``, ``size``,
        ``fontsize``.

    Raises
    ------
    StatError
        If *test* is not a recognized statistical test, or if
        *p_adjust* is not a recognized correction method.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_boxplot
    >>> from plotten.geoms import geom_signif
    >>> df = pd.DataFrame({"g": ["a"]*10 + ["b"]*10, "v": list(range(10)) + list(range(5, 15))})
    >>> p = ggplot(df, aes(x="g", y="v")) + geom_boxplot() + geom_signif(comparisons=[("a", "b")])
    """
    from plotten.stats._signif import StatSignif

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomSignif(tip_length=tip_length, text_format=text_format),
        stat=StatSignif(
            comparisons=comparisons,
            test=test,
            p_adjust=p_adjust,
            step_increase=step_increase,
        ),
        mapping=mapping,
        params=params,
        position=position,
    )


def geom_blank(**params: Any) -> Layer:
    """Create a blank layer that trains scales without drawing.

    Useful for expanding axis limits from data without rendering any marks.

    Parameters
    ----------
    **params
        Aesthetic mappings and layer-specific data.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import geom_blank
    >>> df = pd.DataFrame({"x": [0, 10], "y": [0, 100]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_blank()
    """
    from plotten.stats._identity import StatIdentity

    position = params.pop("position", None)
    data = params.pop("data", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomBlank(),
        stat=StatIdentity(),
        mapping=mapping,
        params=params,
        position=position,
        data=data,
    )


def stat_unique(**params: Any) -> Layer:
    """Create a layer that deduplicates observations before plotting.

    By default uses ``geom_point``, but a different geom can be layered on
    top of deduplicated data.

    Parameters
    ----------
    **params
        Aesthetic mappings and fixed visual properties.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes
    >>> from plotten.geoms import stat_unique
    >>> df = pd.DataFrame({"x": [1, 1, 2, 2, 3], "y": [1, 1, 4, 4, 9]})
    >>> p = ggplot(df, aes(x="x", y="y")) + stat_unique()
    """
    from plotten.stats._unique import StatUnique

    position = params.pop("position", None)
    mapping, params = _extract_aes(params)
    return Layer(
        geom=GeomPoint(),
        stat=StatUnique(),
        mapping=mapping,
        params=params,
        position=position,
    )


__all__ = [
    "GeomAbLine",
    "GeomArea",
    "GeomBar",
    "GeomBlank",
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
    "GeomSignif",
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
    "geom_blank",
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
    "geom_signif",
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
    "stat_unique",
]
