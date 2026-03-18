import os
import tempfile

import polars as pl

from plotten import aes, geom_abline, geom_hline, geom_point, geom_vline, ggplot
from plotten.facets import FacetWrap


def _save_and_check(p):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_geom_hline():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_hline(yintercept=2.0)
    _save_and_check(p)


def test_geom_vline():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_vline(xintercept=2.0)
    _save_and_check(p)


def test_geom_abline():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_abline(slope=1.0, intercept=0.0)
    _save_and_check(p)


def test_refline_with_data_geom():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + geom_hline(yintercept=3.0)
        + geom_vline(xintercept=2.5)
    )
    _save_and_check(p)


def test_refline_in_faceted_plot():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + geom_hline(yintercept=3.5)
        + FacetWrap(facets="g")
    )
    _save_and_check(p)


def test_refline_style_params():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + geom_hline(yintercept=2.0, color="red", linestyle="--", linewidth=2, alpha=0.5)
    )
    _save_and_check(p)
