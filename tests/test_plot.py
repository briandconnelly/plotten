from plotten._aes import aes
from plotten._layer import Layer
from plotten._plot import Plot, ggplot
from plotten.geoms._point import GeomPoint
from plotten.scales._position import ScaleContinuous
from plotten.themes import theme_minimal


def test_ggplot_returns_plot():
    p = ggplot()
    assert isinstance(p, Plot)


def test_ggplot_with_data_and_mapping():
    p = ggplot(data=[1, 2, 3], mapping=aes(x="a"))
    assert p.data == [1, 2, 3]
    assert p.mapping.x == "a"


def test_add_layer():
    p = ggplot()
    layer = Layer(geom=GeomPoint(), mapping=aes(x="x", y="y"))
    p2 = p + layer
    assert len(p2.layers) == 1
    assert len(p.layers) == 0  # immutable


def test_add_scale():
    p = ggplot()
    s = ScaleContinuous("x")
    p2 = p + s
    assert len(p2.scales) == 1
    assert len(p.scales) == 0


def test_add_theme():
    p = ggplot()
    p2 = p + theme_minimal()
    assert p2.theme.panel_background == "none"
    assert p.theme.panel_background == "#ebebeb"


def test_add_unsupported_raises_type_error():
    import pytest

    p = ggplot()
    with pytest.raises(TypeError):
        p + 42


def test_add_preserves_immutability():
    p1 = ggplot(mapping=aes(x="a"))
    layer = Layer(geom=GeomPoint())
    p2 = p1 + layer
    p3 = p2 + theme_minimal()
    # Each is distinct
    assert len(p1.layers) == 0
    assert len(p2.layers) == 1
    assert p3.theme.panel_background == "none"
    assert p2.theme.panel_background == "#ebebeb"
