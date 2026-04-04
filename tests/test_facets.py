import os
import tempfile

import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pytest

from plotten import (
    Aes,
    aes,
    facet_grid,
    facet_wrap,
    geom_point,
    ggplot,
    label_value,
    labeller_both,
    labeller_wrap,
    labs,
)
from plotten._render._mpl import render
from plotten.facets import FacetGrid, FacetWrap

# --- from test_facets.py ---


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

    fw2 = FacetWrap(facets="g", n_cols=3)
    assert fw2.layout(6) == (2, 3)

    fw3 = FacetWrap(facets="g", n_rows=2, n_cols=3)
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


def test_facet_wrap_n_rows_layout():
    fw = FacetWrap(facets="g", n_rows=1)
    assert fw.layout(3) == (1, 3)


# --- from test_v10_facet_labels.py ---

"""Tests for smart facet axis labels (1B)."""


def test_facet_shared_edge_labels():
    """Bottom row gets x-labels, left column gets y-labels, interiors suppressed."""
    df = pl.DataFrame(
        {
            "x": list(range(24)),
            "y": list(range(24)),
            "g": [f"panel_{i // 8}" for i in range(24)],
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + facet_wrap("g", n_cols=2)
        + labs(x="X Axis", y="Y Axis")
    )
    fig = render(plot)

    # At minimum, the figure should render without error
    assert len(fig.get_axes()) >= 2
    plt.close(fig)


def test_facet_single_row():
    """Single row: all panels are bottom row, only left gets y-label."""
    df = pl.DataFrame(
        {
            "x": list(range(6)),
            "y": list(range(6)),
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + facet_wrap("g", n_cols=3)
        + labs(x="X", y="Y")
    )
    fig = render(plot)
    assert len(fig.get_axes()) >= 3
    plt.close(fig)


# --- from test_v13_facets.py ---

"""Tests for v0.13.0 facet enhancements."""


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 3, 5, 2],
            "group": ["A", "A", "B", "B", "C", "C"],
        }
    )


class TestCustomLabeller:
    def test_labeller_both(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=labeller_both("group"))
        )
        fig = render(p)
        assert fig is not None

    def test_labeller_wrap(self, sample_df):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 2, 3, 4],
                "cat": [
                    "Very Long Category Name",
                    "Very Long Category Name",
                    "Another Long Name Here",
                    "Another Long Name Here",
                ],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("cat", labeller=labeller_wrap(12))
        )
        fig = render(p)
        assert fig is not None

    def test_custom_lambda_labeller(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=lambda v: f"Group {v}")
        )
        fig = render(p)
        assert fig is not None

    def test_label_value_default(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=label_value)
        )
        fig = render(p)
        assert fig is not None

    def test_labeller_on_facet_grid(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_grid(cols="group", labeller=labeller_both("group"))
        )
        fig = render(p)
        assert fig is not None


class TestStripPosition:
    def test_strip_bottom(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", strip_position="bottom")
        )
        fig = render(p)
        assert fig is not None

    def test_strip_top_default(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group")
        fig = render(p)
        assert fig is not None


class TestDropParameter:
    def test_drop_true_default(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group", drop=True)
        fig = render(p)
        assert fig is not None

    def test_drop_false(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group", drop=False)
        fig = render(p)
        assert fig is not None
