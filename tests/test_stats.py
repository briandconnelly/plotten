import polars as pl
import narwhals as nw

from plotten.stats import StatIdentity, StatCount, StatBin


def test_stat_identity():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    result = StatIdentity().compute(df)
    assert nw.from_native(result).shape == (3, 2)


def test_stat_count():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    result = nw.from_native(StatCount().compute(df))
    assert set(result.columns) == {"x", "y"}
    # a=3, b=2, c=1
    rows = {r["x"]: r["y"] for r in result.iter_rows(named=True)}
    assert rows["a"] == 3
    assert rows["b"] == 2
    assert rows["c"] == 1


def test_stat_bin():
    df = pl.DataFrame({"x": list(range(100))})
    result = nw.from_native(StatBin(bins=10).compute(df))
    assert "x" in result.columns
    assert "y" in result.columns
    assert result.shape[0] == 10
