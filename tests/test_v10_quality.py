"""Tests for Phase 2: Quality of Life (2A-2D)."""

import matplotlib.pyplot as plt
import polars as pl
import pytest

from plotten import (
    aes,
    after_stat,
    expand_limits,
    geom_histogram,
    geom_point,
    ggplot,
    scale_color_viridis,
    scale_fill_viridis,
)
from plotten._render._mpl import render
from plotten._validation import PlottenError, _suggest_columns
from plotten.scales._viridis import _resolve_option

# --- 2A: Viridis scales ---


class TestViridisScales:
    def test_scale_color_viridis_default(self):
        s = scale_color_viridis()
        assert s._cmap_name == "viridis"

    def test_scale_fill_viridis_magma(self):
        s = scale_fill_viridis(option="magma")
        assert s._cmap_name == "magma"

    def test_viridis_letter_codes(self):
        assert _resolve_option("A") == "magma"
        assert _resolve_option("B") == "inferno"
        assert _resolve_option("C") == "plasma"
        assert _resolve_option("D") == "viridis"
        assert _resolve_option("E") == "cividis"

    def test_viridis_invalid_option(self):
        with pytest.raises(ValueError, match="Unknown viridis option"):
            scale_color_viridis(option="nonexistent")

    def test_viridis_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "color": [1.0, 2.0, 3.0]})
        plot = ggplot(df, aes(x="x", y="y", color="color")) + geom_point() + scale_color_viridis()
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 2B: expand_limits ---


class TestExpandLimits:
    def test_expand_limits_x(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = ggplot(df, aes(x="x", y="y")) + geom_point() + expand_limits(x=0)
        fig = render(plot)
        ax = fig.get_axes()[0]
        xlim = ax.get_xlim()
        # x-axis should include 0
        assert xlim[0] <= 0
        plt.close(fig)

    def test_expand_limits_y(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = ggplot(df, aes(x="x", y="y")) + geom_point() + expand_limits(y=10)
        fig = render(plot)
        ax = fig.get_axes()[0]
        ylim = ax.get_ylim()
        assert ylim[1] >= 10
        plt.close(fig)

    def test_expand_limits_both(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = ggplot(df, aes(x="x", y="y")) + geom_point() + expand_limits(x=[-5, 10], y=0)
        fig = render(plot)
        ax = fig.get_axes()[0]
        xlim = ax.get_xlim()
        assert xlim[0] <= -5
        assert xlim[1] >= 10
        plt.close(fig)


# --- 2C: Better error messages ---


class TestErrorMessages:
    def test_suggest_columns(self):
        suggestions = _suggest_columns({"colour"}, ["color", "fill", "size"])
        assert "color" in suggestions

    def test_no_suggestion_for_unrelated(self):
        suggestions = _suggest_columns({"zzzzz"}, ["color", "fill"])
        assert suggestions == ""

    def test_error_message_includes_suggestion(self):
        """When a required aes column is missing but a similar one exists, suggest it."""

        hint = _suggest_columns({"xend"}, ["x_end", "y", "x"])
        assert "x_end" in hint


# --- 2D: after_stat reliability ---


class TestAfterStat:
    def test_after_stat_valid_column(self):
        from plotten import Aes

        df = pl.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
        plot = ggplot(df, Aes(x="x", y=after_stat("density"))) + geom_histogram(bins=3)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_after_stat_invalid_column(self):
        from plotten import Aes

        df = pl.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
        plot = ggplot(df, Aes(x="x", y=after_stat("nonexistent"))) + geom_histogram(bins=3)
        with pytest.raises(PlottenError, match="does not exist in the stat output"):
            render(plot)
