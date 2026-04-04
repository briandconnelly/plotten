from __future__ import annotations

import datetime
import importlib
import inspect
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, cast

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

if TYPE_CHECKING:
    import narwhals as nw
import polars as pl
import pytest

matplotlib.use("Agg")

import plotten
from plotten import (
    Aes,
    Labs,
    PlotGrid,
    aes,
    after_stat,
    coord_flip,
    expand_limits,
    facet_wrap,
    geom_abline,
    geom_area,
    geom_bar,
    geom_col,
    geom_density,
    geom_histogram,
    geom_hline,
    geom_line,
    geom_path,
    geom_point,
    geom_smooth,
    geom_step,
    geom_vline,
    ggplot,
    ggsave,
    labs,
    scale_alpha_continuous,
    scale_color_viridis,
    scale_fill_viridis,
    scale_linetype_discrete,
    scale_shape_discrete,
    scale_x_continuous,
    scale_x_date,
    scale_x_discrete,
    scale_y_continuous,
    scale_y_log10,
    theme_minimal,
)
from plotten._layer import Layer
from plotten._plot import Plot
from plotten._protocols import Coord, Geom, Scale, Stat
from plotten._render._data_pipeline import _detect_group_key, _split_by_group
from plotten._render._mpl import render
from plotten._render._resolve import resolve
from plotten._validation import ConfigError, DataError, ScaleError, _suggest_columns
from plotten.coords._cartesian import CoordCartesian
from plotten.facets import FacetWrap
from plotten.geoms._path import GeomPath
from plotten.geoms._point import GeomPoint
from plotten.positions import PositionDodge, PositionFill, PositionStack
from plotten.scales._base import MappedContinuousScale, MappedDiscreteScale, auto_scale
from plotten.scales._date import ScaleDateContinuous
from plotten.scales._position import ScaleContinuous, ScaleDiscrete
from plotten.scales._viridis import _resolve_option
from plotten.stats._identity import StatIdentity

# --- from test_integration.py ---


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


def test_lazy_select_projects_columns():
    """With lazy_select=True, only mapped columns are collected from a LazyFrame."""
    from plotten import options

    lf = pl.LazyFrame(
        {
            "x": [1, 2, 3],
            "y": [4, 5, 6],
            "unused_a": ["a", "b", "c"],
            "unused_b": [10, 20, 30],
        }
    )
    with options(lazy_select=True):
        p = ggplot(lf, aes(x="x", y="y")) + geom_point()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            p.save(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


def test_lazy_select_off_collects_all_columns():
    """Without lazy_select, a LazyFrame collects all columns (default behavior)."""
    lf = pl.LazyFrame(
        {
            "x": [1, 2, 3],
            "y": [4, 5, 6],
            "extra": ["a", "b", "c"],
        }
    )
    p = ggplot(lf, aes(x="x", y="y")) + geom_point()
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


class TestReprHtml:
    def test_plot_repr_html(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        html = p._repr_html_()
        assert isinstance(html, str)
        assert "vega" in html.lower()
        assert "vegaEmbed" in html

    def test_plot_repr_html_fallback(self):
        """repr_html returns None when Vega-Lite conversion fails."""
        p = ggplot()  # no data — Vega-Lite can't convert
        # Should not raise; returns None so Jupyter falls back to PNG
        result = p._repr_html_()
        # Result is either None (fallback) or a string (if VL handles empty plots)
        assert result is None or isinstance(result, str)


class TestReprMimeBundle:
    def test_plot_default_bundle(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        bundle = p._repr_mimebundle_()
        assert "image/png" in bundle
        assert bundle["image/png"][:4] == b"\x89PNG"
        # HTML should also be present when VL succeeds
        assert "text/html" in bundle

    def test_plot_include_filter(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        bundle = p._repr_mimebundle_(include={"image/png"})
        assert "image/png" in bundle
        assert "text/html" not in bundle

    def test_plot_exclude_filter(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        bundle = p._repr_mimebundle_(exclude={"text/html"})
        assert "image/png" in bundle
        assert "text/html" not in bundle

    def test_grid_mimebundle(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        grid = p | p
        bundle = grid._repr_mimebundle_()
        assert "image/png" in bundle
        assert bundle["image/png"][:4] == b"\x89PNG"


class TestMarimoMime:
    def test_plot_mime(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        content, mimetype = p._mime_()
        assert mimetype == "text/html"
        assert isinstance(content, str)
        # Should be Vega-Lite HTML
        assert "vegaEmbed" in content

    def test_plot_mime_fallback(self):
        """Marimo _mime_ returns PNG data-URI when VL fails."""
        p = ggplot()  # no data
        content, mimetype = p._mime_()
        assert mimetype == "text/html"
        assert isinstance(content, str)
        # Either VL HTML or PNG data-URI fallback
        assert "vegaEmbed" in content or "data:image/png;base64," in content

    def test_grid_mime(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        grid = p | p
        content, mimetype = grid._mime_()
        assert mimetype == "text/html"
        assert "data:image/png;base64," in content


# --- from test_v05_coverage.py ---

"""Additional tests to bring v0.5 coverage to 95%+."""


class TestGeomPointBranches:
    def test_shape_with_color_list(self):
        """Test per-point shapes with per-point colors."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 2, 3, 4],
                "g": ["a", "b", "a", "b"],
                "z": [10, 20, 30, 40],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", color="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_shape_with_size_list(self):
        """Test per-point shapes with per-point sizes."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "a"],
                "z": [10, 20, 30],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", size="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_shape_with_alpha_list(self):
        """Test per-point shapes with per-point alpha."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "a"],
                "z": [10, 50, 100],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", alpha="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_point_with_param_size(self):
        """Test geom_point with size as a param, not aesthetic."""
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point(size=50)
        assert len(p._repr_png_()) > 0

    def test_point_with_param_alpha(self):
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point(alpha=0.5)
        assert len(p._repr_png_()) > 0


class TestGeomLineBranches:
    def test_line_with_alpha_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(alpha=0.5)
        assert len(p._repr_png_()) > 0

    def test_line_with_linetype_mapped(self):
        """Mapped linetype (list of strings)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "a", "a"]})
        p = ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line()
        assert len(p._repr_png_()) > 0

    def test_line_with_size_mapped(self):
        """Mapped size as linewidth."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [1.0, 1.0, 1.0]})
        p = ggplot(df, aes(x="x", y="y", size="z")) + geom_line()
        assert len(p._repr_png_()) > 0

    def test_line_with_linetype_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(linetype="dashed")
        assert len(p._repr_png_()) > 0

    def test_line_with_size_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(size=3)
        assert len(p._repr_png_()) > 0

    def test_line_with_color_mapped(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(color="red")
        assert len(p._repr_png_()) > 0


class TestAutoScaleFallbacks:
    def test_unknown_aesthetic_numeric(self):
        """Non-special aesthetic with numeric data should get ScaleContinuous."""

        s = pl.Series("weight", [1.0, 2.0, 3.0])
        scale = auto_scale("weight", s)
        assert isinstance(scale, ScaleContinuous)

    def test_unknown_aesthetic_categorical(self):
        """Non-special aesthetic with string data should get ScaleDiscrete."""

        s = pl.Series("category", ["a", "b", "c"])
        scale = auto_scale("category", s)
        assert isinstance(scale, ScaleDiscrete)


class TestScaleAlphaDiscreteLegend:
    def test_legend_entries(self):
        scale = scale_alpha_continuous()
        s = pl.Series("alpha", [0, 100])
        scale.train(s)
        entries = scale.legend_entries()
        assert all(e.alpha is not None for e in entries)

    def test_discrete_legend(self):
        from plotten.scales._alpha import ScaleAlphaDiscrete

        scale = ScaleAlphaDiscrete()
        s = pl.Series("alpha", ["lo", "hi"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2


class TestScaleSizeDiscreteLegend:
    def test_legend_entries(self):
        from plotten.scales._size import ScaleSizeDiscrete

        scale = ScaleSizeDiscrete()
        s = pl.Series("size", ["sm", "lg"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert entries[0].size is not None


class TestScaleLinetypeLegend:
    def test_get_labels(self):
        scale = scale_linetype_discrete()
        s = pl.Series("linetype", ["a", "b"])
        scale.train(s)
        labels = scale.get_labels()
        assert labels == ["a", "b"]


class TestScaleShapeLegend:
    def test_get_labels(self):
        scale = scale_shape_discrete()
        s = pl.Series("shape", ["cat", "dog"])
        scale.train(s)
        labels = scale.get_labels()
        assert labels == ["cat", "dog"]


class TestDateScaleBranches:
    def test_scale_y_date(self):
        from plotten import scale_y_date

        scale = scale_y_date()
        assert scale.aesthetic == "y"

    def test_scale_x_datetime(self):
        from plotten import scale_x_datetime

        scale = scale_x_datetime()
        assert scale.aesthetic == "x"

    def test_scale_y_datetime(self):
        from plotten import scale_y_datetime

        scale = scale_y_datetime()
        assert scale.aesthetic == "y"

    def test_date_with_limits(self):

        scale = ScaleDateContinuous(
            aesthetic="x",
            limits=(datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
        )
        lo, hi = scale.get_limits()
        assert lo < hi


class TestPositionNoXY:
    def test_dodge_no_x(self):
        data = {"y": [1, 2]}
        result = PositionDodge().adjust(data, {})
        assert result == data

    def test_stack_no_x(self):
        data = {"y": [1, 2]}
        result = PositionStack().adjust(data, {})
        assert result == data

    def test_fill_no_x(self):
        data = {"y": [1, 2]}
        result = PositionFill().adjust(data, {})
        assert result == data


class TestHistogramWithPosition:
    def test_histogram_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3, 4, 5, 1, 2, 3]})
        p = ggplot(df, aes(x="x")) + geom_histogram(bins=5)
        assert len(p._repr_png_()) > 0


class TestGeomPointShapeBranches:
    """Test uncommon branches when shapes are mapped."""

    def test_shape_with_param_size(self):
        """Shape mapped, size as param (not aesthetic)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(size=50)
        assert len(p._repr_png_()) > 0

    def test_shape_with_param_alpha(self):
        """Shape mapped, alpha as param (not aesthetic)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(alpha=0.5)
        assert len(p._repr_png_()) > 0

    def test_shape_with_single_color_string(self):
        """Shape mapped, color is a fixed string."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(color="red")
        assert len(p._repr_png_()) > 0


class TestGeomLineMappedBranches:
    def test_line_with_alpha_mapped(self):
        """Alpha mapped as aesthetic on line."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [10, 50, 100]})
        p = ggplot(df, aes(x="x", y="y", alpha="z")) + geom_line()
        assert len(p._repr_png_()) > 0


class TestColWithFillBranches:
    def test_col_with_color_string(self):
        df = pl.DataFrame({"x": ["a", "b"], "y": [10, 20]})
        p = ggplot(df, aes(x="x", y="y")) + geom_col(color="blue")
        assert len(p._repr_png_()) > 0

    def test_col_with_alpha(self):
        df = pl.DataFrame({"x": ["a", "b"], "y": [10, 20]})
        p = ggplot(df, aes(x="x", y="y")) + geom_col(alpha=0.5)
        assert len(p._repr_png_()) > 0


# --- from test_v08_coverage.py ---

"""Extra coverage tests for v0.8.0 features."""


class TestGeomPathCoverage:
    def test_path_with_size_param(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 2.0], "y": [0.0, 1.0, 0.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(size=2)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_default_stat(self):

        g = GeomPath()
        assert isinstance(g.default_stat(), StatIdentity)


class TestGeomStepCoverage:
    def test_step_with_all_params(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step(
            color="red", alpha=0.5, linetype="--", size=2
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatQQCoveragePandas:
    def test_qq_pandas(self):
        import numpy as np

        from plotten.stats._qq import StatQQ, StatQQLine

        np.random.seed(42)
        df = pd.DataFrame({"x": np.random.randn(20)})
        result = cast("nw.DataFrame", StatQQ().compute(df))
        assert "x" in result.columns
        assert "y" in result.columns

        result2 = cast("nw.DataFrame", StatQQLine().compute(df))
        assert len(result2) == 2


class TestLabelNumberThousandsSeparator:
    def test_label_number_default_thousands_separator(self):
        from plotten.scales._labels import label_number

        fmt = label_number(precision=1)
        assert fmt(12345.6) == "12,345.6"


# --- from test_v09_expand.py ---

"""Tests for expand parameter on continuous and discrete scales."""


class TestContinuousExpand:
    def test_default_expand_matches_default_padding(self):
        s = ScaleContinuous()
        assert s._expand == (0.05, 0)

    def test_expand_overrides_padding(self):
        s = ScaleContinuous(expand=(0.1, 0.5))
        assert s._expand == (0.1, 0.5)

    def test_expand_mult_and_add(self):
        s = ScaleContinuous(expand=(0.1, 2.0))
        s.train(pd.Series([0, 100]))
        lo, hi = s.get_limits()
        # span=100, pad = 100*0.1 + 2.0 = 12.0
        assert lo == pytest.approx(-12.0)
        assert hi == pytest.approx(112.0)

    def test_expand_zero(self):
        s = ScaleContinuous(expand=(0, 0))
        s.train(pd.Series([10, 20]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(10.0)
        assert hi == pytest.approx(20.0)

    def test_expand_add_only(self):
        s = ScaleContinuous(expand=(0, 1.0))
        s.train(pd.Series([5, 15]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(4.0)
        assert hi == pytest.approx(16.0)

    def test_padding_and_expand_raises(self):
        with pytest.raises(ScaleError, match="Cannot specify both"):
            ScaleContinuous(padding=0.1, expand=(0.1, 0))

    def test_default_padding_with_expand_ok(self):
        # Default padding=0.05 should not conflict with expand
        s = ScaleContinuous(expand=(0.2, 0))
        assert s._expand == (0.2, 0)

    def test_scale_factory_accepts_expand(self):
        s = scale_x_continuous(expand=(0, 5))
        assert s._expand == (0, 5)
        assert s.aesthetic == "x"

    def test_scale_y_factory_accepts_expand(self):
        s = scale_y_continuous(expand=(0.1, 1))
        assert s._expand == (0.1, 1)
        assert s.aesthetic == "y"

    def test_expand_in_plot(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + scale_x_continuous(expand=(0, 0))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_xlim()
        assert lo == pytest.approx(1.0)
        assert hi == pytest.approx(3.0)

    def test_backward_compat_padding(self):
        s = ScaleContinuous(padding=0.1)
        assert s._expand == (0.1, 0)
        s.train(pd.Series([0, 100]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(-10.0)
        assert hi == pytest.approx(110.0)


class TestDiscreteExpand:
    def test_default_expand(self):
        s = ScaleDiscrete()
        assert s._expand == (0, 0.6)

    def test_custom_expand(self):
        s = ScaleDiscrete(expand=(0.1, 0.5))
        assert s._expand == (0.1, 0.5)

    def test_default_expand_limits(self):
        s = ScaleDiscrete()
        s.train(pd.Series(["a", "b", "c"]))
        lo, hi = s.get_limits()
        # n=3, mult=0, add=0.6 → lo=-0.6, hi=2+0.6=2.6
        assert lo == pytest.approx(-0.6)
        assert hi == pytest.approx(2.6)

    def test_expand_with_mult(self):
        s = ScaleDiscrete(expand=(0.5, 0))
        s.train(pd.Series(["a", "b", "c"]))
        lo, hi = s.get_limits()
        # n=3, lo = -0.5*2 - 0 = -1.0, hi = 2 + 0.5*2 + 0 = 3.0
        assert lo == pytest.approx(-1.0)
        assert hi == pytest.approx(3.0)

    def test_expand_zero(self):
        s = ScaleDiscrete(expand=(0, 0))
        s.train(pd.Series(["a", "b"]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(0)
        assert hi == pytest.approx(1.0)

    def test_single_level(self):
        s = ScaleDiscrete()
        s.train(pd.Series(["a"]))
        lo, hi = s.get_limits()
        # n=1, lo = -0*0 - 0.6 = -0.6, hi = 0 + 0*0 + 0.6 = 0.6
        assert lo == pytest.approx(-0.6)
        assert hi == pytest.approx(0.6)

    def test_empty_levels(self):
        s = ScaleDiscrete()
        lo, hi = s.get_limits()
        assert lo == pytest.approx(-0.5)
        assert hi == pytest.approx(0.5)

    def test_factory_accepts_expand(self):
        s = scale_x_discrete(expand=(0, 1.0))
        assert s._expand == (0, 1.0)

    def test_discrete_expand_in_plot(self):
        df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_bar() + scale_x_discrete(expand=(0, 0))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_xlim()
        assert lo == pytest.approx(0)
        assert hi == pytest.approx(2.0)


# --- from test_v15_api.py ---

"""Phase 1 API consistency tests for v0.15.0."""


class TestAllImports:
    """Verify every symbol in plotten.__all__ is importable."""

    @pytest.mark.parametrize("name", plotten.__all__)
    def test_symbol_importable(self, name: str):
        obj = getattr(plotten, name, None)
        assert obj is not None, f"plotten.{name} listed in __all__ but not importable"

    def test_all_sorted(self):
        """__all__ should be sorted for readability."""
        assert plotten.__all__ == sorted(plotten.__all__)


class TestSubpackageAll:
    """Verify subpackage __all__ entries are importable."""

    @pytest.mark.parametrize(
        "module_path",
        [
            "plotten.geoms",
            "plotten.scales",
            "plotten.positions",
            "plotten.coords",
            "plotten.facets",
            "plotten.themes",
            "plotten.stats",
        ],
    )
    def test_subpackage_all_importable(self, module_path: str):
        mod = importlib.import_module(module_path)
        for name in mod.__all__:
            obj = getattr(mod, name, None)
            assert obj is not None, f"{module_path}.{name} in __all__ but not importable"


class TestColourAlias:
    """Verify 'colour' works as alias for 'color' in aes()."""

    def test_colour_alias(self):
        mapping = plotten.aes(x="a", colour="b")
        assert mapping.color == "b"
        assert mapping.x == "a"

    def test_colour_and_color_raises(self):
        with pytest.raises(ConfigError, match="Cannot specify both"):
            plotten.aes(color="a", colour="b")

    def test_color_still_works(self):
        mapping = plotten.aes(color="species")
        assert mapping.color == "species"


class TestMethodConsistency:
    """Verify Plot and PlotGrid have consistent public methods."""

    def test_plot_has_show_and_save(self):
        p = plotten.ggplot()
        assert callable(getattr(p, "show", None))
        assert callable(getattr(p, "save", None))

    def test_plotgrid_has_show_and_save(self):
        from plotten._composition import PlotGrid

        g = PlotGrid()
        assert callable(getattr(g, "show", None))
        assert callable(getattr(g, "save", None))

    def test_save_units_parameter(self):
        """Both Plot.save and PlotGrid.save should accept a 'units' parameter."""
        plot_params = inspect.signature(plotten.Plot.save).parameters
        assert "units" in plot_params

        grid_params = inspect.signature(PlotGrid.save).parameters
        assert "units" in grid_params

    def test_save_signatures_compatible(self):
        """Plot.save and PlotGrid.save should have the same core parameters."""

        plot_params = set(inspect.signature(plotten.Plot.save).parameters)
        grid_params = set(inspect.signature(plotten.PlotGrid.save).parameters)
        core = {"path", "dpi", "width", "height", "units"}
        assert core <= plot_params
        assert core <= grid_params


class TestGeomFactoryConsistency:
    """Verify all geom factories accept **params / **kwargs."""

    @pytest.mark.parametrize(
        "name",
        [n for n in plotten.__all__ if n.startswith("geom_") or n.startswith("stat_")],
    )
    def test_geom_is_callable(self, name: str):
        fn = getattr(plotten, name)
        assert callable(fn), f"{name} should be callable"

    def test_linetype_aesthetic_exists(self):
        """The Aes dataclass should use 'linetype' (not 'line_type')."""
        mapping = plotten.aes(linetype="group")
        assert mapping.linetype == "group"
        assert not hasattr(plotten.Aes, "line_type")


# --- from test_v15_performance.py ---

"""Tests for v0.15.0 Phase 3: Performance improvements."""


class TestImportTime:
    """Verify that ``import plotten`` completes in a reasonable time."""

    def test_import_time_under_500ms(self) -> None:
        """import plotten should complete in under 500ms.

        This guards against accidentally pulling heavy dependencies
        (matplotlib, scipy) at import time.  The threshold is generous
        to avoid flaking on cold-cache CI runners.
        """
        code = (
            "import time; t = time.time(); import plotten; "
            "print(f'{(time.time() - t) * 1000:.0f}')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        ms = int(result.stdout.strip())
        assert ms < 500, f"import plotten took {ms}ms, expected < 500ms"


class TestScaleCaching:
    """Verify that scale break/label computation is cached."""

    def test_continuous_breaks_cached(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series = pl.Series("x", [1.0, 2.0, 3.0, 4.0, 5.0])
        scale.train(series)

        breaks1 = scale.get_breaks()
        breaks2 = scale.get_breaks()
        assert breaks1 is breaks2, "get_breaks() should return cached list"

    def test_continuous_labels_cached(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series = pl.Series("x", [1.0, 2.0, 3.0, 4.0, 5.0])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2, "get_labels() should return cached list"

    def test_cache_invalidated_on_train(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series1 = pl.Series("x", [1.0, 2.0, 3.0])
        scale.train(series1)
        breaks1 = scale.get_breaks()

        series2 = pl.Series("x", [10.0, 20.0])
        scale.train(series2)
        breaks2 = scale.get_breaks()

        assert breaks1 is not breaks2, "Cache should be invalidated after train()"
        assert breaks2[-1] > breaks1[-1], "New breaks should reflect expanded domain"

    def test_discrete_labels_cached(self) -> None:
        scale = ScaleDiscrete(aesthetic="x")
        series = pl.Series("x", ["a", "b", "c"])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2, "get_labels() should return cached list"

    def test_discrete_cache_invalidated(self) -> None:
        scale = ScaleDiscrete(aesthetic="x")
        series1 = pl.Series("x", ["a", "b"])
        scale.train(series1)
        labels1 = scale.get_labels()

        series2 = pl.Series("x", ["c", "d"])
        scale.train(series2)
        labels2 = scale.get_labels()

        assert labels1 is not labels2
        assert len(labels2) == 4

    def test_mapped_continuous_breaks_cached(self) -> None:
        """MappedContinuousScale subclasses should also cache breaks."""

        class _TestScale(MappedContinuousScale):
            def __init__(self) -> None:
                super().__init__("test")
                self._breaks = None
                self._limits = None

            def map_data(self, values: object) -> object:
                return values

        scale = _TestScale()
        series = pl.Series("v", [0.0, 10.0])
        scale.train(series)

        breaks1 = scale.get_breaks()
        breaks2 = scale.get_breaks()
        assert breaks1 is breaks2

    def test_mapped_discrete_labels_cached(self) -> None:
        """MappedDiscreteScale subclasses should also cache labels."""

        class _TestScale(MappedDiscreteScale):
            def __init__(self) -> None:
                super().__init__("test")
                self._levels: list = []

            def map_data(self, values: object) -> object:
                return values

        scale = _TestScale()
        series = pl.Series("v", ["x", "y", "z"])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2


# --- from test_v11_ggsave.py ---

"""Tests for the ggsave() convenience function."""


def _make_plot():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    return ggplot(df, Aes(x="x", y="y")) + geom_point()


def test_ggsave_basic(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_svg(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.svg"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_pdf(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.pdf"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_width_height(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=8, height=6)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_width_only(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=10)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_height_only(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, height=5)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_cm_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=20, height=15, units="cm")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_mm_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=200, height=150, units="mm")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_px_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=800, height=600, units="px")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_transparent(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, transparent=True)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_custom_dpi(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, dpi=72)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_pathlib(tmp_path: Path) -> None:
    p = _make_plot()
    out = Path(tmp_path) / "subdir" / "plot.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


# --- from test_v05_save.py ---

"""Tests for v0.5 save improvements."""


class TestSave:
    @pytest.fixture
    def simple_plot(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        return ggplot(df, aes(x="x", y="y")) + geom_point()

    def test_save_default(self, simple_plot, tmp_path):
        path = str(tmp_path / "test.png")
        simple_plot.save(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_width_height_inches(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_wh.png")
        simple_plot.save(path, width=10, height=6, units="in")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_cm(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_cm.png")
        simple_plot.save(path, width=25, height=15, units="cm")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_mm(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_mm.png")
        simple_plot.save(path, width=250, height=150, units="mm")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_px(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_px.png")
        simple_plot.save(path, width=800, height=600, units="px", dpi=100)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_backward_compat(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_compat.png")
        simple_plot.save(path, dpi=72)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_width_only(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_w.png")
        simple_plot.save(path, width=12)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


# --- from test_v05_dates.py ---

"""Tests for v0.5 date/time scales."""


class TestScaleDateContinuous:
    def test_train_python_date(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [
                datetime.date(2024, 1, 1),
                datetime.date(2024, 6, 1),
                datetime.date(2024, 12, 31),
            ],
        )
        scale.train(dates)
        lo, hi = scale.get_limits()
        assert lo < hi

    def test_train_python_datetime(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [
                datetime.datetime(2024, 1, 1, 0, 0),
                datetime.datetime(2024, 6, 1, 12, 0),
            ],
        )
        scale.train(dates)
        lo, hi = scale.get_limits()
        assert lo < hi

    def test_map_data(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)],
        )
        scale.train(dates)
        mapped = scale.map_data(dates)
        assert isinstance(mapped, list)
        assert len(mapped) == 2
        assert mapped[0] < mapped[1]

    def test_breaks(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)],
        )
        scale.train(dates)
        breaks = scale.get_breaks()
        assert len(breaks) == 6


class TestAutoScaleDate:
    def test_detects_date(self):
        s = pl.Series("x", [datetime.date(2024, 1, 1), datetime.date(2024, 6, 1)])
        scale = auto_scale("x", s)
        assert isinstance(scale, ScaleDateContinuous)

    def test_detects_datetime(self):
        s = pl.Series(
            "x",
            [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 6, 1)],
        )
        scale = auto_scale("x", s)
        assert isinstance(scale, ScaleDateContinuous)


class TestExplicitDateScale:
    def test_scale_x_date(self):
        scale = scale_x_date()
        assert isinstance(scale, ScaleDateContinuous)
        assert scale.aesthetic == "x"


class TestDateIntegration:
    def test_python_date_renders(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.date(2024, 1, 1),
                    datetime.date(2024, 4, 1),
                    datetime.date(2024, 7, 1),
                ],
                "y": [10, 20, 30],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_python_datetime_renders(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.datetime(2024, 1, 1, 0, 0),
                    datetime.datetime(2024, 6, 1, 12, 0),
                    datetime.datetime(2024, 12, 1, 6, 0),
                ],
                "y": [1, 2, 3],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_explicit_scale_x_date(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.date(2024, 1, 1),
                    datetime.date(2024, 6, 1),
                ],
                "y": [10, 20],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line() + scale_x_date()
        fig = p._repr_png_()
        assert len(fig) > 0


class TestDateWithPandas:
    def test_pandas_timestamp_renders(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame(
            {
                "x": pd.to_datetime(["2024-01-01", "2024-06-01", "2024-12-01"]),
                "y": [1, 2, 3],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line()
        fig = p._repr_png_()
        assert len(fig) > 0


# --- from test_plot.py ---


def test_ggplot_returns_plot():
    p = ggplot()
    assert isinstance(p, Plot)


def test_ggplot_with_data_and_mapping():
    p = ggplot(data=[1, 2, 3], mapping=aes(x="a"))
    assert p.data == [1, 2, 3]
    assert p.mapping.x == "a"


def test_add_layer():
    p = ggplot()
    layer = Layer(geom=GeomPoint(), mapping=aes(x="x", y="y"))
    p2 = p + layer
    assert len(p2.layers) == 1
    assert len(p.layers) == 0  # immutable


def test_add_scale():
    p = ggplot()
    s = ScaleContinuous("x")
    p2 = p + s
    assert len(p2.scales) == 1
    assert len(p.scales) == 0


def test_add_theme():
    p = ggplot()
    p2 = p + theme_minimal()
    assert p2.theme.panel_background == "none"
    assert p.theme.panel_background == "#ffffff"


def test_add_unsupported_raises_config_error():

    p = ggplot()
    with pytest.raises(ConfigError, match="Cannot add 'int' to a Plot"):
        p + 42


def test_add_preserves_immutability():
    p1 = ggplot(mapping=aes(x="a"))
    layer = Layer(geom=GeomPoint())
    p2 = p1 + layer
    p3 = p2 + theme_minimal()
    # Each is distinct
    assert len(p1.layers) == 0
    assert len(p2.layers) == 1
    assert p3.theme.panel_background == "none"
    assert p2.theme.panel_background == "#ffffff"


# --- from test_layer.py ---


def test_layer_construction():
    layer = Layer(geom=GeomPoint(), mapping=aes(x="a", y="b"))
    assert layer.geom is not None
    assert layer.mapping.x == "a"
    assert layer.stat is None
    assert layer.data is None


def test_layer_with_stat():
    layer = Layer(geom=GeomPoint(), stat=StatIdentity(), mapping=Aes())
    assert isinstance(layer.stat, StatIdentity)


def test_layer_frozen():
    layer = Layer(geom=GeomPoint())
    try:
        layer.geom = None  # type: ignore[misc]
        pytest.fail("Should have raised")
    except AttributeError:
        pass


# --- from test_labs.py ---


def test_labs_creation():
    lb = Labs(title="My Title", x="X Axis")
    assert lb.title == "My Title"
    assert lb.x == "X Axis"
    assert lb.y is None


def test_labs_convenience():
    lb = labs(title="Hello", y="Y Axis")
    assert isinstance(lb, Labs)
    assert lb.title == "Hello"
    assert lb.y == "Y Axis"


def test_labs_merge():
    a = Labs(title="A", x="X1")
    b = Labs(title="B", caption="Cap")
    merged = a + b
    assert merged.title == "B"  # other wins
    assert merged.x == "X1"  # kept from self
    assert merged.caption == "Cap"


def test_labs_immutable():
    lb = Labs(title="T")
    assert lb.title == "T"


def test_plot_with_labs():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Test", x="X Label", y="Y Label")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_subtitle_only():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(subtitle="Just subtitle")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_title_and_subtitle():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + labs(title="Main Title", subtitle="A subtitle")
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_caption_rendering():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(caption="Source: test data")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


# --- from test_protocols.py ---


def test_stat_protocol():
    assert isinstance(StatIdentity(), Stat)


def test_geom_protocol():
    assert isinstance(GeomPoint(), Geom)


def test_scale_protocol():
    assert isinstance(ScaleContinuous("x"), Scale)


def test_coord_protocol():
    assert isinstance(CoordCartesian(), Coord)


# --- from test_reflines.py ---


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


# --- from test_v10_quality.py ---

"""Tests for Phase 2: Quality of Life (2A-2D)."""

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
        with pytest.raises(ScaleError, match="Unknown viridis option"):
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

        df = pl.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
        plot = ggplot(df, Aes(x="x", y=after_stat("density"))) + geom_histogram(bins=3)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_after_stat_invalid_column(self):

        df = pl.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
        plot = ggplot(df, Aes(x="x", y=after_stat("nonexistent"))) + geom_histogram(bins=3)
        with pytest.raises(DataError, match="does not exist in the stat output"):
            render(plot)


# --- from test_v08_grouping.py ---

"""Tests for v0.8.0 group splitting and multi-series rendering."""


class TestGroupSplitting:
    def test_detect_group_key_color(self):
        data = {"x": [1, 2, 3], "y": [1, 2, 3], "color": ["red", "red", "blue"]}
        assert _detect_group_key(data) == "color"

    def test_detect_group_key_group(self):
        data = {"x": [1, 2], "y": [1, 2], "group": ["a", "b"], "color": ["red", "red"]}
        assert _detect_group_key(data) == "group"

    def test_detect_group_key_none_uniform(self):
        data = {"x": [1, 2], "y": [1, 2], "color": ["red", "red"]}
        assert _detect_group_key(data) is None

    def test_detect_group_key_none_no_aesthetic(self):
        data = {"x": [1, 2], "y": [1, 2]}
        assert _detect_group_key(data) is None

    def test_detect_group_key_fill(self):
        data = {"x": [1, 2], "y": [1, 2], "fill": ["a", "b"]}
        assert _detect_group_key(data) == "fill"

    def test_detect_group_key_linetype(self):
        data = {"x": [1, 2], "y": [1, 2], "linetype": ["-", "--"]}
        assert _detect_group_key(data) == "linetype"

    def test_split_by_group_basic(self):
        data = {
            "x": [1, 2, 3, 4],
            "y": [10, 20, 30, 40],
            "color": ["red", "red", "blue", "blue"],
        }
        result = _split_by_group(data, "color")
        assert len(result) == 2
        assert result[0]["x"] == [1, 2]
        assert result[0]["y"] == [10, 20]
        assert result[0]["color"] == ["red", "red"]
        assert result[1]["x"] == [3, 4]
        assert result[1]["color"] == ["blue", "blue"]

    def test_split_preserves_order(self):
        data = {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "color": ["blue", "red", "blue"],
        }
        result = _split_by_group(data, "color")
        assert len(result) == 2
        assert result[0]["color"] == ["blue", "blue"]
        assert result[0]["x"] == [1, 3]
        assert result[1]["color"] == ["red"]

    def test_split_scalar_non_list(self):
        data = {
            "x": [1, 2, 3, 4],
            "y": [10, 20, 30, 40],
            "color": ["red", "red", "blue", "blue"],
            "alpha": 0.5,
        }
        result = _split_by_group(data, "color")
        assert result[0]["alpha"] == 0.5


class TestMultiSeriesLine:
    def test_line_color_grouping(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="grp")) + geom_line()
        fig = render(p)
        ax = fig.axes[0]
        assert len(ax.lines) >= 2
        plt.close(fig)

    def test_line_group_aesthetic(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", group="grp")) + geom_line()
        fig = render(p)
        ax = fig.axes[0]
        assert len(ax.lines) >= 2
        plt.close(fig)

    def test_line_no_grouping(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line()
        fig = render(p)
        ax = fig.axes[0]
        assert len(ax.lines) >= 1
        plt.close(fig)


class TestMultiSeriesArea:
    def test_area_color_grouping(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="grp")) + geom_area()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestMultiSeriesStep:
    def test_step_color_grouping(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="grp")) + geom_step()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestMultiSeriesDensity:
    def test_density_color_grouping(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0, 1.5, 2.5, 3.5, 4.5, 5.5],
                "grp": ["a"] * 5 + ["b"] * 5,
            }
        )
        p = ggplot(df, aes(x="x", color="grp")) + geom_density()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestSupportsGroupSplitting:
    def test_line_supports_splitting(self):
        from plotten.geoms._line import GeomLine

        assert GeomLine.supports_group_splitting is True

    def test_point_does_not_support_splitting(self):

        assert GeomPoint.supports_group_splitting is False

    def test_area_supports_splitting(self):
        from plotten.geoms._area import GeomArea

        assert GeomArea.supports_group_splitting is True

    def test_step_supports_splitting(self):
        from plotten.geoms._step import GeomStep

        assert GeomStep.supports_group_splitting is True

    def test_smooth_supports_splitting(self):
        from plotten.geoms._smooth import GeomSmooth

        assert GeomSmooth.supports_group_splitting is True

    def test_ribbon_supports_splitting(self):
        from plotten.geoms._ribbon import GeomRibbon

        assert GeomRibbon.supports_group_splitting is True

    def test_density_supports_splitting(self):
        from plotten.geoms._density import GeomDensity

        assert GeomDensity.supports_group_splitting is True

    def test_bar_no_splitting(self):
        from plotten.geoms._bar import GeomBar

        assert GeomBar.supports_group_splitting is False

    def test_boxplot_no_splitting(self):
        from plotten.geoms._boxplot import GeomBoxplot

        assert GeomBoxplot.supports_group_splitting is False

    def test_refline_no_splitting(self):
        from plotten.geoms._refline import GeomAbLine, GeomHLine, GeomVLine

        assert GeomHLine.supports_group_splitting is False
        assert GeomVLine.supports_group_splitting is False
        assert GeomAbLine.supports_group_splitting is False


class TestResolveGroupSplitting:
    def test_resolve_splits_line_layers(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="grp")) + geom_line()
        resolved = resolve(p)
        layers = resolved.panels[0].layers
        # Should be split into 2 layers (one per group)
        assert len(layers) == 2

    def test_resolve_no_split_for_point(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "grp": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="grp")) + geom_point()
        resolved = resolve(p)
        layers = resolved.panels[0].layers
        # Should remain as 1 layer (point handles per-element)
        assert len(layers) == 1
