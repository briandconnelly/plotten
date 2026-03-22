"""Tests for geom-aware legend swatches."""

from __future__ import annotations

import matplotlib.pyplot as plt
import polars as pl
import pytest
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from plotten import aes, geom_bar, geom_col, geom_line, geom_point, ggplot
from plotten._render._mpl import render
from plotten._render._resolve import _infer_legend_keys, resolve
from plotten.geoms._bar import GeomBar
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.scales._base import LegendEntry


@pytest.fixture
def simple_df():
    return pl.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 3, 4], "g": ["a", "b", "a", "b"]})


# --- Unit tests for _infer_legend_keys ---


class TestInferLegendKeys:
    def test_point_geom_color(self, simple_df):
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_point()
        keys = _infer_legend_keys(plot)
        assert keys["color"] == "point"

    def test_line_geom_color(self, simple_df):
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_line()
        keys = _infer_legend_keys(plot)
        assert keys["color"] == "line"

    def test_bar_geom_fill(self, simple_df):
        plot = ggplot(simple_df, aes(x="x", y="y", fill="g")) + geom_bar()
        keys = _infer_legend_keys(plot)
        assert keys["fill"] == "rect"

    def test_first_layer_wins(self, simple_df):
        """When multiple geoms map the same aesthetic, first layer wins."""
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_point() + geom_line()
        keys = _infer_legend_keys(plot)
        assert keys["color"] == "point"

    def test_first_layer_wins_line_then_point(self, simple_df):
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_line() + geom_point()
        keys = _infer_legend_keys(plot)
        assert keys["color"] == "line"

    def test_no_mapped_aesthetics(self, simple_df):
        plot = ggplot(simple_df, aes(x="x", y="y")) + geom_point()
        keys = _infer_legend_keys(plot)
        assert keys == {}


# --- Unit tests for LegendEntry ---


class TestLegendEntryKey:
    def test_default_key_is_rect(self):
        entry = LegendEntry(label="test")
        assert entry.key == "rect"

    def test_key_can_be_set(self):
        entry = LegendEntry(label="test", key="point")
        assert entry.key == "point"

    def test_replace_key(self):
        from dataclasses import replace

        entry = LegendEntry(label="test", color="red")
        updated = replace(entry, key="line")
        assert updated.key == "line"
        assert updated.color == "red"


# --- Unit tests for legend_key class attributes ---


class TestGeomLegendKey:
    def test_point_key(self):
        assert GeomPoint.legend_key == "point"

    def test_line_key(self):
        assert GeomLine.legend_key == "line"

    def test_bar_key(self):
        assert GeomBar.legend_key == "rect"


# --- Integration tests ---


class TestLegendKeyRendering:
    def test_point_legend_has_scatter(self, simple_df):
        """geom_point + color mapping should render point swatches."""
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_point()
        fig = render(plot)
        # Find legend axes (not the main axes)
        legend_axes = [ax for ax in fig.get_axes() if not ax.get_xlabel() and not ax.get_ylabel()]
        # At least one legend axis should contain PathCollection (scatter)
        has_scatter = any(
            any(isinstance(c, PathCollection) for c in ax.collections) for ax in legend_axes
        )
        assert has_scatter, "Point legend should contain scatter markers (PathCollection)"
        plt.close(fig)

    def test_line_legend_has_lines(self, simple_df):
        """geom_line + color mapping should render line swatches."""
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_line()
        fig = render(plot)
        legend_axes = [ax for ax in fig.get_axes() if not ax.get_xlabel() and not ax.get_ylabel()]
        has_line = any(any(isinstance(ln, Line2D) for ln in ax.get_lines()) for ax in legend_axes)
        assert has_line, "Line legend should contain Line2D swatches"
        plt.close(fig)

    def test_col_legend_has_rectangles(self, simple_df):
        """geom_col + fill mapping should render rectangle swatches."""
        plot = ggplot(simple_df, aes(x="x", y="y", fill="g")) + geom_col()
        fig = render(plot)
        legend_axes = [ax for ax in fig.get_axes() if not ax.get_xlabel() and not ax.get_ylabel()]
        has_rect = any(any(isinstance(p, Rectangle) for p in ax.patches) for ax in legend_axes)
        assert has_rect, "Col legend should contain Rectangle swatches"
        plt.close(fig)

    def test_resolved_plot_has_legend_keys(self, simple_df):
        """ResolvedPlot should carry legend_keys dict."""
        plot = ggplot(simple_df, aes(x="x", y="y", color="g")) + geom_point()
        resolved = resolve(plot)
        assert resolved.legend_keys == {"color": "point"}
