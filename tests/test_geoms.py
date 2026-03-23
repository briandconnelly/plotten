from __future__ import annotations

import math
import os
import tempfile
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

from plotten import (
    Aes,
    aes,
    geom_area,
    geom_boxplot,
    geom_col,
    geom_contour,
    geom_contour_filled,
    geom_count,
    geom_crossbar,
    geom_curve,
    geom_density,
    geom_dotplot,
    geom_errorbar,
    geom_hex,
    geom_histogram,
    geom_hline,
    geom_jitter,
    geom_label,
    geom_linerange,
    geom_path,
    geom_point,
    geom_pointrange,
    geom_polygon,
    geom_quantile,
    geom_raster,
    geom_rect,
    geom_ribbon,
    geom_rug,
    geom_segment,
    geom_smooth,
    geom_spoke,
    geom_step,
    geom_text,
    geom_tile,
    geom_violin,
    ggplot,
    stat_density_2d,
    stat_density_2d_filled,
    stat_ellipse,
    stat_sum,
    stat_summary_bin,
)
from plotten._render._mpl import render
from plotten.geoms._area import GeomArea
from plotten.geoms._bar import GeomBar
from plotten.geoms._col import GeomCol
from plotten.geoms._curve import GeomCurve
from plotten.geoms._density import GeomDensity
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.geoms._quantile import GeomQuantile
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._spoke import GeomSpoke
from plotten.geoms._tile import GeomTile
from plotten.geoms._violin import GeomViolin
from plotten.positions._dodge import PositionDodge
from plotten.positions._dodge2 import PositionDodge2, position_dodge2
from plotten.stats._contour import StatContour
from plotten.stats._count import StatCount
from plotten.stats._count_overlap import StatCountOverlap
from plotten.stats._density2d import StatDensity2d
from plotten.stats._dotplot import StatDotplot
from plotten.stats._ellipse import StatEllipse
from plotten.stats._identity import StatIdentity
from plotten.stats._quantile import StatQuantile
from plotten.stats._summary_bin import StatSummaryBin

# --- from test_geoms.py ---


def test_geom_point_required_aes():
    g = GeomPoint()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_line_required_aes():
    g = GeomLine()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_bar_required_aes():
    g = GeomBar()
    assert g.required_aes == frozenset({"x"})
    assert isinstance(g.default_stat(), StatCount)


def test_geom_area_required_aes():
    g = GeomArea()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_ribbon_required_aes():
    g = GeomRibbon()
    assert g.required_aes == frozenset({"x", "ymin", "ymax"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_tile_required_aes():
    g = GeomTile()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_errorbar_required_aes():
    g = GeomErrorbar()
    assert g.required_aes == frozenset({"x", "ymin", "ymax"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_col_required_aes():
    g = GeomCol()
    assert g.required_aes == frozenset({"x", "y"})
    assert isinstance(g.default_stat(), StatIdentity)


def test_geom_density_required_aes():
    g = GeomDensity()
    assert g.required_aes == frozenset({"x"})
    from plotten.stats._density import StatDensity

    assert isinstance(g.default_stat(), StatDensity)


def test_geom_violin_required_aes():
    g = GeomViolin()
    assert g.required_aes == frozenset({"x", "y"})
    from plotten.stats._violin import StatViolin

    assert isinstance(g.default_stat(), StatViolin)


# --- from test_new_geoms.py ---


def test_histogram_render():
    df = pl.DataFrame({"val": [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 5.5, 6.0, 7.0]})
    p = ggplot(df, aes(x="val")) + geom_histogram(bins=5)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_boxplot_render():
    df = pl.DataFrame(
        {
            "group": ["a"] * 10 + ["b"] * 10,
            "value": list(range(10)) + list(range(5, 15)),
        }
    )
    p = ggplot(df, aes(x="group", y="value")) + geom_boxplot()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_smooth_ols_render():
    df = pl.DataFrame(
        {
            "x": list(range(20)),
            "y": [float(i) + (i % 3) for i in range(20)],
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_smooth(method="ols")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_smooth_moving_average_render():
    df = pl.DataFrame(
        {
            "x": list(range(20)),
            "y": [float(i) * 0.5 for i in range(20)],
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_smooth(method="moving_average")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_text_render():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "lbl": ["A", "B", "C"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_text()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_label_render():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "lbl": ["A", "B", "C"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_label()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


# --- from test_v04_geoms.py ---


@pytest.fixture(params=["polars", "pandas"])
def backend(request):
    return request.param


def make_df(data: dict, backend: str):
    if backend == "polars":
        return pl.DataFrame(data)
    return pd.DataFrame(data)


def assert_renders(plot):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        plot.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_geom_area(backend):
    df = make_df({"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 5, 1]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_area()
    assert_renders(p)


def test_geom_ribbon(backend):
    df = make_df(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "lo": [1.0, 2.0, 1.5, 3.0, 0.5],
            "hi": [3.0, 5.0, 4.0, 6.0, 2.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_ribbon()
    assert_renders(p)


def test_geom_tile_plain(backend):
    df = make_df(
        {"x": [0, 1, 0, 1], "y": [0, 0, 1, 1], "val": [1.0, 2.0, 3.0, 4.0]},
        backend,
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_tile(fill="steelblue")
    assert_renders(p)


def test_geom_tile_with_labels(backend):
    df = make_df(
        {
            "x": [0, 1, 0, 1],
            "y": [0, 0, 1, 1],
            "lbl": ["A", "B", "C", "D"],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_tile(fill="lightblue")
    assert_renders(p)


def test_geom_errorbar(backend):
    df = make_df(
        {
            "x": [1, 2, 3],
            "lo": [0.5, 1.5, 2.0],
            "hi": [1.5, 3.0, 4.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_errorbar()
    assert_renders(p)


def test_geom_col(backend):
    df = make_df({"x": ["a", "b", "c"], "y": [10, 20, 15]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_col()
    assert_renders(p)


def test_geom_density_single():
    pytest.importorskip("scipy")
    df = pl.DataFrame({"x": [float(i) for i in range(50)]})
    p = ggplot(df, aes(x="x")) + geom_density()
    assert_renders(p)


def test_geom_density_grouped():
    pytest.importorskip("scipy")
    df = pl.DataFrame(
        {
            "x": [float(i) for i in range(40)],
            "g": ["a"] * 20 + ["b"] * 20,
        }
    )
    p = ggplot(df, aes(x="x", color="g")) + geom_density()
    assert_renders(p)


def test_geom_density_pandas():
    pytest.importorskip("scipy")
    df = pd.DataFrame({"x": [float(i) for i in range(50)]})
    p = ggplot(df, aes(x="x")) + geom_density()
    assert_renders(p)


def test_geom_violin():
    pytest.importorskip("scipy")

    rng = np.random.default_rng(42)
    df = pl.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_violin()
    assert_renders(p)


def test_geom_violin_pandas():
    pytest.importorskip("scipy")

    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {
            "x": ["a"] * 30 + ["b"] * 30,
            "y": rng.normal(0, 1, 60).tolist(),
        }
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_violin()
    assert_renders(p)


def test_errorbar_with_points(backend):
    df = make_df(
        {
            "x": [1, 2, 3],
            "y": [1.0, 2.5, 3.0],
            "lo": [0.5, 1.5, 2.0],
            "hi": [1.5, 3.0, 4.0],
        },
        backend,
    )
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_errorbar(ymin="lo", ymax="hi")
    assert_renders(p)


def test_area_with_refline(backend):
    df = make_df({"x": [1, 2, 3, 4], "y": [2, 4, 3, 5]}, backend)
    p = ggplot(df, aes(x="x", y="y")) + geom_area() + geom_hline(yintercept=3)
    assert_renders(p)


# --- from test_v07_geoms.py ---

"""Tests for v0.7.0 new geoms: segment, rect, step, rug, jitter."""

# --- GeomSegment ---


class TestGeomSegment:
    def test_basic_segment(self):
        df = pl.DataFrame({"x": [0, 1], "y": [0, 1], "xend": [1, 2], "yend": [1, 0]})
        p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_segment_with_arrow(self):
        df = pl.DataFrame({"x": [0], "y": [0], "xend": [1], "yend": [1]})
        p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment(arrow=True)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_segment_per_segment_color(self):
        df = pl.DataFrame(
            {"x": [0, 1], "y": [0, 1], "xend": [1, 2], "yend": [1, 0], "c": ["a", "b"]}
        )
        p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend", color="c")) + geom_segment()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_segment_with_linecollection(self):
        """Uniform color uses LineCollection path."""
        df = pl.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0], "xend": [1, 2, 3], "yend": [1, 0, 1]})
        p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment(
            color="red", alpha=0.8
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_segment_params(self):
        df = pl.DataFrame({"x": [0], "y": [0], "xend": [1], "yend": [1]})
        p = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment(
            size=2, linetype="--", alpha=0.5
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- GeomRect ---


class TestGeomRect:
    def test_basic_rect(self):
        df = pl.DataFrame({"xmin": [0, 2], "xmax": [1, 3], "ymin": [0, 1], "ymax": [1, 2]})
        p = ggplot(df, aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax")) + geom_rect()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rect_with_fill_and_color(self):
        df = pl.DataFrame({"xmin": [0], "xmax": [1], "ymin": [0], "ymax": [1], "f": ["a"]})
        p = ggplot(
            df, aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax", fill="f")
        ) + geom_rect(color="black", alpha=0.8)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rect_custom_params(self):
        df = pl.DataFrame({"xmin": [0], "xmax": [2], "ymin": [0], "ymax": [3]})
        p = ggplot(df, aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax")) + geom_rect(
            fill="blue", alpha=0.3
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- GeomStep ---


class TestGeomStep:
    def test_basic_step(self):
        df = pl.DataFrame({"x": [1, 2, 3, 4], "y": [1, 3, 2, 4]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_step_with_direction(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step(direction="pre")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_step_with_styling(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step(
            color="red", alpha=0.5, linetype="--", size=2
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_step_with_mapped_color(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "c": ["a", "a", "a"]})
        p = ggplot(df, aes(x="x", y="y", color="c")) + geom_step()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- GeomRug ---


class TestGeomRug:
    def test_basic_rug_bottom(self):
        df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 3, 5]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_rug()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rug_all_sides(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_rug(sides="bltr")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rug_left_only(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_rug(sides="l", color="red")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rug_top_right(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_rug(sides="tr", length=0.05, alpha=0.8)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rug_x_only(self):
        """Rug with only x data should draw bottom ticks."""
        df = pl.DataFrame({"x": [1, 2, 3]})
        p = ggplot(df, aes(x="x")) + geom_rug(sides="b")
        # GeomRug has no required aes, so this should work
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rug_incompatible_with_polar(self):
        """geom_rug should raise a clear error when used with polar coords."""
        from plotten._validation import RenderError
        from plotten.coords import coord_polar

        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_rug() + coord_polar()
        with pytest.raises(RenderError, match="not compatible with polar"):
            render(p)


# --- geom_jitter ---


class TestGeomJitter:
    def test_basic_jitter(self):
        df = pl.DataFrame({"x": [1, 1, 1, 2, 2, 2], "y": [1, 2, 3, 1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_jitter(seed=42)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_jitter_width_height(self):
        df = pl.DataFrame({"x": [1, 1, 2, 2], "y": [1, 2, 1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_jitter(width=0.2, height=0.1, seed=42)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_jitter_creates_layer_with_position(self):
        from plotten.positions._jitter import PositionJitter

        layer = geom_jitter(width=0.3, height=0.1, seed=42)
        assert isinstance(layer.position, PositionJitter)
        assert layer.position.width == 0.3
        assert layer.position.height == 0.1
        assert layer.position.seed == 42


# --- Factory functions ---


class TestGeomFactories:
    def test_geom_segment_factory(self):
        layer = geom_segment(arrow=True)
        assert layer.params.get("arrow") is True

    def test_geom_rect_factory(self):
        layer = geom_rect()
        from plotten.geoms._rect import GeomRect

        assert isinstance(layer.geom, GeomRect)

    def test_geom_step_factory(self):
        layer = geom_step(direction="pre")
        assert layer.params.get("direction") == "pre"

    def test_geom_rug_factory(self):
        layer = geom_rug(sides="bl", length=0.05)
        assert layer.params.get("sides") == "bl"
        assert layer.params.get("length") == 0.05


# --- from test_v08_geoms.py ---

"""Tests for v0.8.0 new geoms: path, polygon, crossbar, pointrange, linerange, hex."""


class TestGeomPath:
    def test_basic_path(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 0.5], "y": [0.0, 1.0, 0.5]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_with_color(self):
        df = pl.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(color="red")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_group_splitting(self):
        df = pl.DataFrame(
            {
                "x": [0, 1, 2, 0, 1, 2],
                "y": [0, 1, 0, 1, 0, 1],
                "g": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_path()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_supports_group_splitting(self):
        from plotten.geoms._path import GeomPath

        assert GeomPath.supports_group_splitting is True

    def test_path_with_linetype(self):
        df = pl.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(linetype="--")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_with_alpha(self):
        df = pl.DataFrame({"x": [0, 1, 2], "y": [0, 1, 0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(alpha=0.5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestGeomPolygon:
    def test_basic_polygon(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 0.5], "y": [0.0, 0.0, 1.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_polygon()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_polygon_with_fill(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 0.5], "y": [0.0, 0.0, 1.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_polygon(fill="blue", color="red")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_polygon_group_splitting(self):
        df = pl.DataFrame(
            {
                "x": [0.0, 1.0, 0.5, 2.0, 3.0, 2.5],
                "y": [0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
                "g": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", group="g")) + geom_polygon()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_polygon_supports_group_splitting(self):
        from plotten.geoms._polygon import GeomPolygon

        assert GeomPolygon.supports_group_splitting is True

    def test_polygon_with_alpha(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 0.5], "y": [0.0, 0.0, 1.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_polygon(alpha=0.3)
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestGeomCrossbar:
    def test_basic_crossbar(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [5, 7, 6], "ymin": [3, 5, 4], "ymax": [7, 9, 8]})
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_crossbar()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_crossbar_with_params(self):
        df = pl.DataFrame({"x": [1], "y": [5], "ymin": [3], "ymax": [7]})
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_crossbar(
            width=0.3, fill="skyblue", color="navy"
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_crossbar_y_limits_include_ymin_ymax(self):
        """Regression: y-axis must encompass ymin/ymax, not just y."""
        df = pl.DataFrame({"x": [1, 2], "y": [5, 8], "ymin": [2, 5], "ymax": [8, 11]})
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_crossbar()
        from plotten._render._resolve import resolve

        resolved = resolve(p)
        y_scale = resolved.scales["y"]
        lo, hi = y_scale.get_limits()
        assert lo <= 2, f"y-axis lower limit {lo} does not include ymin=2"
        assert hi >= 11, f"y-axis upper limit {hi} does not include ymax=11"

    def test_crossbar_no_group_splitting(self):
        from plotten.geoms._crossbar import GeomCrossbar

        assert GeomCrossbar.supports_group_splitting is False

    def test_crossbar_multiple_points(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [5, 7, 6, 8],
                "ymin": [3, 5, 4, 6],
                "ymax": [7, 9, 8, 10],
            }
        )
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_crossbar()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestGeomPointrange:
    def test_basic_pointrange(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [5, 7, 6], "ymin": [3, 5, 4], "ymax": [7, 9, 8]})
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_pointrange()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_pointrange_with_params(self):
        df = pl.DataFrame({"x": [1], "y": [5], "ymin": [3], "ymax": [7]})
        p = ggplot(df, aes(x="x", y="y", ymin="ymin", ymax="ymax")) + geom_pointrange(
            color="red", size=50
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_pointrange_no_group_splitting(self):
        from plotten.geoms._pointrange import GeomPointrange

        assert GeomPointrange.supports_group_splitting is False


class TestGeomLinerange:
    def test_basic_linerange(self):
        df = pl.DataFrame({"x": [1, 2, 3], "ymin": [3, 5, 4], "ymax": [7, 9, 8]})
        p = ggplot(df, aes(x="x", ymin="ymin", ymax="ymax")) + geom_linerange()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_linerange_with_params(self):
        df = pl.DataFrame({"x": [1, 2], "ymin": [1, 2], "ymax": [5, 6]})
        p = ggplot(df, aes(x="x", ymin="ymin", ymax="ymax")) + geom_linerange(
            color="green", linewidth=2
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_linerange_no_group_splitting(self):
        from plotten.geoms._linerange import GeomLinerange

        assert GeomLinerange.supports_group_splitting is False


class TestGeomHex:
    def test_basic_hex(self):

        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(100).tolist(), "y": np.random.randn(100).tolist()})
        p = ggplot(df, aes(x="x", y="y")) + geom_hex()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_hex_with_bins(self):

        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(50).tolist(), "y": np.random.randn(50).tolist()})
        p = ggplot(df, aes(x="x", y="y")) + geom_hex(bins=10)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_hex_no_group_splitting(self):
        from plotten.geoms._hex import GeomHex

        assert GeomHex.supports_group_splitting is False


# --- from test_v10_geoms.py ---

"""Tests for Phase 3: New Geoms & Stats (3A-3D)."""

# --- 3A: geom_curve ---


class TestGeomCurve:
    def test_required_aes(self):
        assert GeomCurve.required_aes == frozenset({"x", "y", "xend", "yend"})

    def test_renders(self):
        df = pl.DataFrame(
            {
                "x": [0.0, 1.0],
                "y": [0.0, 1.0],
                "xend": [1.0, 2.0],
                "yend": [1.0, 0.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_curve()
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_curvature_param(self):
        df = pl.DataFrame(
            {
                "x": [0.0],
                "y": [0.0],
                "xend": [1.0],
                "yend": [1.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_curve(curvature=0.5)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 3B: geom_spoke ---


class TestGeomSpoke:
    def test_required_aes(self):
        assert GeomSpoke.required_aes == frozenset({"x", "y", "angle", "radius"})

    def test_renders(self):
        df = pl.DataFrame(
            {
                "x": [0.0, 1.0],
                "y": [0.0, 1.0],
                "angle": [0.0, math.pi / 4],
                "radius": [1.0, 0.5],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", angle="angle", radius="radius")) + geom_spoke()
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_arrow_param(self):
        df = pl.DataFrame(
            {
                "x": [0.0],
                "y": [0.0],
                "angle": [0.0],
                "radius": [1.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", angle="angle", radius="radius")) + geom_spoke(
            arrow=True
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 3C: geom_dotplot ---


class TestGeomDotplot:
    def test_stat_dotplot(self):

        df = pd.DataFrame({"x": [1.0, 1.1, 2.0, 2.1, 2.2, 3.0]})
        stat = StatDotplot(bins=3)
        result = cast("nw.DataFrame", stat.compute(df))
        assert "x" in result.columns
        assert "y" in result.columns

    def test_renders(self):
        df = pl.DataFrame({"x": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 2.0, 2.5]})
        plot = ggplot(df, aes(x="x")) + geom_dotplot(bins=5)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 3D: stat_summary_bin ---


class TestStatSummaryBin:
    def test_stat_summary_bin_compute(self):

        df = pd.DataFrame(
            {
                "x": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                "y": [10.0, 12.0, 20.0, 22.0, 30.0, 32.0],
            }
        )
        stat = StatSummaryBin(bins=3)
        result = cast("nw.DataFrame", stat.compute(df))
        assert "x" in result.columns
        assert "y" in result.columns
        assert "ymin" in result.columns
        assert "ymax" in result.columns

    def test_renders(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                "y": [10.0, 12.0, 20.0, 22.0, 30.0, 32.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y")) + stat_summary_bin(bins=3)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- from test_v110_geoms.py ---

"""Tests for Phase 3 of v1.1.0: geom_quantile, stat_quantile, position_dodge2."""

# ---------------------------------------------------------------------------
# StatQuantile
# ---------------------------------------------------------------------------


class TestStatQuantile:
    def test_default_quantiles(self):
        stat = StatQuantile()
        assert stat.quantiles == [0.25, 0.5, 0.75]
        assert stat.n_points == 100

    def test_custom_quantiles(self):
        stat = StatQuantile(quantiles=[0.1, 0.9], n_points=50)
        assert stat.quantiles == [0.1, 0.9]
        assert stat.n_points == 50

    def test_required_aes(self):
        stat = StatQuantile()
        assert stat.required_aes == frozenset({"x", "y"})

    def test_compute_produces_correct_columns(self):

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        stat = StatQuantile(quantiles=[0.25, 0.5, 0.75], n_points=20)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))

        cols = set(result.columns)
        assert "x" in cols
        assert "y" in cols
        assert "group" in cols

    def test_compute_output_length(self):

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        n_points = 20
        quantiles = [0.25, 0.5, 0.75]
        stat = StatQuantile(quantiles=quantiles, n_points=n_points)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))

        expected_len = n_points * len(quantiles)
        assert len(result) == expected_len

    def test_compute_groups_match_quantiles(self):

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        quantiles = [0.1, 0.5, 0.9]
        stat = StatQuantile(quantiles=quantiles, n_points=20)
        result = cast("nw.DataFrame", nw.from_native(stat.compute(df)))

        groups = sorted(set(result.get_column("group").to_list()))
        assert groups == sorted(quantiles)

    def test_quantile_regression_linear_data(self):
        """With perfectly linear data, all quantile lines should have similar slopes."""
        x = np.arange(0.0, 10.0, 0.1)
        y = 3.0 * x + 5.0
        slope, intercept = StatQuantile._quantile_regression(x, y, 0.5)
        assert abs(slope - 3.0) < 0.1
        assert abs(intercept - 5.0) < 0.5

    def test_median_quantile_close_to_ols_for_symmetric_noise(self):
        """For symmetric noise, median regression should be close to OLS."""
        rng = np.random.default_rng(123)
        x = np.linspace(0, 10, 200)
        y = 2.0 * x + 1.0 + rng.normal(0, 0.5, 200)
        slope, intercept = StatQuantile._quantile_regression(x, y, 0.5)
        assert abs(slope - 2.0) < 0.3
        assert abs(intercept - 1.0) < 1.0


# ---------------------------------------------------------------------------
# GeomQuantile
# ---------------------------------------------------------------------------


class TestGeomQuantile:
    def test_required_aes(self):
        geom = GeomQuantile()
        assert geom.required_aes == frozenset({"x", "y"})

    def test_supports_group_splitting(self):
        geom = GeomQuantile()
        assert geom.supports_group_splitting is True

    def test_default_stat_is_stat_quantile(self):
        geom = GeomQuantile()
        stat = geom.default_stat()
        assert isinstance(stat, StatQuantile)
        assert stat.quantiles == [0.25, 0.5, 0.75]

    def test_custom_quantiles_passed_to_stat(self):
        geom = GeomQuantile(quantiles=[0.1, 0.9], n_points=50)
        stat = geom.default_stat()
        assert stat.quantiles == [0.1, 0.9]
        assert stat.n_points == 50

    def test_draw(self):
        """GeomQuantile.draw should call ax.plot."""

        fig, ax = plt.subplots()
        geom = GeomQuantile()
        data = cast("GeomDrawData", {"x": [1, 2, 3], "y": [2, 4, 6]})
        geom.draw(data, ax, cast("GeomParams", {}))
        # Should have drawn one line
        assert len(ax.lines) == 1
        plt.close(fig)

    def test_draw_with_params(self):
        """GeomQuantile.draw should pass through aesthetic params."""

        fig, ax = plt.subplots()
        geom = GeomQuantile()
        data = cast("GeomDrawData", {"x": [1, 2, 3], "y": [2, 4, 6]})
        geom.draw(data, ax, cast("GeomParams", {"color": "red", "alpha": 0.5, "size": 2}))
        line = ax.lines[0]
        assert line.get_alpha() == 0.5
        assert line.get_linewidth() == 2
        plt.close(fig)


# ---------------------------------------------------------------------------
# PositionDodge2
# ---------------------------------------------------------------------------


class TestPositionDodge2:
    def test_default_params(self):
        pos = PositionDodge2()
        assert pos.width == 0.9
        assert pos.padding == 0.1

    def test_custom_params(self):
        pos = PositionDodge2(width=0.8, padding=0.2)
        assert pos.width == 0.8
        assert pos.padding == 0.2

    def test_no_x_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"y": [1, 2, 3]}
        result = pos.adjust(data, {})
        assert result == data

    def test_no_group_key_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"x": [1, 2, 3]}
        result = pos.adjust(data, {})
        assert result == data

    def test_single_group_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"x": [1, 2, 3], "fill": ["a", "a", "a"]}
        result = pos.adjust(data, {})
        assert result["x"] == [1, 2, 3]

    def test_two_groups_dodge(self):
        pos = PositionDodge2(width=0.9, padding=0.0)
        data = {"x": [1, 1], "fill": ["a", "b"]}
        params: dict = {}
        result = pos.adjust(data, params)
        # With padding=0, element_width = 0.9 / 2 = 0.45
        # offsets: -0.225, +0.225
        assert len(result["x"]) == 2
        assert result["x"][0] < 1.0
        assert result["x"][1] > 1.0
        # Check symmetry
        assert abs((result["x"][0] + result["x"][1]) / 2 - 1.0) < 1e-10
        # Check that width is set in params
        assert "width" in params

    def test_dodge2_narrower_than_dodge_with_padding(self):
        """With padding > 0, dodge2 element width should be narrower than dodge."""
        dodge = PositionDodge(width=0.9)
        dodge2 = PositionDodge2(width=0.9, padding=0.3)

        data = {"x": [1, 1, 1], "fill": ["a", "b", "c"]}
        params_d: dict = {}
        params_d2: dict = {}
        dodge.adjust(dict(data), params_d)
        dodge2.adjust(dict(data), params_d2)

        # dodge width = 0.9 / 3 = 0.3
        # dodge2 width = 0.9 * (1 - 0.3) / 3 = 0.21
        assert params_d2["width"] < params_d["width"]

    def test_missing_categories_centered(self):
        """When not all groups are present at every x, bars should still be centered."""
        pos = PositionDodge2(width=0.9, padding=0.0)
        data = {
            "x": [1, 1, 1, 2, 2],
            "y": [10, 20, 30, 40, 50],
            "fill": ["a", "b", "c", "a", "b"],
        }
        params: dict = {}
        result = pos.adjust(data, params)
        x_at_2 = [result["x"][i] for i in (3, 4)]
        center = sum(x_at_2) / len(x_at_2)
        assert center == pytest.approx(2.0), f"Bars at x=2 not centered: {x_at_2}"

    def test_position_dodge2_factory(self):
        pos = position_dodge2(width=0.8, padding=0.15)
        assert isinstance(pos, PositionDodge2)
        assert pos.width == 0.8
        assert pos.padding == 0.15


# ---------------------------------------------------------------------------
# geom_quantile factory
# ---------------------------------------------------------------------------


class TestGeomQuantileFactory:
    def test_geom_quantile_returns_layer(self):
        from plotten._layer import Layer
        from plotten.geoms import geom_quantile

        layer = geom_quantile()
        assert isinstance(layer, Layer)
        assert isinstance(layer.geom, GeomQuantile)
        assert isinstance(layer.stat, StatQuantile)

    def test_geom_quantile_custom_quantiles(self):

        layer = geom_quantile(quantiles=[0.1, 0.9])
        assert isinstance(layer.stat, StatQuantile)
        assert layer.stat.quantiles == [0.1, 0.9]

    def test_geom_quantile_custom_n_points(self):

        layer = geom_quantile(n_points=50)
        assert isinstance(layer.stat, StatQuantile)
        assert layer.stat.n_points == 50


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------


class TestExports:
    def test_stat_quantile_in_stats_init(self):
        from plotten.stats import StatQuantile as _S

        assert _S is StatQuantile

    def test_geom_quantile_in_geoms_init(self):
        from plotten.geoms import GeomQuantile as _G

        assert _G is GeomQuantile

    def test_position_dodge2_in_positions_init(self):
        from plotten.positions import PositionDodge2 as _P
        from plotten.positions import position_dodge2 as _f

        assert _P is PositionDodge2
        assert _f is position_dodge2

    def test_top_level_exports(self):
        import plotten

        assert hasattr(plotten, "geom_quantile")
        assert hasattr(plotten, "PositionDodge2")
        assert hasattr(plotten, "position_dodge2")


# --- from test_v12_count.py ---

"""Tests for geom_count / stat_sum."""


class TestStatCountOverlap:
    def test_compute_counts(self):
        df = pd.DataFrame({"x": [1, 1, 2, 2, 2, 3], "y": [1, 1, 2, 2, 2, 3]})
        stat = StatCountOverlap()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        assert "n" in frame.columns
        counts = dict(
            zip(
                frame.get_column("x").to_list(),
                frame.get_column("n").to_list(),
                strict=True,
            )
        )
        assert counts[1] == 2
        assert counts[2] == 3
        assert counts[3] == 1

    def test_unique_points(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        stat = StatCountOverlap()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        assert all(n == 1 for n in frame.get_column("n").to_list())


class TestGeomCount:
    def test_renders(self):
        df = pd.DataFrame(
            {
                "x": [1, 1, 1, 2, 2, 3],
                "y": [1, 1, 1, 2, 2, 3],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_count()
        fig = render(p)
        assert fig is not None

    def test_stat_sum_alias(self):
        """stat_sum should produce the same result as geom_count."""
        df = pd.DataFrame({"x": [1, 1, 2], "y": [1, 1, 2]})
        p = ggplot(df, Aes(x="x", y="y")) + stat_sum()
        fig = render(p)
        assert fig is not None


# --- from test_v09_contour_density2d.py ---

"""Tests for contour, raster, and density 2d geoms/stats."""


def _grid_data():
    """Create simple gridded test data."""
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    xx, yy = np.meshgrid(x, y)
    zz = np.exp(-(xx**2 + yy**2))
    return pd.DataFrame({"x": xx.ravel(), "y": yy.ravel(), "z": zz.ravel()})


def _scatter_data(n=200):
    """Create scatter data for density estimation."""
    rng = np.random.default_rng(42)
    return pd.DataFrame({"x": rng.normal(0, 1, n), "y": rng.normal(0, 1, n)})


class TestStatContour:
    def test_compute(self):
        df = _grid_data()
        stat = StatContour(bins=5)
        result = cast("nw.DataFrame", stat.compute(df))
        assert "x" in result.columns
        assert "y" in result.columns
        assert "z" in result.columns
        assert len(result) > 0

    def test_required_aes(self):
        assert StatContour.required_aes == frozenset({"x", "y", "z"})


class TestStatDensity2d:
    def test_compute(self):
        df = _scatter_data()
        stat = StatDensity2d(n=50)
        result = cast("nw.DataFrame", stat.compute(df))
        assert "x" in result.columns
        assert "y" in result.columns
        assert "z" in result.columns
        assert len(result) == 50 * 50

    def test_required_aes(self):
        assert StatDensity2d.required_aes == frozenset({"x", "y"})

    def test_custom_n(self):
        df = _scatter_data()
        stat = StatDensity2d(n=30)
        result = cast("nw.DataFrame", stat.compute(df))
        assert len(result) == 30 * 30


class TestGeomContour:
    def test_contour_renders(self):
        df = _grid_data()
        p = ggplot(df, Aes(x="x", y="y", z="z")) + geom_contour()
        fig = render(p)
        assert fig is not None

    def test_contour_filled_renders(self):
        df = _grid_data()
        p = ggplot(df, Aes(x="x", y="y", z="z")) + geom_contour_filled()
        fig = render(p)
        assert fig is not None


class TestGeomRaster:
    def test_raster_renders(self):
        x = np.linspace(0, 1, 10)
        y = np.linspace(0, 1, 10)
        xx, yy = np.meshgrid(x, y)
        df = pd.DataFrame(
            {
                "x": xx.ravel(),
                "y": yy.ravel(),
                "z": (xx + yy).ravel(),
            }
        )
        p = ggplot(df, Aes(x="x", y="y", z="z")) + geom_raster()
        fig = render(p)
        assert fig is not None


class TestDensity2d:
    def test_stat_density_2d_renders(self):
        df = _scatter_data()
        p = ggplot(df, Aes(x="x", y="y")) + stat_density_2d()
        fig = render(p)
        assert fig is not None

    def test_stat_density_2d_filled_renders(self):
        df = _scatter_data()
        p = ggplot(df, Aes(x="x", y="y")) + stat_density_2d_filled()
        fig = render(p)
        assert fig is not None


class TestAesZ:
    def test_z_field_exists(self):

        a = Aes(z="elevation")
        assert a.z == "elevation"

    def test_z_default_none(self):

        a = Aes()
        assert a.z is None


# --- from test_v12_ellipse.py ---

"""Tests for stat_ellipse confidence ellipses."""


class TestStatEllipse:
    def test_renders(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 50), "y": rng.normal(0, 1, 50)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_ellipse()
        fig = render(p)
        assert fig is not None

    def test_custom_level(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 50), "y": rng.normal(0, 1, 50)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_ellipse(level=0.99)
        fig = render(p)
        assert fig is not None

    def test_compute_returns_ellipse_points(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 100), "y": rng.normal(0, 1, 100)})
        stat = StatEllipse(level=0.95, segments=51)
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        assert len(frame) == 51
        assert "x" in frame.columns
        assert "y" in frame.columns

    def test_ellipse_centered_near_mean(self):
        rng = np.random.default_rng(42)
        x = rng.normal(5, 1, 200)
        y = rng.normal(10, 1, 200)
        df = pd.DataFrame({"x": x, "y": y})
        stat = StatEllipse()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        ex = frame.get_column("x").to_list()
        ey = frame.get_column("y").to_list()
        # Center of ellipse should be near (5, 10)
        assert abs(np.mean(ex) - 5) < 0.5
        assert abs(np.mean(ey) - 10) < 0.5

    def test_too_few_points(self):
        """With fewer than 3 points, return empty frame."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        stat = StatEllipse()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        assert len(frame) == 0

    def test_correlated_data(self):
        """Ellipse for correlated data should be elongated."""
        rng = np.random.default_rng(42)
        x = rng.normal(0, 1, 200)
        y = x * 2 + rng.normal(0, 0.1, 200)
        df = pd.DataFrame({"x": x, "y": y})
        stat = StatEllipse()
        result = cast("nw.DataFrame", stat.compute(df))
        frame = cast("nw.DataFrame", nw.from_native(result))
        ex = np.array(frame.get_column("x").to_list())
        ey = np.array(frame.get_column("y").to_list())
        # The y range should be much larger than x range
        assert (ey.max() - ey.min()) > (ex.max() - ex.min())
