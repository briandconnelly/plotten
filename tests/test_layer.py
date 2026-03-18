from plotten._aes import Aes, aes
from plotten._layer import Layer
from plotten.geoms._point import GeomPoint
from plotten.stats._identity import StatIdentity


def test_layer_construction():
    layer = Layer(geom=GeomPoint(), mapping=aes(x="a", y="b"))
    assert layer.geom is not None
    assert layer.mapping.x == "a"
    assert layer.stat is None
    assert layer.data is None


def test_layer_with_stat():
    layer = Layer(geom=GeomPoint(), stat=StatIdentity(), mapping=Aes())
    assert isinstance(layer.stat, StatIdentity)


def test_layer_frozen():
    layer = Layer(geom=GeomPoint())
    try:
        layer.geom = None  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass
