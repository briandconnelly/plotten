"""Registry of unsupported features for Vega-Lite export."""

from __future__ import annotations

import warnings
from typing import Any

from plotten._validation import PlottenError, PlottenWarning


def _class_name(obj: Any) -> str:
    return type(obj).__name__


_UNSUPPORTED_GEOMS: set[str] = {
    "GeomContour",
    "GeomContourFilled",
    "GeomHex",
    "GeomSpoke",
    "GeomCurve",
    "GeomDensityRidges",
    "GeomQuantile",
    "GeomRug",
    "GeomDotplot",
    "GeomRaster",
    "GeomPolygon",
    "GeomAbLine",
    "GeomCrossbar",
    "GeomPointrange",
    "GeomLinerange",
    "GeomErrorbarH",
    "GeomViolin",
    "GeomSummary",
}


def check_geom(geom: Any) -> None:
    """Raise PlottenError if the geom has no Vega-Lite equivalent."""
    name = _class_name(geom)
    if name in _UNSUPPORTED_GEOMS:
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
    warnings.warn(msg, PlottenWarning, stacklevel=3)
