"""Standard geom factory functions generated via _make_geom_factory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._col import GeomCol
from plotten.geoms._crossbar import GeomCrossbar
from plotten.geoms._curve import GeomCurve
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._errorbarh import GeomErrorbarH
from plotten.geoms._hex import GeomHex
from plotten.geoms._line import GeomLine
from plotten.geoms._linerange import GeomLinerange
from plotten.geoms._path import GeomPath
from plotten.geoms._point import GeomPoint
from plotten.geoms._pointrange import GeomPointrange
from plotten.geoms._polygon import GeomPolygon
from plotten.geoms._rect import GeomRect
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._rug import GeomRug
from plotten.geoms._segment import GeomSegment
from plotten.geoms._spoke import GeomSpoke
from plotten.geoms._step import GeomStep
from plotten.geoms._text import GeomLabel, GeomText
from plotten.geoms._tile import GeomTile
from plotten.geoms._violin import GeomViolin

if TYPE_CHECKING:
    from collections.abc import Callable


def _extract_aes(params: dict[str, Any]) -> tuple[Aes, dict[str, Any]]:
    """Split params into Aes fields and remaining params."""
    from plotten._computed import AfterScale, AfterStat

    aes_kwargs = {
        k: params.pop(k)
        for k in list(params)
        if hasattr(Aes, k) and isinstance(params[k], str | AfterStat | AfterScale)
    }
    return Aes(**aes_kwargs), params


def _make_geom_factory(geom_cls: type, doc: str) -> Callable[..., Layer]:
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
