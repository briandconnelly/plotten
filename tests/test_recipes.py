"""Tests for plot recipes."""

from __future__ import annotations

import tempfile

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl

from plotten import (
    Plot,
    ggsave,
    plot_dumbbell,
    plot_forest,
    plot_lollipop,
    plot_slope,
    plot_waterfall,
)

matplotlib.use("Agg")


def _render_plot(p: Plot) -> None:
    """Helper to render a plot to a temp file."""
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        ggsave(p, f.name)
    plt.close("all")


class TestPlotWaterfall:
    def test_returns_plot(self):
        df = pd.DataFrame({"category": ["A", "B", "C"], "value": [100, -30, 50]})
        p = plot_waterfall(df, x="category", y="value")
        assert isinstance(p, Plot)

    def test_renders(self):
        df = pd.DataFrame({"category": ["A", "B", "C"], "value": [100, -30, 50]})
        p = plot_waterfall(df, x="category", y="value")
        _render_plot(p)

    def test_with_title(self):
        df = pd.DataFrame({"cat": ["X", "Y"], "val": [10, -5]})
        p = plot_waterfall(df, x="cat", y="val", title="My Waterfall")
        assert isinstance(p, Plot)

    def test_no_total(self):
        df = pd.DataFrame({"cat": ["A", "B"], "val": [10, 20]})
        p = plot_waterfall(df, x="cat", y="val", total_label=None)
        _render_plot(p)

    def test_no_connector(self):
        df = pd.DataFrame({"cat": ["A", "B"], "val": [10, 20]})
        p = plot_waterfall(df, x="cat", y="val", connector=False)
        _render_plot(p)

    def test_polars_input(self):
        df = pl.DataFrame({"cat": ["A", "B", "C"], "val": [50, -20, 30]})
        p = plot_waterfall(df, x="cat", y="val")
        _render_plot(p)

    def test_custom_colors(self):
        df = pd.DataFrame({"cat": ["A", "B"], "val": [10, -5]})
        p = plot_waterfall(
            df,
            x="cat",
            y="val",
            fill_increase="#00ff00",
            fill_decrease="#ff0000",
            fill_total="#0000ff",
        )
        assert isinstance(p, Plot)


class TestPlotDumbbell:
    def test_returns_plot(self):
        df = pd.DataFrame(
            {
                "team": ["A", "B", "C"],
                "before": [10, 20, 30],
                "after": [15, 18, 35],
            }
        )
        p = plot_dumbbell(df, x_start="before", x_end="after", y="team")
        assert isinstance(p, Plot)

    def test_renders(self):
        df = pd.DataFrame(
            {
                "team": ["A", "B"],
                "start": [5, 10],
                "end": [15, 20],
            }
        )
        p = plot_dumbbell(df, x_start="start", x_end="end", y="team")
        _render_plot(p)

    def test_has_three_layers(self):
        """Should have segment + 2 point layers."""
        df = pd.DataFrame({"team": ["A"], "s": [1], "e": [5]})
        p = plot_dumbbell(df, x_start="s", x_end="e", y="team")
        assert len(p.layers) == 3

    def test_with_title(self):
        df = pd.DataFrame({"t": ["X"], "a": [1], "b": [2]})
        p = plot_dumbbell(df, x_start="a", x_end="b", y="t", title="Dumbbell")
        assert isinstance(p, Plot)

    def test_polars_input(self):
        df = pl.DataFrame({"g": ["A", "B"], "s": [1, 3], "e": [4, 6]})
        p = plot_dumbbell(df, x_start="s", x_end="e", y="g")
        _render_plot(p)


class TestPlotLollipop:
    def test_returns_plot(self):
        df = pd.DataFrame({"item": ["A", "B", "C"], "value": [10, 25, 15]})
        p = plot_lollipop(df, x="item", y="value")
        assert isinstance(p, Plot)

    def test_renders_vertical(self):
        df = pd.DataFrame({"item": [1, 2, 3], "value": [10, 25, 15]})
        p = plot_lollipop(df, x="item", y="value")
        _render_plot(p)

    def test_renders_horizontal(self):
        df = pd.DataFrame({"item": [1, 2], "value": [10, 25]})
        p = plot_lollipop(df, x="item", y="value", horizontal=True)
        _render_plot(p)

    def test_has_two_layers(self):
        """Should have segment + point."""
        df = pd.DataFrame({"x": [1], "y": [5]})
        p = plot_lollipop(df, x="x", y="y")
        assert len(p.layers) == 2

    def test_custom_baseline(self):
        df = pd.DataFrame({"x": [1, 2], "y": [10, 20]})
        p = plot_lollipop(df, x="x", y="y", baseline=5)
        _render_plot(p)

    def test_polars_input(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
        p = plot_lollipop(df, x="x", y="y")
        _render_plot(p)


class TestPlotSlope:
    def test_returns_plot(self):
        df = pd.DataFrame(
            {
                "time": ["before", "before", "after", "after"],
                "score": [10, 20, 15, 18],
                "group": ["A", "B", "A", "B"],
            }
        )
        p = plot_slope(df, x="time", y="score", group="group")
        assert isinstance(p, Plot)

    def test_renders(self):
        df = pd.DataFrame(
            {
                "time": ["t1", "t1", "t2", "t2"],
                "val": [5, 8, 7, 6],
                "who": ["X", "Y", "X", "Y"],
            }
        )
        p = plot_slope(df, x="time", y="val", group="who")
        _render_plot(p)

    def test_no_labels(self):
        df = pd.DataFrame(
            {
                "time": ["a", "a", "b", "b"],
                "val": [1, 2, 3, 4],
                "g": ["p", "q", "p", "q"],
            }
        )
        p = plot_slope(df, x="time", y="val", group="g", label=False)
        _render_plot(p)

    def test_with_color(self):
        df = pd.DataFrame(
            {
                "t": ["1", "1", "2", "2"],
                "v": [10, 20, 15, 25],
                "g": ["a", "b", "a", "b"],
            }
        )
        p = plot_slope(df, x="t", y="v", group="g", color="steelblue")
        assert isinstance(p, Plot)


class TestPlotForest:
    def test_returns_plot(self):
        df = pd.DataFrame(
            {
                "study": ["Study 1", "Study 2", "Study 3"],
                "effect": [0.5, -0.2, 0.8],
                "lo": [0.1, -0.6, 0.3],
                "hi": [0.9, 0.2, 1.3],
            }
        )
        p = plot_forest(df, y="study", x="effect", xmin="lo", xmax="hi")
        assert isinstance(p, Plot)

    def test_renders(self):
        df = pd.DataFrame(
            {
                "study": ["A", "B"],
                "est": [1.2, 0.8],
                "lower": [0.5, 0.3],
                "upper": [1.9, 1.3],
            }
        )
        p = plot_forest(df, y="study", x="est", xmin="lower", xmax="upper")
        _render_plot(p)

    def test_custom_vline(self):
        df = pd.DataFrame({"s": ["X"], "e": [1.5], "lo": [1.0], "hi": [2.0]})
        p = plot_forest(df, y="s", x="e", xmin="lo", xmax="hi", vline=1.0)
        assert isinstance(p, Plot)

    def test_has_three_layers(self):
        """Should have vline + errorbar + point."""
        df = pd.DataFrame({"s": ["A"], "e": [0.5], "lo": [0.1], "hi": [0.9]})
        p = plot_forest(df, y="s", x="e", xmin="lo", xmax="hi")
        assert len(p.layers) == 3

    def test_polars_input(self):
        df = pl.DataFrame(
            {
                "study": ["A", "B"],
                "effect": [0.5, 1.0],
                "lo": [0.1, 0.5],
                "hi": [0.9, 1.5],
            }
        )
        p = plot_forest(df, y="study", x="effect", xmin="lo", xmax="hi")
        _render_plot(p)

    def test_with_title(self):
        df = pd.DataFrame({"s": ["A"], "e": [0.5], "lo": [0.1], "hi": [0.9]})
        p = plot_forest(df, y="s", x="e", xmin="lo", xmax="hi", title="Forest Plot")
        assert isinstance(p, Plot)
