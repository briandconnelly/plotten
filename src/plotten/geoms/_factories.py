"""Standard geom factory functions generated via _make_geom_factory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten._validation import (
    validate_aesthetic_value,
    validate_alpha,
    validate_color,
    validate_geom_params,
    validate_size,
)
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


_PASSTHROUGH_AESTHETICS = frozenset({"hatch"})


def _extract_aes(params: dict[str, Any]) -> tuple[Aes, dict[str, Any]]:
    """Split params into Aes fields and remaining params.

    Aesthetics in ``_PASSTHROUGH_AESTHETICS`` are only extracted when the
    value is an ``AfterStat`` or ``AfterScale`` — plain strings are kept
    as fixed params since they represent literal values (e.g. hatch
    patterns), not column names.
    """
    from plotten._computed import AfterScale, AfterStat

    aes_kwargs = {}
    for k in list(params):
        if not hasattr(Aes, k):
            continue
        val = params[k]
        if k in _PASSTHROUGH_AESTHETICS:
            if isinstance(val, AfterStat | AfterScale):
                aes_kwargs[k] = params.pop(k)
        elif isinstance(val, str | AfterStat | AfterScale):
            aes_kwargs[k] = params.pop(k)
    return Aes(**aes_kwargs), params


def _validate_layer_params(geom_name: str, geom_cls: type, params: dict[str, Any]) -> None:
    """Validate fixed params against geom known_params and check aesthetic values."""
    known = getattr(geom_cls, "known_params", None)
    if known is not None:
        validate_geom_params(geom_name, params, known)

    for key, value in params.items():
        if key in ("color", "fill"):
            validate_color(value)
        elif key == "alpha":
            validate_alpha(value)
        elif key == "size":
            validate_size(value)
        elif key in ("shape", "linetype", "hatch"):
            validate_aesthetic_value(key, value)


def _make_geom_factory(geom_cls: type, doc: str) -> Callable[..., Layer]:
    """Generate a standard geom factory: pop position, extract aes, return Layer."""

    def factory(**params: Any) -> Layer:
        position = params.pop("position", None)
        data = params.pop("data", None)
        explicit_mapping = params.pop("mapping", None)
        mapping, params = _extract_aes(params)
        if explicit_mapping is not None:
            mapping = mapping | explicit_mapping
        _validate_layer_params(factory.__name__, geom_cls, params)
        return Layer(geom=geom_cls(), mapping=mapping, params=params, position=position, data=data)

    factory.__doc__ = doc
    factory.__name__ = (
        f"geom_{geom_cls.__name__[4:].lower()}"
        if geom_cls.__name__.startswith("Geom")
        else geom_cls.__name__
    )
    factory.__qualname__ = factory.__name__
    return factory


# --- Standard factories (generated) ---
geom_point = _make_geom_factory(
    GeomPoint,
    """Create a scatter point layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
color : str, optional
    Point color as a column name or fixed value.
size : float, optional
    Point area in squared points (default 36).
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).
shape : str, optional
    Marker shape such as ``"o"``, ``"s"``, or ``"^"``.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_point
>>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_point(color="steelblue")
""",
)

geom_line = _make_geom_factory(
    GeomLine,
    """Create a line layer connecting observations ordered by x.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
color : str, optional
    Line color as a column name or fixed value.
linetype : str, optional
    Line style such as ``"solid"``, ``"dashed"``, or ``"dotted"``.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_line
>>> df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 4]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_line()
""",
)

geom_bar = _make_geom_factory(
    GeomBar,
    """Create a bar layer using stat=count.

Parameters
----------
x : str
    Column name mapped to the x-axis (categories to count).
fill : str, optional
    Bar fill color as a column name or fixed value.
color : str, optional
    Bar outline color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).
position : str, optional
    Position adjustment: ``"stack"``, ``"dodge"``, or ``"fill"``.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_bar
>>> df = pd.DataFrame({"fruit": ["apple", "banana", "apple", "cherry"]})
>>> p = ggplot(df, aes(x="fruit")) + geom_bar(fill="coral")
""",
)

geom_boxplot = _make_geom_factory(
    GeomBoxplot,
    """Create a box-and-whisker plot layer.

Parameters
----------
x : str
    Column name for the grouping variable.
y : str
    Column name for the continuous variable.
fill : str, optional
    Box fill color as a column name or fixed value.
color : str, optional
    Box outline color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_boxplot
>>> df = pd.DataFrame({"g": ["a", "a", "b", "b"], "v": [1, 3, 2, 5]})
>>> p = ggplot(df, aes(x="g", y="v")) + geom_boxplot(fill="lightblue")
""",
)

geom_text = _make_geom_factory(
    GeomText,
    """Create a text annotation layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
label : str
    Column name containing the text to display.
size : float, optional
    Font size in points.
color : str, optional
    Text color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).
angle : float, optional
    Rotation angle in degrees.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_text
>>> df = pd.DataFrame({"x": [1, 2], "y": [3, 4], "lbl": ["A", "B"]})
>>> p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_text(size=12)
""",
)

geom_label = _make_geom_factory(
    GeomLabel,
    """Create a text layer with a background box.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
label : str
    Column name containing the text to display.
fill : str, optional
    Background box fill color.
color : str, optional
    Text color as a column name or fixed value.
size : float, optional
    Font size in points.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_label
>>> df = pd.DataFrame({"x": [1, 2], "y": [3, 4], "lbl": ["A", "B"]})
>>> p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_label(fill="yellow")
""",
)

geom_area = _make_geom_factory(
    GeomArea,
    """Create a filled area layer under a line.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
fill : str, optional
    Area fill color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_area
>>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 3, 2]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_area(fill="skyblue", alpha=0.5)
""",
)

geom_ribbon = _make_geom_factory(
    GeomRibbon,
    """Create a filled band between ymin and ymax.

Parameters
----------
x : str
    Column name mapped to the x-axis.
ymin : str
    Column name for the lower bound.
ymax : str
    Column name for the upper bound.
fill : str, optional
    Ribbon fill color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_ribbon
>>> df = pd.DataFrame({"x": [1, 2, 3], "lo": [0, 1, 1], "hi": [2, 3, 4]})
>>> p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_ribbon(alpha=0.3)
""",
)

geom_tile = _make_geom_factory(
    GeomTile,
    """Create a rectangular tile layer for heatmaps.

Parameters
----------
x : str
    Column name mapped to the x-axis (tile center).
y : str
    Column name mapped to the y-axis (tile center).
fill : str, optional
    Tile fill color as a column name or fixed value.
color : str, optional
    Tile border color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_tile
>>> df = pd.DataFrame({"x": [1, 1, 2, 2], "y": [1, 2, 1, 2], "v": [1, 2, 3, 4]})
>>> p = ggplot(df, aes(x="x", y="y", fill="v")) + geom_tile()
""",
)

geom_errorbar = _make_geom_factory(
    GeomErrorbar,
    """Create a vertical error bar layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
ymin : str
    Column name for the lower error bound.
ymax : str
    Column name for the upper error bound.
color : str, optional
    Error bar color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_errorbar
>>> df = pd.DataFrame({"x": [1, 2], "lo": [0.8, 1.5], "hi": [1.2, 2.5]})
>>> p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_errorbar()
""",
)

geom_errorbarh = _make_geom_factory(
    GeomErrorbarH,
    """Create a horizontal error bar layer.

Parameters
----------
y : str
    Column name mapped to the y-axis.
xmin : str
    Column name for the left error bound.
xmax : str
    Column name for the right error bound.
color : str, optional
    Error bar color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_errorbarh
>>> df = pd.DataFrame({"y": [1, 2], "lo": [0.5, 1.0], "hi": [1.5, 2.0]})
>>> p = ggplot(df, aes(y="y", xmin="lo", xmax="hi")) + geom_errorbarh()
""",
)

geom_col = _make_geom_factory(
    GeomCol,
    """Create a bar layer with pre-computed heights.

Parameters
----------
x : str
    Column name mapped to the x-axis (categories).
y : str
    Column name mapped to the y-axis (bar heights).
fill : str, optional
    Bar fill color as a column name or fixed value.
color : str, optional
    Bar outline color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).
position : str, optional
    Position adjustment: ``"stack"``, ``"dodge"``, or ``"fill"``.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_col
>>> df = pd.DataFrame({"item": ["A", "B", "C"], "count": [10, 20, 15]})
>>> p = ggplot(df, aes(x="item", y="count")) + geom_col(fill="teal")
""",
)

geom_violin = _make_geom_factory(
    GeomViolin,
    """Create a violin plot layer.

Parameters
----------
x : str
    Column name for the grouping variable.
y : str
    Column name for the continuous variable.
fill : str, optional
    Violin fill color as a column name or fixed value.
color : str, optional
    Violin outline color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_violin
>>> df = pd.DataFrame({"g": ["a"]*4 + ["b"]*4, "v": [1, 2, 3, 4, 2, 3, 4, 5]})
>>> p = ggplot(df, aes(x="g", y="v")) + geom_violin(fill="plum")
""",
)

geom_segment = _make_geom_factory(
    GeomSegment,
    """Create a line segment layer.

Parameters
----------
x : str
    Column name for the segment start x-coordinate.
y : str
    Column name for the segment start y-coordinate.
xend : str
    Column name for the segment end x-coordinate.
yend : str
    Column name for the segment end y-coordinate.
color : str, optional
    Segment color as a column name or fixed value.
linetype : str, optional
    Line style such as ``"solid"``, ``"dashed"``, or ``"dotted"``.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_segment
>>> df = pd.DataFrame({"x": [0], "y": [0], "xend": [1], "yend": [1]})
>>> p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment()
""",
)

geom_rect = _make_geom_factory(
    GeomRect,
    """Create a rectangle layer from corner coordinates.

Parameters
----------
xmin : str
    Column name for the left edge.
xmax : str
    Column name for the right edge.
ymin : str
    Column name for the bottom edge.
ymax : str
    Column name for the top edge.
fill : str, optional
    Rectangle fill color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_rect
>>> df = pd.DataFrame({"x0": [0], "x1": [2], "y0": [0], "y1": [3]})
>>> p = ggplot(df, aes(xmin="x0", xmax="x1", ymin="y0", ymax="y1")) + geom_rect()
""",
)

geom_step = _make_geom_factory(
    GeomStep,
    """Create a step line layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
color : str, optional
    Step line color as a column name or fixed value.
linetype : str, optional
    Line style such as ``"solid"``, ``"dashed"``, or ``"dotted"``.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_step
>>> df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 3, 2, 4]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_step(color="darkgreen")
""",
)

geom_rug = _make_geom_factory(
    GeomRug,
    """Create a marginal rug mark layer.

Parameters
----------
x : str, optional
    Column name for rug marks on the x-axis.
y : str, optional
    Column name for rug marks on the y-axis.
color : str, optional
    Rug mark color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_rug
>>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_rug(alpha=0.5)
""",
)

geom_path = _make_geom_factory(
    GeomPath,
    """Create a path layer connecting points in data order.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
color : str, optional
    Path color as a column name or fixed value.
linetype : str, optional
    Line style such as ``"solid"``, ``"dashed"``, or ``"dotted"``.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_path
>>> df = pd.DataFrame({"x": [0, 1, 0.5], "y": [0, 1, 0.5]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_path(color="navy")
""",
)

geom_polygon = _make_geom_factory(
    GeomPolygon,
    """Create a filled polygon layer.

Parameters
----------
x : str
    Column name for polygon vertex x-coordinates.
y : str
    Column name for polygon vertex y-coordinates.
group : str, optional
    Column name that identifies separate polygons.
fill : str, optional
    Polygon fill color as a column name or fixed value.
color : str, optional
    Polygon outline color.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_polygon
>>> df = pd.DataFrame({"x": [0, 1, 0.5], "y": [0, 0, 1], "g": [1, 1, 1]})
>>> p = ggplot(df, aes(x="x", y="y", group="g")) + geom_polygon(fill="gold")
""",
)

geom_crossbar = _make_geom_factory(
    GeomCrossbar,
    """Create a crossbar layer (box with a middle line).

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name for the middle value.
ymin : str
    Column name for the lower extent.
ymax : str
    Column name for the upper extent.
fill : str, optional
    Crossbar fill color as a column name or fixed value.
color : str, optional
    Crossbar outline color.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_crossbar
>>> df = pd.DataFrame({"x": [1, 2], "y": [3, 5], "lo": [2, 4], "hi": [4, 6]})
>>> p = ggplot(df, aes(x="x", y="y", ymin="lo", ymax="hi")) + geom_crossbar()
""",
)

geom_pointrange = _make_geom_factory(
    GeomPointrange,
    """Create a point-with-vertical-range layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name for the point location.
ymin : str
    Column name for the lower range bound.
ymax : str
    Column name for the upper range bound.
color : str, optional
    Point and range color as a column name or fixed value.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_pointrange
>>> df = pd.DataFrame({"x": [1, 2], "y": [3, 5], "lo": [2, 4], "hi": [4, 6]})
>>> p = ggplot(df, aes(x="x", y="y", ymin="lo", ymax="hi")) + geom_pointrange()
""",
)

geom_linerange = _make_geom_factory(
    GeomLinerange,
    """Create a vertical line range layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
ymin : str
    Column name for the lower range bound.
ymax : str
    Column name for the upper range bound.
color : str, optional
    Line color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_linerange
>>> df = pd.DataFrame({"x": [1, 2], "lo": [2, 4], "hi": [4, 6]})
>>> p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_linerange()
""",
)

geom_hex = _make_geom_factory(
    GeomHex,
    """Create a hexagonal binning layer.

Parameters
----------
x : str
    Column name mapped to the x-axis.
y : str
    Column name mapped to the y-axis.
fill : str, optional
    Hex fill color as a column name or fixed value.
alpha : float, optional
    Opacity from 0 (transparent) to 1 (opaque).

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_hex
>>> df = pd.DataFrame({"x": [1, 2, 3, 1, 2], "y": [1, 2, 1, 2, 1]})
>>> p = ggplot(df, aes(x="x", y="y")) + geom_hex()
""",
)

geom_curve = _make_geom_factory(
    GeomCurve,
    """Create a curved line segment layer.

Parameters
----------
x : str
    Column name for the curve start x-coordinate.
y : str
    Column name for the curve start y-coordinate.
xend : str
    Column name for the curve end x-coordinate.
yend : str
    Column name for the curve end y-coordinate.
color : str, optional
    Curve color as a column name or fixed value.
curvature : float, optional
    Amount of curvature; positive curves right, negative curves left.

Examples
--------
>>> import pandas as pd
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_curve
>>> df = pd.DataFrame({"x": [0], "y": [0], "xend": [1], "yend": [1]})
>>> p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_curve()
""",
)

geom_spoke = _make_geom_factory(
    GeomSpoke,
    """Create a radial segment layer from angle and radius.

Parameters
----------
x : str
    Column name for the spoke origin x-coordinate.
y : str
    Column name for the spoke origin y-coordinate.
angle : str
    Column name for the spoke angle in radians.
radius : str
    Column name for the spoke length.
color : str, optional
    Spoke color as a column name or fixed value.

Examples
--------
>>> import pandas as pd
>>> import math
>>> from plotten import ggplot, aes
>>> from plotten.geoms import geom_spoke
>>> df = pd.DataFrame({"x": [0, 0], "y": [0, 0], "a": [0, math.pi / 2], "r": [1, 1]})
>>> p = ggplot(df, aes(x="x", y="y", angle="a", radius="r")) + geom_spoke()
""",
)
