"""Registry of unsupported features for Vega-Lite export."""

from __future__ import annotations

from typing import Any

from plotten._validation import PlottenError, plotten_warn


def _get_unsupported_classes() -> tuple[type, ...]:
    """Lazily import and return unsupported geom classes."""
    from plotten.geoms._contour import GeomContour, GeomContourFilled
    from plotten.geoms._crossbar import GeomCrossbar
    from plotten.geoms._curve import GeomCurve
    from plotten.geoms._density_ridges import GeomDensityRidges
    from plotten.geoms._dotplot import GeomDotplot
    from plotten.geoms._errorbarh import GeomErrorbarH
    from plotten.geoms._hex import GeomHex
    from plotten.geoms._linerange import GeomLinerange
    from plotten.geoms._pointrange import GeomPointrange
    from plotten.geoms._polygon import GeomPolygon
    from plotten.geoms._quantile import GeomQuantile
    from plotten.geoms._raster import GeomRaster
    from plotten.geoms._refline import GeomAbLine
    from plotten.geoms._rug import GeomRug
    from plotten.geoms._spoke import GeomSpoke
    from plotten.geoms._summary import GeomSummary
    from plotten.geoms._violin import GeomViolin

    return (
        GeomContour,
        GeomContourFilled,
        GeomHex,
        GeomSpoke,
        GeomCurve,
        GeomDensityRidges,
        GeomQuantile,
        GeomRug,
        GeomDotplot,
        GeomRaster,
        GeomPolygon,
        GeomAbLine,
        GeomCrossbar,
        GeomPointrange,
        GeomLinerange,
        GeomErrorbarH,
        GeomViolin,
        GeomSummary,
    )


def check_geom(geom: Any) -> None:
    """Raise PlottenError if the geom has no Vega-Lite equivalent."""
    if isinstance(geom, _get_unsupported_classes()):
        name = type(geom).__name__
        msg = (
            f"{name} is not supported by Vega-Lite export. "
            "Use render() or ggsave() for the matplotlib backend instead."
        )
        raise PlottenError(msg)


def warn_unsupported(feature: str, detail: str = "") -> None:
    """Issue a PlottenWarning for partially unsupported features."""
    msg = f"{feature} is not fully supported by Vega-Lite export."
    if detail:
        msg += f" {detail}"
    plotten_warn(msg, stacklevel=3)
