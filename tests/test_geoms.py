from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._col import GeomCol
from plotten.geoms._density import GeomDensity
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._tile import GeomTile
from plotten.geoms._violin import GeomViolin
from plotten.stats._count import StatCount
from plotten.stats._identity import StatIdentity


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


def test_geom_area_required_aes():
    g = GeomArea()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_ribbon_required_aes():
    g = GeomRibbon()
    assert g.required_aes == frozenset({"x", "ymin", "ymax"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_tile_required_aes():
    g = GeomTile()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_errorbar_required_aes():
    g = GeomErrorbar()
    assert g.required_aes == frozenset({"x", "ymin", "ymax"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_col_required_aes():
    g = GeomCol()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_density_required_aes():
    g = GeomDensity()
    assert g.required_aes == frozenset({"x"})
    from plotten.stats._density import StatDensity

    assert isinstance(g.default_stat(), StatDensity)


def test_geom_violin_required_aes():
    g = GeomViolin()
    assert g.required_aes == frozenset({"x", "y"})
    from plotten.stats._violin import StatViolin

    assert isinstance(g.default_stat(), StatViolin)
