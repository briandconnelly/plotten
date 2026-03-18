"""Tests for v0.6.0 stat_summary and guides."""

from __future__ import annotations

import matplotlib
import numpy as np
import polars as pl
import pytest

from plotten import (
    Aes,
    GuideColorbar,
    GuideLegend,
    geom_point,
    ggplot,
    guide_colorbar,
    guide_legend,
    guides,
    scale_color_continuous,
    stat_summary,
)
from plotten.geoms._summary import GeomSummary
from plotten.stats._summary import StatSummary

matplotlib.use("Agg")


# ── StatSummary ─────────────────────────────────────────────────────


class TestStatSummary:
    @pytest.fixture
    def summary_data(self):
        return pl.DataFrame(
            {
                "x": ["a", "a", "a", "b", "b", "b"],
                "y": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            }
        )

    def test_compute_default_mean(self, summary_data):
        stat = StatSummary()
        result = stat.compute(summary_data)
        assert len(result) == 2
        assert "x" in result.columns
        assert "y" in result.columns
        assert "ymin" in result.columns
        assert "ymax" in result.columns

    def test_compute_mean_values(self, summary_data):
        stat = StatSummary(fun_y="mean")
        result = stat.compute(summary_data)
        df = pl.from_pandas(result) if hasattr(result, "iloc") else result
        y_vals = df.get_column("y").to_list()
        assert y_vals[0] == pytest.approx(2.0)
        assert y_vals[1] == pytest.approx(5.0)

    def test_compute_median(self, summary_data):
        stat = StatSummary(fun_y="median")
        result = stat.compute(summary_data)
        df = pl.from_pandas(result) if hasattr(result, "iloc") else result
        y_vals = df.get_column("y").to_list()
        assert y_vals[0] == pytest.approx(2.0)

    def test_compute_min_max(self, summary_data):
        stat = StatSummary(fun_y="mean", fun_ymin="min", fun_ymax="max")
        result = stat.compute(summary_data)
        df = pl.from_pandas(result) if hasattr(result, "iloc") else result
        ymin_vals = df.get_column("ymin").to_list()
        ymax_vals = df.get_column("ymax").to_list()
        assert ymin_vals[0] == pytest.approx(1.0)
        assert ymax_vals[0] == pytest.approx(3.0)

    def test_compute_mean_sd(self, summary_data):
        stat = StatSummary(fun_ymin="mean_sd_lower", fun_ymax="mean_sd_upper")
        result = stat.compute(summary_data)
        df = pl.from_pandas(result) if hasattr(result, "iloc") else result
        y_vals = df.get_column("y").to_list()
        ymin_vals = df.get_column("ymin").to_list()
        ymax_vals = df.get_column("ymax").to_list()
        assert ymin_vals[0] < y_vals[0] < ymax_vals[0]

    def test_custom_callable(self, summary_data):
        stat = StatSummary(fun_y=lambda v: float(np.sum(v)))
        result = stat.compute(summary_data)
        df = pl.from_pandas(result) if hasattr(result, "iloc") else result
        y_vals = df.get_column("y").to_list()
        assert y_vals[0] == pytest.approx(6.0)

    def test_unknown_function_raises(self):
        with pytest.raises(ValueError, match="Unknown summary function"):
            StatSummary(fun_y="nonexistent")

    def test_required_aes(self):
        assert StatSummary.required_aes == frozenset({"x", "y"})


# ── GeomSummary ─────────────────────────────────────────────────────


class TestGeomSummary:
    def test_required_aes(self):
        assert GeomSummary.required_aes == frozenset({"x", "y"})

    def test_default_stat(self):
        g = GeomSummary()
        assert isinstance(g.default_stat(), StatSummary)


# ── stat_summary layer ──────────────────────────────────────────────


class TestStatSummaryLayer:
    def test_renders(self):
        df = pl.DataFrame(
            {
                "x": ["a"] * 10 + ["b"] * 10,
                "y": list(range(10)) + list(range(5, 15)),
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + stat_summary()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_custom_functions(self):
        df = pl.DataFrame(
            {
                "x": ["a"] * 5 + ["b"] * 5,
                "y": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + stat_summary(
            fun_y="median", fun_ymin="min", fun_ymax="max"
        )
        fig = p._repr_png_()
        assert len(fig) > 0


# ── Guides ──────────────────────────────────────────────────────────


class TestGuides:
    def test_guide_legend_creation(self):
        g = guide_legend(title="My Legend", reverse=True)
        assert isinstance(g, GuideLegend)
        assert g.title == "My Legend"
        assert g.reverse is True

    def test_guide_colorbar_creation(self):
        g = guide_colorbar(title="Values", barwidth=0.05, nbin=128)
        assert isinstance(g, GuideColorbar)
        assert g.title == "Values"
        assert g.barwidth == 0.05
        assert g.nbin == 128

    def test_guides_factory(self):
        g = guides(color=guide_legend(title="Color"), fill=guide_colorbar(title="Fill"))
        assert isinstance(g, dict)
        assert "color" in g
        assert "fill" in g

    def test_guide_legend_defaults(self):
        g = GuideLegend()
        assert g.title is None
        assert g.nrow is None
        assert g.ncol is None
        assert g.reverse is False
        assert g.override_aes is None

    def test_guide_colorbar_defaults(self):
        g = GuideColorbar()
        assert g.title is None
        assert g.barwidth is None
        assert g.barheight is None
        assert g.nbin == 256
        assert g.reverse is False


class TestGuidesIntegration:
    def test_guides_in_plot(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
                "z": [0.0, 5.0, 10.0],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="z"))
            + geom_point()
            + scale_color_continuous()
            + guides(color=guide_colorbar(title="My Scale"))
        )
        assert p.guides is not None
        assert "color" in p.guides
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_guide_legend_title_override(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "c"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + guides(color=guide_legend(title="Groups"))
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_guide_reverse(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "c"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + guides(color=guide_legend(reverse=True))
        )
        fig = p._repr_png_()
        assert len(fig) > 0
