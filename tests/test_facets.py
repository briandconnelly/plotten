import os
import tempfile

import polars as pl
import pandas as pd

from plotten import ggplot, aes, geom_point, facet_wrap, facet_grid
from plotten.facets import FacetWrap, FacetGrid


def _make_df():
    return pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )


def _save_and_check(p):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_facet_wrap_data_splitting():
    df = _make_df()
    fw = FacetWrap(facets="g")
    panels = fw.facet_data(df)
    assert len(panels) == 3
    labels = [p[0] for p in panels]
    assert labels == ["a", "b", "c"]
    # Each subset has 2 rows
    for _, subset in panels:
        assert len(subset) == 2


def test_facet_wrap_layout():
    fw = FacetWrap(facets="g")
    assert fw.layout(3) == (2, 2)  # ceil(sqrt(3))=2, ceil(3/2)=2
    assert fw.layout(4) == (2, 2)
    assert fw.layout(1) == (1, 1)

    fw2 = FacetWrap(facets="g", ncol=3)
    assert fw2.layout(6) == (2, 3)

    fw3 = FacetWrap(facets="g", nrow=2, ncol=3)
    assert fw3.layout(6) == (2, 3)


def test_facet_grid_data_splitting():
    df = _make_df()
    fg = FacetGrid(cols="g")
    panels = fg.facet_data(df)
    assert len(panels) == 3


def test_facet_grid_layout_cols_only():
    fg = FacetGrid(cols="g")
    assert fg.layout(3) == (1, 3)


def test_facet_grid_layout_rows_only():
    fg = FacetGrid(rows="g")
    assert fg.layout(3) == (3, 1)


def test_facet_wrap_render_polars():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g")
    _save_and_check(p)


def test_facet_wrap_render_pandas():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g")
    _save_and_check(p)


def test_facet_grid_render():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(cols="g")
    _save_and_check(p)


def test_facet_grid_rows_and_cols():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6, 7, 8],
            "y": [2, 4, 1, 5, 3, 6, 2, 4],
            "r": ["r1", "r1", "r1", "r1", "r2", "r2", "r2", "r2"],
            "c": ["c1", "c1", "c2", "c2", "c1", "c1", "c2", "c2"],
        }
    )
    fg = FacetGrid(rows="r", cols="c")
    panels = fg.facet_data(df)
    assert len(panels) == 4
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(rows="r", cols="c")
    _save_and_check(p)


def test_facet_grid_rows_only_render():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(rows="g")
    _save_and_check(p)


def test_facet_wrap_free_x():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", scales="free_x")
    _save_and_check(p)


def test_facet_wrap_free_y():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", scales="free_y")
    _save_and_check(p)


def test_facet_wrap_free():
    df = _make_df()
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", scales="free")
    _save_and_check(p)


def test_facet_wrap_nrow_layout():
    fw = FacetWrap(facets="g", nrow=1)
    assert fw.layout(3) == (1, 3)
