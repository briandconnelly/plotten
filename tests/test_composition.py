from __future__ import annotations

import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import (
    Aes,
    Plot,
    PlotGrid,
    aes,
    geom_point,
    ggplot,
    inset_element,
    labs,
    plot_annotation,
    plot_grid,
)
from plotten._composition import _flatten_leaves, _tag_label, render_grid
from plotten._render._mpl import render

# --- from test_v07_composition.py ---

"""Tests for v0.7.0 plot composition: PlotGrid, operators, plot_grid, annotations."""


@pytest.fixture
def p1():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    return ggplot(df, aes(x="x", y="y")) + geom_point()


@pytest.fixture
def p2():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [6, 5, 4]})
    return ggplot(df, aes(x="x", y="y")) + geom_point()


@pytest.fixture
def p3():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 3, 2]})
    return ggplot(df, aes(x="x", y="y")) + geom_point()


# --- Operators ---


class TestPlotOperators:
    def test_pipe_operator(self, p1, p2):
        grid = p1 | p2
        assert isinstance(grid, PlotGrid)
        assert grid.direction == "h"
        assert len(grid.plots) == 2

    def test_div_operator(self, p1, p2):
        grid = p1 / p2
        assert isinstance(grid, PlotGrid)
        assert grid.direction == "v"
        assert len(grid.plots) == 2

    def test_nested_operators(self, p1, p2, p3):
        grid = (p1 | p2) / p3
        assert isinstance(grid, PlotGrid)
        assert grid.direction == "v"
        assert isinstance(grid.plots[0], PlotGrid)
        assert grid.plots[0].direction == "h"

    def test_pipe_with_plotgrid(self, p1, p2, p3):
        grid = (p1 | p2) | p3
        assert isinstance(grid, PlotGrid)
        assert grid.direction == "h"

    def test_div_with_plotgrid(self, p1, p2, p3):
        grid = (p1 / p2) / p3
        assert isinstance(grid, PlotGrid)
        assert grid.direction == "v"

    def test_pipe_returns_notimplemented(self, p1):
        assert p1.__or__(42) is NotImplemented

    def test_div_returns_notimplemented(self, p1):
        assert p1.__truediv__(42) is NotImplemented

    def test_plotgrid_pipe_returns_notimplemented(self, p1, p2):
        grid = p1 | p2
        assert grid.__or__(42) is NotImplemented

    def test_plotgrid_div_returns_notimplemented(self, p1, p2):
        grid = p1 | p2
        assert grid.__truediv__(42) is NotImplemented


# --- PlotAnnotation ---


class TestPlotAnnotation:
    def test_annotation_creation(self):
        ann = plot_annotation(title="My Title", subtitle="Sub", caption="Cap")
        assert ann.title == "My Title"
        assert ann.subtitle == "Sub"
        assert ann.caption == "Cap"

    def test_annotation_add_to_grid(self, p1, p2):
        ann = plot_annotation(title="Test")
        grid = (p1 | p2) + ann
        assert grid.annotation is ann

    def test_grid_add_non_annotation_returns_notimplemented(self, p1, p2):
        grid = p1 | p2
        assert grid.__add__(42) is NotImplemented


# --- plot_grid ---


class TestPlotGrid:
    def test_plot_grid_ncol(self, p1, p2, p3):
        grid = plot_grid(p1, p2, p3, ncol=2)
        assert isinstance(grid, PlotGrid)

    def test_plot_grid_nrow(self, p1, p2, p3):
        grid = plot_grid(p1, p2, p3, nrow=1)
        assert isinstance(grid, PlotGrid)

    def test_plot_grid_single(self, p1):
        grid = plot_grid(p1)
        assert isinstance(grid, PlotGrid)

    def test_plot_grid_empty(self):
        grid = plot_grid()
        assert isinstance(grid, PlotGrid)
        assert len(grid.plots) == 0

    def test_plot_grid_default_ncol(self, p1, p2):
        grid = plot_grid(p1, p2)
        assert isinstance(grid, PlotGrid)

    def test_plot_grid_with_widths(self, p1, p2):
        grid = plot_grid(p1, p2, ncol=2, widths=[2.0, 1.0])
        assert isinstance(grid, PlotGrid)


# --- Rendering ---


class TestGridRendering:
    def test_render_horizontal(self, p1, p2):
        grid = p1 | p2
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_vertical(self, p1, p2):
        grid = p1 / p2
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_nested(self, p1, p2, p3):
        grid = (p1 | p2) / p3
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_plot_grid(self, p1, p2, p3):
        grid = plot_grid(p1, p2, p3, ncol=2)
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_with_annotation(self, p1, p2):
        ann = plot_annotation(title="Title", subtitle="Sub", caption="Cap")
        grid = (p1 | p2) + ann
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_with_tag_levels(self, p1, p2):
        ann = plot_annotation(tag_levels="A")
        grid = (p1 | p2) + ann
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_with_labs(self, p1, p2):
        grid = (p1 + labs(title="P1", x="X", y="Y")) | (p2 + labs(title="P2"))
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)


# --- Helper functions ---


class TestHelpers:
    def test_flatten_leaves(self, p1, p2, p3):
        grid = (p1 | p2) / p3
        leaves = _flatten_leaves(grid)
        assert len(leaves) == 3
        assert all(isinstance(leaf, Plot) for leaf in leaves)

    def test_flatten_single(self, p1):
        leaves = _flatten_leaves(p1)
        assert len(leaves) == 1

    def test_tag_labels(self):
        assert _tag_label(0, "A") == "A"
        assert _tag_label(1, "A") == "B"
        assert _tag_label(0, "a") == "a"
        assert _tag_label(0, "1") == "1"
        assert _tag_label(2, "1") == "3"
        assert _tag_label(0, "i") == "i"
        assert _tag_label(3, "i") == "iv"
        # Default fallback
        assert _tag_label(0, "X") == "A"


# --- PlotGrid methods ---


class TestPlotGridMethods:
    def test_show(self, p1, p2, monkeypatch):
        monkeypatch.setattr(plt, "show", lambda *a, **kw: None)
        grid = p1 | p2
        grid.show()

    def test_save(self, p1, p2, tmp_path):
        grid = p1 | p2
        path = str(tmp_path / "grid.png")
        grid.save(path)
        import os

        assert os.path.exists(path)

    def test_save_with_size(self, p1, p2, tmp_path):
        grid = p1 | p2
        path = str(tmp_path / "grid_sized.png")
        grid.save(path, width=10, height=5)

        assert os.path.exists(path)

    def test_repr_png(self, p1, p2):
        grid = p1 | p2
        png = grid._repr_png_()
        assert isinstance(png, bytes)
        assert len(png) > 0

    def test_replace(self, p1, p2):
        grid = p1 | p2
        new_grid = grid._replace(direction="v")
        assert new_grid.direction == "v"
        assert grid.direction == "h"  # original unchanged


class TestPlotGridWidths:
    def test_horizontal_with_widths(self, p1, p2):
        grid = PlotGrid(plots=(p1, p2), direction="h", widths=(2.0, 1.0))
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)

    def test_render_empty_grid(self):
        grid = PlotGrid()
        fig = render_grid(grid)
        assert fig is not None
        plt.close(fig)


# --- from test_v13_composition.py ---

"""Tests for v0.13.0 composition features."""


class TestInsetElement:
    def test_inset_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        inset = ggplot(df, Aes(x="x", y="y")) + geom_point(color="red")
        p = main + inset_element(inset, left=0.6, bottom=0.6, width=0.3, height=0.3)
        fig = render(p)
        # Should have at least 2 axes (main + inset)
        assert len(fig.get_axes()) >= 2

    def test_inset_custom_position(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        inset = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p = main + inset_element(inset, left=0.1, bottom=0.1, width=0.4, height=0.4)
        fig = render(p)
        assert fig is not None

    def test_multiple_insets(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p = (
            main
            + inset_element(ggplot(df, Aes(x="x", y="y")) + geom_point(), left=0.6, bottom=0.6)
            + inset_element(ggplot(df, Aes(x="x", y="y")) + geom_point(), left=0.1, bottom=0.6)
        )
        fig = render(p)
        assert len(fig.get_axes()) >= 3


class TestSharedLegends:
    def test_collect_legends(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p1 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        p2 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        grid = plot_grid(p1, p2, ncol=2, guides="collect")
        fig = render_grid(grid)
        assert fig is not None

    def test_no_collect_default(self):
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": ["a", "b"]})
        p1 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        p2 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        grid = plot_grid(p1, p2, ncol=2)
        fig = render_grid(grid)
        assert fig is not None
