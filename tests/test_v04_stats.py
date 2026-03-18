import narwhals as nw
import polars as pl
import pytest


def test_stat_density_basic():
    pytest.importorskip("scipy")
    from plotten.stats._density import StatDensity

    df = pl.DataFrame({"x": [float(i) for i in range(50)]})
    stat = StatDensity(n_points=100)
    result = nw.from_native(stat.compute(df))
    assert set(result.columns) == {"x", "y"}
    assert len(result) == 100


def test_stat_density_grouped():
    pytest.importorskip("scipy")
    from plotten.stats._density import StatDensity

    df = pl.DataFrame(
        {
            "x": [float(i) for i in range(40)],
            "color": ["a"] * 20 + ["b"] * 20,
        }
    )
    stat = StatDensity(n_points=50)
    result = nw.from_native(stat.compute(df))
    assert "color" in result.columns
    # 2 groups * 50 points each = 100 rows
    assert len(result) == 100


def test_stat_density_pandas():
    pytest.importorskip("scipy")
    import pandas as pd

    from plotten.stats._density import StatDensity

    df = pd.DataFrame({"x": [float(i) for i in range(30)]})
    stat = StatDensity(n_points=50)
    result = stat.compute(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 50


def test_stat_violin_basic():
    pytest.importorskip("scipy")
    import numpy as np

    from plotten.stats._violin import StatViolin

    rng = np.random.default_rng(42)
    df = pl.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    stat = StatViolin(n_points=50)
    result = nw.from_native(stat.compute(df))
    assert set(result.columns) == {"x", "y_grid", "density", "y_min", "y_max"}
    # One row per x group
    assert len(result) == 2


def test_stat_violin_pandas():
    pytest.importorskip("scipy")
    import numpy as np
    import pandas as pd

    from plotten.stats._violin import StatViolin

    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    stat = StatViolin(n_points=50)
    result = stat.compute(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
