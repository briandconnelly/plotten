from plotten._protocols import Stat, Geom, Scale, Coord
from plotten.geoms._point import GeomPoint
from plotten.stats._identity import StatIdentity
from plotten.scales._position import ScaleContinuous
from plotten.coords._cartesian import CoordCartesian


def test_stat_protocol():
    assert isinstance(StatIdentity(), Stat)


def test_geom_protocol():
    assert isinstance(GeomPoint(), Geom)


def test_scale_protocol():
    assert isinstance(ScaleContinuous("x"), Scale)


def test_coord_protocol():
    assert isinstance(CoordCartesian(), Coord)
