from plotten._protocols import Coord, Geom, Scale, Stat
from plotten.coords._cartesian import CoordCartesian
from plotten.geoms._point import GeomPoint
from plotten.scales._position import ScaleContinuous
from plotten.stats._identity import StatIdentity


def test_stat_protocol():
    assert isinstance(StatIdentity(), Stat)


def test_geom_protocol():
    assert isinstance(GeomPoint(), Geom)


def test_scale_protocol():
    assert isinstance(ScaleContinuous("x"), Scale)


def test_coord_protocol():
    assert isinstance(CoordCartesian(), Coord)
