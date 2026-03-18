import narwhals as nw
import polars as pl
import pytest

from plotten.stats import StatBin, StatCount, StatIdentity
from plotten.stats._smooth import StatSmooth


def test_stat_identity():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    result = StatIdentity().compute(df)
    assert nw.from_native(result).shape == (3, 2)


def test_stat_count():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    result = nw.from_native(StatCount().compute(df))
    assert {"x", "y", "count", "prop"}.issubset(set(result.columns))
    # a=3, b=2, c=1
    rows = {r["x"]: r["y"] for r in result.iter_rows(named=True)}
    assert rows["a"] == 3
    assert rows["b"] == 2
    assert rows["c"] == 1
    # Verify count matches y and prop sums to 1
    prop_rows = {r["x"]: r["prop"] for r in result.iter_rows(named=True)}
    assert sum(prop_rows.values()) == pytest.approx(1.0)


def test_stat_bin():
    df = pl.DataFrame({"x": list(range(100))})
    result = nw.from_native(StatBin(bins=10).compute(df))
    assert "x" in result.columns
    assert "y" in result.columns
    assert result.shape[0] == 10


def test_stat_smooth_loess():
    pytest.importorskip("scipy")
    df = pl.DataFrame({"x": list(range(20)), "y": [float(i % 5) for i in range(20)]})
    stat = StatSmooth(method="loess", se=True, n_points=10)
    result = nw.from_native(stat.compute(df))
    assert result.shape[0] == 10
    assert set(result.columns) >= {"x", "y", "ymin", "ymax"}


def test_stat_smooth_moving_average():
    df = pl.DataFrame({"x": list(range(20)), "y": [float(i) for i in range(20)]})
    stat = StatSmooth(method="moving_average", se=False, n_points=10)
    result = nw.from_native(stat.compute(df))
    assert result.shape[0] == 10
    assert set(result.columns) >= {"x", "y"}


def test_stat_smooth_unknown_method():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    stat = StatSmooth(method="nonexistent")
    with pytest.raises(ValueError, match="Unknown smoothing method"):
        stat.compute(df)
