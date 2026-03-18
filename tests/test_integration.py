import os
import tempfile

import pandas as pd
import polars as pl

from plotten import (
    aes,
    coord_flip,
    facet_wrap,
    geom_bar,
    geom_line,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    scale_y_log10,
    theme_minimal,
)


def test_scatter_polars():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 1, 5, 3],
            "g": ["a", "b", "a", "b", "a"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point(size=5) + theme_minimal()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_scatter_pandas():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 1, 5, 3],
            "g": ["a", "b", "a", "b", "a"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + theme_minimal()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_line_plot():
    df = pl.DataFrame({"x": [1, 2, 3, 4], "y": [1, 4, 2, 3]})
    p = ggplot(df, aes(x="x", y="y")) + geom_line()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_bar_plot():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    p = ggplot(df, aes(x="x")) + geom_bar()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_faceted_scatter():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_smooth_with_ci():
    df = pl.DataFrame(
        {
            "x": list(range(20)),
            "y": [float(i) + (i % 3) for i in range(20)],
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_smooth(method="ols")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_coord_flip_bar():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    p = ggplot(df, aes(x="x")) + geom_bar() + coord_flip()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_log_scale():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 100, 1000, 10000, 100000]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_log10()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_multi_layer_composition():
    df = pl.DataFrame(
        {
            "x": list(range(20)),
            "y": [float(i) + (i % 3) for i in range(20)],
        }
    )
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + geom_smooth(method="ols")
        + labs(title="Multi-layer", x="X", y="Y")
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_repr_png():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point()
    png_bytes = p._repr_png_()
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0
    # PNG magic bytes
    assert png_bytes[:4] == b"\x89PNG"
