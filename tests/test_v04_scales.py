import os
import tempfile

import polars as pl

from plotten import aes, geom_point, ggplot
from plotten.scales import (
    ScaleColorContinuous,
    ScaleColorDiscrete,
    ScaleContinuous,
    ScaleDiscrete,
    scale_color_manual,
    scale_fill_manual,
    scale_x_continuous,
    scale_x_discrete,
    scale_y_continuous,
    scale_y_discrete,
)


def test_continuous_manual_breaks():
    s = ScaleContinuous("x", breaks=[0, 5, 10])
    s.train(pl.Series("x", [0.0, 10.0]))
    assert s.get_breaks() == [0, 5, 10]


def test_continuous_manual_limits():
    s = ScaleContinuous("x", limits=(0, 100))
    s.train(pl.Series("x", [10.0, 20.0]))
    assert s.get_limits() == (0, 100)


def test_continuous_manual_labels():
    s = ScaleContinuous("x", breaks=[0, 5, 10], labels=["low", "mid", "high"])
    s.train(pl.Series("x", [0.0, 10.0]))
    assert s.get_labels() == ["low", "mid", "high"]


def test_continuous_default_labels_from_breaks():
    s = ScaleContinuous("x", breaks=[1, 2, 3])
    s.train(pl.Series("x", [1.0, 3.0]))
    assert s.get_labels() == ["1", "2", "3"]


def test_discrete_manual_labels_dict():
    s = ScaleDiscrete("x", labels={"a": "Alpha", "b": "Beta"})
    s.train(pl.Series("x", ["a", "b"]))
    assert s.get_labels() == ["Alpha", "Beta"]


def test_discrete_manual_labels_list():
    s = ScaleDiscrete("x", labels=["Cat", "Dog"])
    s.train(pl.Series("x", ["a", "b"]))
    assert s.get_labels() == ["Cat", "Dog"]


def test_color_discrete_manual_palette():
    s = ScaleColorDiscrete(values={"a": "#ff0000", "b": "#0000ff"})
    s.train(pl.Series("g", ["a", "b"]))
    colors = s.map_data(pl.Series("g", ["a", "b", "a"]))
    assert colors == ["#ff0000", "#0000ff", "#ff0000"]


def test_color_discrete_manual_legend_entries():
    s = ScaleColorDiscrete(values={"a": "#ff0000", "b": "#0000ff"})
    s.train(pl.Series("g", ["a", "b"]))
    entries = s.legend_entries()
    assert len(entries) == 2
    assert entries[0].color == "#ff0000"
    assert entries[1].color == "#0000ff"


def test_color_discrete_manual_fallback():
    s = ScaleColorDiscrete(values={"a": "#ff0000"})
    s.train(pl.Series("g", ["a", "b"]))
    colors = s.map_data(pl.Series("g", ["a", "b"]))
    assert colors[0] == "#ff0000"
    assert colors[1] == "#000000"  # fallback


def test_color_continuous_manual_breaks():
    s = ScaleColorContinuous(breaks=[0, 50, 100])
    s.train(pl.Series("v", [0.0, 100.0]))
    assert s.get_breaks() == [0, 50, 100]


def test_color_continuous_manual_limits():
    s = ScaleColorContinuous(limits=(0, 200))
    s.train(pl.Series("v", [10.0, 50.0]))
    assert s.get_limits() == (0, 200)


def test_scale_x_continuous_convenience():
    s = scale_x_continuous(breaks=[1, 2, 3], limits=(0, 4))
    assert s.aesthetic == "x"
    assert s._breaks == [1, 2, 3]
    assert s._limits == (0, 4)


def test_scale_y_continuous_convenience():
    s = scale_y_continuous(breaks=[10, 20])
    assert s.aesthetic == "y"
    assert s._breaks == [10, 20]


def test_scale_x_discrete_convenience():
    s = scale_x_discrete(labels={"a": "Alpha"})
    assert s.aesthetic == "x"


def test_scale_y_discrete_convenience():
    s = scale_y_discrete()
    assert s.aesthetic == "y"


def test_scale_color_manual_convenience():
    s = scale_color_manual(values={"a": "red", "b": "blue"})
    assert s.aesthetic == "color"
    assert s._manual_values == {"a": "red", "b": "blue"}


def test_scale_fill_manual_convenience():
    s = scale_fill_manual(values={"x": "#123456"})
    assert s.aesthetic == "fill"


def test_render_with_manual_breaks():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + scale_x_continuous(breaks=[1, 3, 5], limits=(0, 6))
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_render_with_color_manual():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [2, 4, 1, 5],
            "g": ["a", "b", "a", "b"],
        }
    )
    p = (
        ggplot(df, aes(x="x", y="y", color="g"))
        + geom_point()
        + scale_color_manual(values={"a": "red", "b": "blue"})
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
