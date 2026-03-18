from plotten.geoms._point import GeomPoint
from plotten.geoms._line import GeomLine
from plotten.geoms._bar import GeomBar
from plotten.stats._identity import StatIdentity
from plotten.stats._count import StatCount


def test_geom_point_required_aes():
    g = GeomPoint()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_line_required_aes():
    g = GeomLine()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_bar_required_aes():
    g = GeomBar()
    assert g.required_aes == frozenset({"x"})
    assert isinstance(g.default_stat(), StatCount)
