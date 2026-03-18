import polars as pl

from plotten.scales import (
    ScaleContinuous,
    ScaleDiscrete,
    ScaleColorContinuous,
    ScaleColorDiscrete,
    auto_scale,
)


def test_continuous_train_and_limits():
    s = ScaleContinuous("x")
    series = pl.Series("x", [1.0, 5.0, 10.0])
    s.train(series)
    lo, hi = s.get_limits()
    assert lo < 1.0  # padded
    assert hi > 10.0  # padded


def test_continuous_breaks():
    s = ScaleContinuous("y")
    series = pl.Series("y", [0.0, 100.0])
    s.train(series)
    breaks = s.get_breaks()
    assert len(breaks) == 6


def test_discrete_train_and_map():
    s = ScaleDiscrete("x")
    series = pl.Series("x", ["b", "a", "c", "a"])
    s.train(series)
    assert s._levels == ["a", "b", "c"]
    mapped = s.map_data(pl.Series("x", ["c", "a"]))
    assert mapped == [2, 0]


def test_discrete_labels():
    s = ScaleDiscrete("x")
    s.train(pl.Series("x", ["cat", "dog"]))
    assert s.get_labels() == ["cat", "dog"]


def test_color_continuous():
    s = ScaleColorContinuous()
    series = pl.Series("v", [0.0, 0.5, 1.0])
    s.train(series)
    colors = s.map_data(series)
    assert len(colors) == 3
    assert all(c.startswith("#") for c in colors)


def test_color_discrete():
    s = ScaleColorDiscrete()
    series = pl.Series("g", ["a", "b", "c"])
    s.train(series)
    colors = s.map_data(series)
    assert len(colors) == 3
    assert all(c.startswith("#") for c in colors)


def test_auto_scale_numeric():
    series = pl.Series("x", [1, 2, 3])
    s = auto_scale("x", series)
    assert isinstance(s, ScaleContinuous)


def test_auto_scale_string():
    series = pl.Series("x", ["a", "b"])
    s = auto_scale("x", series)
    assert isinstance(s, ScaleDiscrete)


def test_auto_scale_color_numeric():
    series = pl.Series("color", [1.0, 2.0])
    s = auto_scale("color", series)
    assert isinstance(s, ScaleColorContinuous)


def test_auto_scale_color_string():
    series = pl.Series("color", ["a", "b"])
    s = auto_scale("color", series)
    assert isinstance(s, ScaleColorDiscrete)
