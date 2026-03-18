import os
import tempfile

import pandas as pd
import polars as pl
import pytest

from plotten import (
    aes,
    geom_area,
    geom_col,
    geom_density,
    geom_errorbar,
    geom_hline,
    geom_point,
    geom_ribbon,
    geom_tile,
    geom_violin,
    ggplot,
)


@pytest.fixture(params=["polars", "pandas"])
def backend(request):
    return request.param


def make_df(data: dict, backend: str):
    if backend == "polars":
        return pl.DataFrame(data)
    return pd.DataFrame(data)


def assert_renders(plot):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        plot.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_geom_area(backend):
    df = make_df({"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 5, 1]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_area()
    assert_renders(p)


def test_geom_ribbon(backend):
    df = make_df(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "lo": [1.0, 2.0, 1.5, 3.0, 0.5],
            "hi": [3.0, 5.0, 4.0, 6.0, 2.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_ribbon()
    assert_renders(p)


def test_geom_tile_plain(backend):
    df = make_df(
        {"x": [0, 1, 0, 1], "y": [0, 0, 1, 1], "val": [1.0, 2.0, 3.0, 4.0]},
        backend,
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_tile(fill="steelblue")
    assert_renders(p)


def test_geom_tile_with_labels(backend):
    df = make_df(
        {
            "x": [0, 1, 0, 1],
            "y": [0, 0, 1, 1],
            "lbl": ["A", "B", "C", "D"],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_tile(fill="lightblue")
    assert_renders(p)


def test_geom_errorbar(backend):
    df = make_df(
        {
            "x": [1, 2, 3],
            "lo": [0.5, 1.5, 2.0],
            "hi": [1.5, 3.0, 4.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_errorbar()
    assert_renders(p)


def test_geom_col(backend):
    df = make_df({"x": ["a", "b", "c"], "y": [10, 20, 15]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_col()
    assert_renders(p)


def test_geom_density_single():
    pytest.importorskip("scipy")
    df = pl.DataFrame({"x": [float(i) for i in range(50)]})
    p = ggplot(df, aes(x="x")) + geom_density()
    assert_renders(p)


def test_geom_density_grouped():
    pytest.importorskip("scipy")
    df = pl.DataFrame(
        {
            "x": [float(i) for i in range(40)],
            "g": ["a"] * 20 + ["b"] * 20,
        }
    )
    p = ggplot(df, aes(x="x", color="g")) + geom_density()
    assert_renders(p)


def test_geom_density_pandas():
    pytest.importorskip("scipy")
    df = pd.DataFrame({"x": [float(i) for i in range(50)]})
    p = ggplot(df, aes(x="x")) + geom_density()
    assert_renders(p)


def test_geom_violin():
    pytest.importorskip("scipy")
    import numpy as np

    rng = np.random.default_rng(42)
    df = pl.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_violin()
    assert_renders(p)


def test_geom_violin_pandas():
    pytest.importorskip("scipy")
    import numpy as np

    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_violin()
    assert_renders(p)


def test_errorbar_with_points(backend):
    df = make_df(
        {
            "x": [1, 2, 3],
            "y": [1.0, 2.5, 3.0],
            "lo": [0.5, 1.5, 2.0],
            "hi": [1.5, 3.0, 4.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_errorbar(ymin="lo", ymax="hi")
    assert_renders(p)


def test_area_with_refline(backend):
    df = make_df({"x": [1, 2, 3, 4], "y": [2, 4, 3, 5]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_area() + geom_hline(yintercept=3)
    assert_renders(p)
