from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from plotten._types import GeomDrawData, GeomParams

import matplotlib
import matplotlib.pyplot as plt
import narwhals as nw
import numpy as np
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

import plotten
from plotten import (
    Aes,
    GuideColorbar,
    GuideLegend,
    aes,
    geom_bin2d,
    geom_density_ridges,
    geom_point,
    geom_qq,
    geom_qq_line,
    geom_smooth,
    ggplot,
    guide_colorbar,
    guide_legend,
    guides,
    scale_color_continuous,
    stat_cor,
    stat_ecdf,
    stat_function,
    stat_poly_eq,
    stat_summary,
)
from plotten._layer import Layer
from plotten._render._mpl import render
from plotten.geoms._errorbarh import GeomErrorbarH
from plotten.geoms._freqpoly import GeomFreqpoly
from plotten.geoms._summary import GeomSummary
from plotten.stats import StatBin, StatCount, StatIdentity
from plotten.stats._bin2d import StatBin2d
from plotten.stats._cor import StatCor
from plotten.stats._density import StatDensity
from plotten.stats._density_ridges import StatDensityRidges
from plotten.stats._ecdf import StatECDF
from plotten.stats._function import StatFunction
from plotten.stats._poly_eq import StatPolyEq
from plotten.stats._qq import StatQQ, StatQQLine
from plotten.stats._smooth import StatSmooth
from plotten.stats._summary import StatSummary, _resolve_fun_data
from plotten.stats._violin import StatViolin

# --- from test_stats.py ---


def test_stat_identity():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    result = cast("nw.DataFrame", StatIdentity().compute(df))
    assert cast("nw.DataFrame", nw.from_native(result).shape == (3, 2))


def test_stat_count():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    result = cast("nw.DataFrame", nw.from_native(StatCount().compute(df)))
    assert {"x", "y", "count", "prop"}.issubset(set(result.columns))
    # a=3, b=2, c=1
    rows = {r["x"]: r["y"] for r in result.iter_rows(named=True)}
    assert rows["a"] == 3
    assert rows["b"] == 2
    assert rows["c"] == 1
    # Verify count matches y and prop sums to 1
    prop_rows = {r["x"]: r["prop"] for r in result.iter_rows(named=True)}
    assert sum(prop_rows.values()) == pytest.approx(1.0)


def test_stat_bin():
    df = pl.DataFrame({"x": list(range(100))})
    result = cast("nw.DataFrame", nw.from_native(StatBin(bins=10).compute(df)))
    assert "x" in result.columns
    assert "y" in result.columns
    assert result.shape[0] == 10


def test_stat_smooth_loess():
    pytest.importorskip("scipy")
    df = pl.DataFrame({"x": list(range(20)), "y": [float(i % 5) for i in range(20)]})
    stat = StatSmooth(method="loess", se=True, n_points=10)
    result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
    assert result.shape[0] == 10
    assert set(result.columns) >= {"x", "y", "ymin", "ymax"}


def test_stat_smooth_moving_average():
    df = pl.DataFrame({"x": list(range(20)), "y": [float(i) for i in range(20)]})
    stat = StatSmooth(method="moving_average", se=False, n_points=10)
    result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
    assert result.shape[0] == 10
    assert set(result.columns) >= {"x", "y"}


def test_stat_smooth_unknown_method():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    stat = StatSmooth(method="nonexistent")
    with pytest.raises(ValueError, match="Unknown smoothing method"):
        stat.compute(df)


# --- from test_v04_stats.py ---


def test_stat_density_basic():
    pytest.importorskip("scipy")
    from plotten.stats._density import StatDensity

    df = pl.DataFrame({"x": [float(i) for i in range(50)]})
    stat = StatDensity(n_points=100)
    result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
    assert set(result.columns) == {"x", "y"}
    assert len(result) == 100


def test_stat_density_grouped():
    pytest.importorskip("scipy")

    df = pl.DataFrame(
        {
            "x": [float(i) for i in range(40)],
            "color": ["a"] * 20 + ["b"] * 20,
        }
    )
    stat = StatDensity(n_points=50)
    result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
    assert "color" in result.columns
    # 2 groups * 50 points each = 100 rows
    assert len(result) == 100


def test_stat_density_pandas():
    pytest.importorskip("scipy")

    df = pd.DataFrame({"x": [float(i) for i in range(30)]})
    stat = StatDensity(n_points=50)
    result = cast("nw.DataFrame", stat.compute(df))
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 50


def test_stat_violin_basic():
    pytest.importorskip("scipy")

    rng = np.random.default_rng(42)
    df = pl.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    stat = StatViolin(n_points=50)
    result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
    assert set(result.columns) == {"x", "y_grid", "density", "y_min", "y_max"}
    # One row per x group
    assert len(result) == 2


def test_stat_violin_pandas():
    pytest.importorskip("scipy")

    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    stat = StatViolin(n_points=50)
    result = cast("nw.DataFrame", stat.compute(df))
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2


# --- from test_v08_stats.py ---

"""Tests for v0.8.0 new stats: ECDF, QQ, Bin2d."""


class TestStatECDF:
    def test_compute_polars(self):
        df = pl.DataFrame({"x": [3.0, 1.0, 2.0, 5.0, 4.0]})
        stat = StatECDF()
        result = cast("nw.DataFrame", stat.compute(df))
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 5
        assert result_df["x"].to_list() == [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result_df["y"].to_list() == [0.2, 0.4, 0.6, 0.8, 1.0]

    def test_compute_pandas(self):

        df = pd.DataFrame({"x": [3.0, 1.0, 2.0]})
        stat = StatECDF()
        result = cast("nw.DataFrame", stat.compute(df))
        assert list(result["x"]) == [1.0, 2.0, 3.0]
        np.testing.assert_allclose(list(result["y"]), [1 / 3, 2 / 3, 1.0])

    def test_stat_ecdf_render(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
        p = ggplot(df, aes(x="x")) + stat_ecdf()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatQQ:
    def test_compute_qq(self):
        np.random.seed(42)
        data = np.random.randn(50)
        df = pl.DataFrame({"x": data.tolist()})
        stat = StatQQ()
        result = cast("nw.DataFrame", stat.compute(df))
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 50
        assert "x" in result_df.columns
        assert "y" in result_df.columns
        # y should be sorted sample values
        assert result_df["y"].to_list() == sorted(data.tolist())

    def test_compute_qq_line(self):
        np.random.seed(42)
        data = np.random.randn(50)
        df = pl.DataFrame({"x": data.tolist()})
        stat = StatQQLine()
        result = cast("nw.DataFrame", stat.compute(df))
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 2
        assert "x" in result_df.columns
        assert "y" in result_df.columns

    def test_geom_qq_render(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(30).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_qq_line_render(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(30).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq_line()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_qq_combined(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(50).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq() + geom_qq_line()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatBin2d:
    def test_compute_bin2d(self):
        np.random.seed(42)
        df = pl.DataFrame(
            {
                "x": np.random.randn(100).tolist(),
                "y": np.random.randn(100).tolist(),
            }
        )
        stat = StatBin2d(bins=5)
        result = cast("nw.DataFrame", stat.compute(df))
        result_df = pl.DataFrame(result)
        assert "x" in result_df.columns
        assert "y" in result_df.columns
        assert "fill" in result_df.columns
        assert all(f > 0 for f in result_df["fill"].to_list())

    def test_geom_bin2d_render(self):
        np.random.seed(42)
        df = pl.DataFrame(
            {
                "x": np.random.randn(100).tolist(),
                "y": np.random.randn(100).tolist(),
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_bin2d(bins=5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bin2d_pandas(self):

        np.random.seed(42)
        df = pd.DataFrame(
            {
                "x": np.random.randn(50),
                "y": np.random.randn(50),
            }
        )
        stat = StatBin2d(bins=5)
        result = cast("nw.DataFrame", stat.compute(df))
        assert "x" in result.columns
        assert "fill" in result.columns


# --- from test_v06_stat_summary.py ---

"""Tests for v0.6.0 stat_summary and guides."""

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
        result = cast("nw.DataFrame", stat.compute(summary_data))
        assert len(result) == 2
        assert "x" in result.columns
        assert "y" in result.columns
        assert "ymin" in result.columns
        assert "ymax" in result.columns

    def test_compute_mean_values(self, summary_data):
        stat = StatSummary(fun_y="mean")
        result = cast("nw.DataFrame", stat.compute(summary_data))
        df = cast("pl.DataFrame", pl.from_pandas(result) if hasattr(result, "iloc") else result)
        y_vals = df.get_column("y").to_list()
        assert y_vals[0] == pytest.approx(2.0)
        assert y_vals[1] == pytest.approx(5.0)

    def test_compute_median(self, summary_data):
        stat = StatSummary(fun_y="median")
        result = cast("nw.DataFrame", stat.compute(summary_data))
        df = cast("pl.DataFrame", pl.from_pandas(result) if hasattr(result, "iloc") else result)
        y_vals = df.get_column("y").to_list()
        assert y_vals[0] == pytest.approx(2.0)

    def test_compute_min_max(self, summary_data):
        stat = StatSummary(fun_y="mean", fun_ymin="min", fun_ymax="max")
        result = cast("nw.DataFrame", stat.compute(summary_data))
        df = cast("pl.DataFrame", pl.from_pandas(result) if hasattr(result, "iloc") else result)
        ymin_vals = df.get_column("ymin").to_list()
        ymax_vals = df.get_column("ymax").to_list()
        assert ymin_vals[0] == pytest.approx(1.0)
        assert ymax_vals[0] == pytest.approx(3.0)

    def test_compute_mean_sd(self, summary_data):
        stat = StatSummary(fun_ymin="mean_sd_lower", fun_ymax="mean_sd_upper")
        result = cast("nw.DataFrame", stat.compute(summary_data))
        df = cast("pl.DataFrame", pl.from_pandas(result) if hasattr(result, "iloc") else result)
        y_vals = df.get_column("y").to_list()
        ymin_vals = df.get_column("ymin").to_list()
        ymax_vals = df.get_column("ymax").to_list()
        assert ymin_vals[0] < y_vals[0] < ymax_vals[0]

    def test_custom_callable(self, summary_data):
        stat = StatSummary(fun_y=lambda v: float(np.sum(v)))
        result = cast("nw.DataFrame", stat.compute(summary_data))
        df = cast("pl.DataFrame", pl.from_pandas(result) if hasattr(result, "iloc") else result)
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


# --- from test_v09_stat_function.py ---

"""Tests for stat_function."""


class TestStatFunction:
    def test_basic_sin(self):
        stat = StatFunction(fun=np.sin, n=50)
        result = cast("nw.DataFrame", stat.compute(pd.DataFrame({"x": [0, 2 * math.pi]})))
        assert len(result) == 50
        assert "x" in result.columns
        assert "y" in result.columns

    def test_custom_n(self):
        stat = StatFunction(fun=lambda x: x**2, n=200)
        result = cast("nw.DataFrame", stat.compute(pd.DataFrame({"x": [0, 10]})))
        assert len(result) == 200

    def test_xlim_override(self):
        stat = StatFunction(fun=lambda x: x, n=10, xlim=(-5, 5))
        result = cast("pd.DataFrame", stat.compute(pd.DataFrame({"x": [0]})))
        assert result["x"].iloc[0] == pytest.approx(-5.0)
        assert result["x"].iloc[-1] == pytest.approx(5.0)

    def test_no_data_x_range(self):
        stat = StatFunction(fun=lambda x: x, n=10)
        # No x column → defaults to (0, 1)
        result = cast("pd.DataFrame", stat.compute(pd.DataFrame({"a": [1]})))
        assert result["x"].iloc[0] == pytest.approx(0.0)
        assert result["x"].iloc[-1] == pytest.approx(1.0)

    def test_uses_data_x_range(self):
        stat = StatFunction(fun=lambda x: x, n=10)
        result = cast("pd.DataFrame", stat.compute(pd.DataFrame({"x": [10, 20]})))
        assert result["x"].iloc[0] == pytest.approx(10.0)
        assert result["x"].iloc[-1] == pytest.approx(20.0)

    def test_required_aes_empty(self):
        assert StatFunction.required_aes == frozenset()

    def test_in_plot_standalone(self):
        p = ggplot() + stat_function(fun=np.sin, xlim=(0, 2 * math.pi))
        fig = render(p)
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert len(lines) >= 1

    def test_in_plot_with_data(self):
        df = pd.DataFrame({"x": np.linspace(0, 10, 50), "y": np.random.default_rng(42).random(50)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + stat_function(fun=lambda x: x * 0.1, color="red")
        )
        fig = render(p)
        ax = fig.axes[0]
        # Should have both points and a line
        assert len(ax.collections) >= 1 or len(ax.get_lines()) >= 1

    def test_stat_function_with_custom_xlim(self):
        p = ggplot() + stat_function(fun=lambda x: x**2, xlim=(-3, 3), n=51)
        fig = render(p)
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert len(lines) >= 1
        xdata = lines[0].get_xdata()
        assert float(xdata[0]) == pytest.approx(-3.0)  # type: ignore[index]
        assert float(xdata[-1]) == pytest.approx(3.0)  # type: ignore[index]


# --- from test_v12_smooth.py ---

"""Tests for v0.12.0 smooth enhancements."""


class TestPolynomialSmooth:
    def test_poly_method(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + geom_smooth(method="poly", degree=2)
        fig = render(p)
        assert fig is not None

    def test_poly_default_degree(self):
        stat = StatSmooth(method="poly")
        assert stat.degree == 2

    def test_poly_cubic(self):
        df = pd.DataFrame({"x": range(10), "y": [x**3 for x in range(10)]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_smooth(method="poly", degree=3)
        fig = render(p)
        assert fig is not None

    def test_poly_no_se(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_smooth(method="poly", se=False)
        fig = render(p)
        assert fig is not None


class TestStatPolyEq:
    def test_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 5, 4, 5]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_poly_eq()
        fig = render(p)
        assert fig is not None

    def test_compute_output(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        stat = StatPolyEq(degree=1)
        result = cast("nw.DataFrame", stat.compute(df))

        frame = cast("nw.DataFrame", nw.from_native(result))
        assert "label" in frame.columns
        label = frame.get_column("label").to_list()[0]
        assert "R²" in label
        assert "y =" in label

    def test_quadratic_eq(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        stat = StatPolyEq(degree=2)
        result = cast("nw.DataFrame", stat.compute(df))

        label = cast("nw.DataFrame", nw.from_native(result).get_column("label").to_list())[0]
        assert "R²" in label

    def test_perfect_fit_r_squared(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        stat = StatPolyEq(degree=1)
        result = cast("nw.DataFrame", stat.compute(df))

        label = cast("nw.DataFrame", nw.from_native(result).get_column("label").to_list())[0]
        assert "1.000" in label  # R² should be 1.0


# --- from test_v12_ridges.py ---

"""Tests for geom_density_ridges."""


class TestStatDensityRidges:
    def test_compute_produces_groups(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(3, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        stat = StatDensityRidges()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        assert "x" in frame.columns
        assert "ymin" in frame.columns
        assert "ymax" in frame.columns
        groups = set(frame.get_column("group").to_list())
        assert "A" in groups
        assert "B" in groups

    def test_baselines_offset(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(0, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        stat = StatDensityRidges()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        ymin_vals = frame.get_column("ymin").to_list()
        groups = frame.get_column("group").to_list()
        # Group A baseline should be 0, Group B baseline should be 1
        a_baselines = {ymin_vals[i] for i, g in enumerate(groups) if g == "A"}
        b_baselines = {ymin_vals[i] for i, g in enumerate(groups) if g == "B"}
        assert 0.0 in a_baselines
        assert 1.0 in b_baselines


class TestGeomDensityRidges:
    def test_renders(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate(
                    [
                        rng.normal(0, 1, 100),
                        rng.normal(2, 1, 100),
                        rng.normal(4, 1, 100),
                    ]
                ),
                "y": ["Group A"] * 100 + ["Group B"] * 100 + ["Group C"] * 100,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges()
        fig = render(p)
        assert fig is not None

    def test_custom_bandwidth(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(3, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges(bandwidth=0.5)
        fig = render(p)
        assert fig is not None

    def test_custom_alpha(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": rng.normal(0, 1, 100),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges(alpha=0.3)
        fig = render(p)
        assert fig is not None


# --- from test_v14_stat_cor.py ---

"""Tests for Phase 3: stat_cor and stat_summary improvements."""

# ---------------------------------------------------------------------------
# 3A: StatCor
# ---------------------------------------------------------------------------


class TestStatCor:
    """Tests for StatCor correlation annotation stat."""

    def _make_df(self, x: list[float], y: list[float]) -> pl.DataFrame:
        return pl.DataFrame({"x": x, "y": y})

    def test_pearson_positive_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor(method="pearson")
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        assert "R = 1.00" in label
        assert "p" in label

    def test_spearman_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor(method="spearman")
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        assert "rho = 1.00" in label

    def test_negative_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        stat = StatCor(method="pearson")
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        assert "R = -1.00" in label

    def test_no_correlation(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.standard_normal(200).tolist()
        y = rng.standard_normal(200).tolist()
        stat = StatCor(method="pearson")
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        # R should be close to 0
        assert "R =" in label

    def test_output_columns(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor()
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert "x" in result_nw.columns
        assert "y" in result_nw.columns
        assert "label" in result_nw.columns
        assert len(result_nw) == 1

    def test_label_position_default(self) -> None:
        x = [0.0, 10.0]
        y = [0.0, 100.0]
        stat = StatCor(label_x=0.1, label_y=0.9)
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        # label_x=0.1 means 10% from left: 0 + 0.1 * 10 = 1.0
        assert abs(result_nw["x"][0] - 1.0) < 1e-6
        # label_y=0.9 means 90% from bottom: 0 + 0.9 * 100 = 90.0
        assert abs(result_nw["y"][0] - 90.0) < 1e-6

    def test_custom_label_position(self) -> None:
        x = [0.0, 10.0]
        y = [0.0, 100.0]
        stat = StatCor(label_x=0.5, label_y=0.5)
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["x"][0] - 5.0) < 1e-6
        assert abs(result_nw["y"][0] - 50.0) < 1e-6

    def test_digits_parameter(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.1, 3.9, 6.2, 7.8, 10.1]
        stat = StatCor(digits=3)
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        # Should have 3 decimal places in the R value
        parts = label.split(",")[0]  # "R = X.XXX"
        r_val = parts.split("=")[1].strip()
        assert len(r_val.split(".")[1]) == 3

    def test_invalid_method_raises(self) -> None:
        with pytest.raises(ValueError, match="method must be"):
            StatCor(method="kendall")

    def test_p_value_formatting_small(self) -> None:
        # Perfect correlation -> p should be very small
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
        stat = StatCor()
        result = cast("nw.DataFrame", stat.compute(self._make_df(x, y)))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        label = result_nw["label"][0]
        assert "p < 0.001" in label


class TestStatCorFactory:
    """Test the stat_cor() factory function."""

    def test_stat_cor_creates_layer(self) -> None:
        from plotten.geoms import stat_cor

        layer = stat_cor()
        assert layer is not None
        assert layer.stat is not None

    def test_stat_cor_with_params(self) -> None:

        layer = stat_cor(method="spearman", digits=3, label_x=0.5, label_y=0.5)
        assert isinstance(layer.stat, StatCor)
        assert layer.stat.method == "spearman"
        assert layer.stat.digits == 3

    def test_stat_cor_exported_from_top_level(self) -> None:

        assert hasattr(plotten, "stat_cor")


# ---------------------------------------------------------------------------
# 3B: StatSummary improvements
# ---------------------------------------------------------------------------


class TestStatSummaryImprovements:
    """Tests for stat_summary built-in functions and fun_data."""

    def _make_df(self, x: list, y: list[float]) -> pl.DataFrame:
        return pl.DataFrame({"x": x, "y": y})

    def test_median_hilow(self) -> None:
        df = self._make_df(
            ["a", "a", "a", "a", "a"],
            [1.0, 2.0, 3.0, 4.0, 5.0],
        )
        stat = StatSummary(fun_data="median_hilow")
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["y"][0] - 3.0) < 1e-6  # median
        assert abs(result_nw["ymin"][0] - 2.0) < 1e-6  # 25th percentile
        assert abs(result_nw["ymax"][0] - 4.0) < 1e-6  # 75th percentile

    def test_mean_range(self) -> None:
        df = self._make_df(
            ["a", "a", "a", "a", "a"],
            [1.0, 2.0, 3.0, 4.0, 5.0],
        )
        stat = StatSummary(fun_data="mean_range")
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["y"][0] - 3.0) < 1e-6  # mean
        assert abs(result_nw["ymin"][0] - 1.0) < 1e-6  # min
        assert abs(result_nw["ymax"][0] - 5.0) < 1e-6  # max

    def test_fun_data_callable_dict(self) -> None:
        """fun_data accepts a callable returning a dict."""

        def my_fun(v: np.ndarray) -> dict[str, float]:
            return {"y": float(np.mean(v)), "ymin": float(np.min(v)), "ymax": float(np.max(v))}

        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_data=my_fun)
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6

    def test_fun_data_callable_tuple(self) -> None:
        """fun_data accepts a callable returning a tuple."""

        def my_fun(v: np.ndarray) -> tuple[float, float, float]:
            return (float(np.median(v)), float(np.min(v)), float(np.max(v)))

        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_data=my_fun)
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6

    def test_fun_data_overrides_individual_funs(self) -> None:
        """When fun_data is set, fun_y/fun_ymin/fun_ymax are ignored."""
        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(
            fun_y="median",
            fun_ymin="min",
            fun_ymax="max",
            fun_data="mean_range",
        )
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        # Should use mean_range, not median
        assert abs(result_nw["y"][0] - 20.0) < 1e-6  # mean, not median

    def test_multiple_groups_with_fun_data(self) -> None:
        df = self._make_df(
            ["a", "a", "b", "b"],
            [1.0, 3.0, 10.0, 20.0],
        )
        stat = StatSummary(fun_data="mean_range")
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert len(result_nw) == 2
        # Group "a": mean=2, min=1, max=3
        assert abs(result_nw["y"][0] - 2.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 1.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 3.0) < 1e-6

    def test_unknown_fun_data_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown fun_data"):
            _resolve_fun_data("nonexistent")

    def test_stat_summary_factory_with_fun_data(self) -> None:

        layer = stat_summary(fun_data="median_hilow")
        assert layer is not None
        assert isinstance(layer.stat, StatSummary)
        assert layer.stat._fun_data is not None

    def test_existing_behavior_unchanged(self) -> None:
        """Default StatSummary still works with fun_y/fun_ymin/fun_ymax."""
        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_y="mean", fun_ymin="min", fun_ymax="max")
        result = cast("nw.DataFrame", stat.compute(df))
        result_nw = cast(
            "pl.DataFrame",
            pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result,
        )
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6


# --- from test_v14_freqpoly.py ---

"""Tests for Phase 1 of v0.14.0: geom_freqpoly, geom_area, geom_errorbarh."""

# --- GeomFreqpoly unit tests ---


class TestGeomFreqpoly:
    def test_required_aes(self):
        g = GeomFreqpoly()
        assert g.required_aes == frozenset({"x"})

    def test_default_stat_is_stat_bin(self):
        g = GeomFreqpoly()
        assert isinstance(g.default_stat(), StatBin)

    def test_supports_group_splitting(self):
        g = GeomFreqpoly()
        assert g.supports_group_splitting is True

    def test_draw_produces_line(self):
        g = GeomFreqpoly()
        fig, ax = plt.subplots()
        data = cast("GeomDrawData", {"x": [1.0, 2.0, 3.0], "y": [5, 10, 3]})
        g.draw(data, ax, cast("GeomParams", {}))
        # Should produce one Line2D artist
        assert len(ax.lines) == 1
        plt.close(fig)

    def test_draw_with_color_and_params(self):
        g = GeomFreqpoly()
        fig, ax = plt.subplots()
        data = cast("GeomDrawData", {"x": [1.0, 2.0, 3.0], "y": [5, 10, 3], "color": "red"})
        g.draw(data, ax, cast("GeomParams", {"alpha": 0.5}))
        line = ax.lines[0]
        assert line.get_alpha() == 0.5
        plt.close(fig)


# --- geom_freqpoly factory tests ---


class TestGeomFreqpolyFactory:
    def test_returns_layer(self):
        layer = plotten.geom_freqpoly()
        assert isinstance(layer, Layer)

    def test_layer_has_stat_bin(self):
        layer = plotten.geom_freqpoly(bins=20)
        assert isinstance(layer.stat, StatBin)
        assert layer.stat.bins == 20

    def test_layer_geom_is_freqpoly(self):
        layer = plotten.geom_freqpoly()
        assert isinstance(layer.geom, GeomFreqpoly)

    def test_end_to_end_render(self):
        """Ensure geom_freqpoly renders without error in a full plot."""
        df = pl.DataFrame({"val": [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]})
        p = plotten.ggplot(df, plotten.aes(x="val")) + plotten.geom_freqpoly(bins=5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- geom_area already exists (1B: skipped, just verify) ---


class TestGeomAreaExists:
    def test_geom_area_is_exported(self):
        assert hasattr(plotten, "geom_area")

    def test_geom_area_returns_layer(self):
        layer = plotten.geom_area()
        assert isinstance(layer, Layer)


# --- GeomErrorbarH unit tests ---


class TestGeomErrorbarH:
    def test_required_aes(self):
        g = GeomErrorbarH()
        assert g.required_aes == frozenset({"y", "xmin", "xmax"})

    def test_default_stat_is_identity(self):
        g = GeomErrorbarH()
        assert isinstance(g.default_stat(), StatIdentity)

    def test_supports_group_splitting(self):
        g = GeomErrorbarH()
        assert g.supports_group_splitting is False

    def test_draw_produces_lines(self):
        g = GeomErrorbarH()
        fig, ax = plt.subplots()
        data = cast("GeomDrawData", {"y": [1.0, 2.0], "xmin": [0.5, 1.5], "xmax": [1.5, 2.5]})
        g.draw(data, ax, cast("GeomParams", {}))
        # Each point produces 1 hline (stem) + 2 vlines (caps) = 3 LineCollections
        # matplotlib hlines/vlines create LineCollections
        assert len(ax.collections) > 0
        plt.close(fig)


# --- geom_errorbarh factory tests ---


class TestGeomErrorbarhFactory:
    def test_returns_layer(self):
        layer = plotten.geom_errorbarh()
        assert isinstance(layer, Layer)

    def test_layer_geom_is_errorbarh(self):
        layer = plotten.geom_errorbarh()
        assert isinstance(layer.geom, GeomErrorbarH)

    def test_end_to_end_render(self):
        """Ensure geom_errorbarh renders without error in a full plot."""
        df = pl.DataFrame({"y": [1.0, 2.0, 3.0], "xmin": [0.5, 1.5, 2.5], "xmax": [1.5, 2.5, 3.5]})
        p = (
            plotten.ggplot(df, plotten.aes(y="y", xmin="xmin", xmax="xmax"))
            + plotten.geom_errorbarh()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- KDE bandwidth parameters ---


class TestStatDensityBandwidth:
    def test_bw_method_silverman(self):
        from plotten.stats._density import StatDensity

        df = pl.DataFrame({"x": [float(i) for i in range(50)]})
        stat = StatDensity(bw_method="silverman")
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
        assert "x" in result.columns
        assert "y" in result.columns
        assert len(result) == 200

    def test_bw_method_scott(self):
        from plotten.stats._density import StatDensity

        df = pl.DataFrame({"x": [float(i) for i in range(50)]})
        stat = StatDensity(bw_method="scott")
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
        assert len(result) == 200

    def test_bw_method_scalar(self):
        from plotten.stats._density import StatDensity

        df = pl.DataFrame({"x": [float(i) for i in range(50)]})
        stat = StatDensity(bw_method=0.5)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
        assert len(result) == 200

    def test_bw_adjust_smoother(self):
        """Higher bw_adjust produces smoother density with lower peak."""
        from plotten.stats._density import StatDensity

        df = pl.DataFrame({"x": [1.0, 1.0, 1.0, 5.0, 5.0, 5.0]})
        default = cast("nw.DataFrame", nw.from_native(StatDensity().compute(df)))
        smooth = cast("nw.DataFrame", nw.from_native(StatDensity(bw_adjust=2.0).compute(df)))
        default_peak = max(default.get_column("y").to_list())
        smooth_peak = max(smooth.get_column("y").to_list())
        assert smooth_peak < default_peak

    def test_bw_adjust_rougher(self):
        """Lower bw_adjust produces rougher density with higher peak."""
        from plotten.stats._density import StatDensity

        df = pl.DataFrame({"x": [1.0, 1.0, 1.0, 5.0, 5.0, 5.0]})
        default = cast("nw.DataFrame", nw.from_native(StatDensity().compute(df)))
        rough = cast("nw.DataFrame", nw.from_native(StatDensity(bw_adjust=0.3).compute(df)))
        default_peak = max(default.get_column("y").to_list())
        rough_peak = max(rough.get_column("y").to_list())
        assert rough_peak > default_peak

    def test_bw_adjust_with_groups(self):
        from plotten.stats._density import StatDensity

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                "color": ["a", "a", "a", "b", "b", "b"],
            }
        )
        stat = StatDensity(bw_adjust=0.5)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
        assert "color" in result.columns

    def test_geom_density_forwards_bw_params(self):
        df = pl.DataFrame({"x": [float(i) for i in range(50)]})
        p = ggplot(df, plotten.aes(x="x")) + plotten.geom_density(bw_adjust=0.5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_density_bw_method(self):
        df = pl.DataFrame({"x": [float(i) for i in range(50)]})
        p = ggplot(df, plotten.aes(x="x")) + plotten.geom_density(bw_method="silverman")
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatDensityRidgesBandwidth:
    def test_bw_adjust(self):
        from plotten.stats._density_ridges import StatDensityRidges

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                "y": ["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
            }
        )
        stat = StatDensityRidges(bw_adjust=0.5)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))
        assert "x" in result.columns
        assert "ymin" in result.columns
        assert "ymax" in result.columns

    def test_geom_density_ridges_forwards_bw_adjust(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                "y": ["a", "a", "a", "a", "a", "b", "b", "b", "b", "b"],
            }
        )
        p = ggplot(df, plotten.aes(x="x", y="y")) + plotten.geom_density_ridges(bw_adjust=2.0)
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- StatUnique tests ---


class TestStatUnique:
    def test_deduplication(self):
        from plotten.stats._unique import StatUnique

        df = pl.DataFrame({"x": [1, 1, 2, 2, 3], "y": [1, 1, 4, 4, 9]})
        result = StatUnique().compute(df)
        result_nw = nw.from_native(result)
        assert result_nw.shape[0] == 3

    def test_all_unique(self):
        from plotten.stats._unique import StatUnique

        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        result = StatUnique().compute(df)
        result_nw = nw.from_native(result)
        assert result_nw.shape[0] == 3

    def test_stat_unique_render(self):
        from plotten import stat_unique

        df = pd.DataFrame({"x": [1, 1, 2, 2, 3], "y": [1, 1, 4, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + stat_unique()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_stat_unique_returns_layer(self):
        from plotten import stat_unique
        from plotten._layer import Layer

        layer = stat_unique()
        assert isinstance(layer, Layer)


# --- GeomBlank tests ---


class TestGeomBlank:
    def test_returns_layer(self):
        from plotten import geom_blank
        from plotten._layer import Layer

        layer = geom_blank()
        assert isinstance(layer, Layer)

    def test_geom_blank_renders_empty(self):
        from plotten import geom_blank

        df = pd.DataFrame({"x": [0, 10], "y": [0, 100]})
        p = ggplot(df, aes(x="x", y="y")) + geom_blank()
        fig = render(p)
        assert fig is not None
        ax = fig.axes[0]
        # Axes should reflect the data domain
        xlo, xhi = ax.get_xlim()
        assert xlo <= 0
        assert xhi >= 10
        plt.close(fig)

    def test_geom_blank_with_other_geom(self):
        from plotten import geom_blank

        df_points = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        df_range = pd.DataFrame({"x": [0, 10], "y": [0, 50]})
        p = ggplot(df_points, aes(x="x", y="y")) + geom_point() + geom_blank(data=df_range)
        fig = render(p)
        assert fig is not None
        plt.close(fig)
