from __future__ import annotations

import os
import tempfile

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import (
    Aes,
    aes,
    coord_cartesian,
    coord_equal,
    coord_fixed,
    coord_flip,
    coord_polar,
    coord_trans,
    geom_bar,
    geom_line,
    geom_point,
    ggplot,
    theme,
)
from plotten._render._mpl import render
from plotten._validation import ConfigError
from plotten.coords._cartesian import CoordCartesian
from plotten.coords._equal import CoordEqual, CoordFixed
from plotten.coords._polar import CoordPolar
from plotten.coords._trans import CoordTrans

# --- from test_coord_flip.py ---


def _save_and_check(p):
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
    _save_and_check(p)


def test_coord_flip_scatter():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + coord_flip()
    _save_and_check(p)


def test_coord_cartesian_xlim():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + CoordCartesian(xlim=(0, 10))
    _save_and_check(p)


def test_coord_cartesian_ylim():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + CoordCartesian(ylim=(-1, 8))
    _save_and_check(p)


# --- from test_v05_coords.py ---

"""Tests for v0.5 coord_equal and coord_fixed."""


class TestCoordEqual:
    def test_sets_aspect(self):
        fig, ax = plt.subplots()
        coord = CoordEqual()
        coord.transform(None, ax)
        # matplotlib may return "equal" or 1.0
        assert ax.get_aspect() in ("equal", 1.0)
        plt.close(fig)

    def test_with_limits(self):
        fig, ax = plt.subplots()
        coord = CoordEqual(xlim=(0, 10), ylim=(0, 5))
        coord.transform(None, ax)
        assert ax.get_xlim() == (0, 10)
        assert ax.get_ylim() == (0, 5)
        plt.close(fig)

    def test_convenience(self):
        c = coord_equal()
        assert isinstance(c, CoordEqual)


class TestCoordFixed:
    def test_sets_aspect_ratio(self):
        fig, ax = plt.subplots()
        coord = CoordFixed(ratio=2)
        coord.transform(None, ax)
        assert ax.get_aspect() == 2
        plt.close(fig)

    def test_convenience(self):
        c = coord_fixed(ratio=0.5)
        assert isinstance(c, CoordFixed)
        assert c.ratio == 0.5


class TestCoordIntegration:
    def test_coord_equal_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + coord_equal()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_coord_fixed_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + coord_fixed(ratio=2)
        fig = p._repr_png_()
        assert len(fig) > 0


# --- from test_v09_coord_cartesian.py ---

"""Tests for coord_cartesian (zoom without data loss)."""


class TestCoordCartesian:
    def test_factory_creates_instance(self):
        c = coord_cartesian(xlim=(2, 8))
        assert isinstance(c, CoordCartesian)
        assert c.xlim == (2, 8)
        assert c.ylim is None

    def test_default_params(self):
        c = coord_cartesian()
        assert c.xlim is None
        assert c.ylim is None
        assert c.expand is None
        assert c.clip is True

    def test_xlim_zoom(self):
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_cartesian(xlim=(2, 8))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_xlim()
        assert lo == pytest.approx(2.0)
        assert hi == pytest.approx(8.0)

    def test_ylim_zoom(self):
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_cartesian(ylim=(3, 7))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_ylim()
        assert lo == pytest.approx(3.0)
        assert hi == pytest.approx(7.0)

    def test_both_limits(self):
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + coord_cartesian(xlim=(1, 5), ylim=(2, 6))
        )
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_xlim() == pytest.approx((1.0, 5.0))
        assert ax.get_ylim() == pytest.approx((2.0, 6.0))

    def test_expand_param(self):
        c = coord_cartesian(expand=(0.1, 0))
        assert c.expand == (0.1, 0)

    def test_clip_param(self):
        c = coord_cartesian(clip=False)
        assert c.clip is False

    def test_zoom_does_not_drop_data(self):
        """coord_cartesian should zoom visually without affecting stats."""
        df = pd.DataFrame({"x": range(20), "y": range(20)})
        # With coord_cartesian zoom, all data points are still there
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_cartesian(xlim=(5, 15))
        fig = render(p)
        ax = fig.axes[0]
        # All 20 data points should be plotted
        n_points = len(ax.collections[0].get_offsets())  # type: ignore[arg-type]
        assert n_points == 20

    def test_replaces_default_coord(self):
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p2 = p + coord_cartesian(xlim=(0, 10))
        assert isinstance(p2.coord, CoordCartesian)
        assert p2.coord.xlim == (0, 10)


# --- from test_v09_coord_polar.py ---

"""Tests for coord_polar."""


class TestCoordPolar:
    def test_factory(self):
        c = coord_polar()
        assert isinstance(c, CoordPolar)
        assert c.theta == "x"
        assert c.start == 0
        assert c.direction == 1

    def test_theta_y(self):
        c = coord_polar(theta="y")
        assert c.theta == "y"

    def test_custom_start(self):
        c = coord_polar(start=np.pi / 2)
        assert c.start == pytest.approx(np.pi / 2)

    def test_counterclockwise(self):
        c = coord_polar(direction=-1)
        assert c.direction == -1

    def test_polar_axes_created(self):
        df = pd.DataFrame({"x": range(6), "y": [1, 2, 3, 4, 5, 6]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar()
        fig = render(p)
        ax = fig.axes[0]
        assert ax.name == "polar"

    def test_polar_with_line(self):
        angles = np.linspace(0, 2 * np.pi, 50)
        df = pd.DataFrame({"x": angles, "y": np.abs(np.sin(2 * angles))})
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + coord_polar()
        fig = render(p)
        assert fig is not None
        assert fig.axes[0].name == "polar"

    def test_polar_with_bar(self):
        """Pie-chart style: bars in polar coords."""
        df = pd.DataFrame({"x": ["A", "B", "C"], "y": [30, 50, 20]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_bar() + coord_polar()
        fig = render(p)
        assert fig is not None
        assert fig.axes[0].name == "polar"

    def test_polar_direction(self):
        df = pd.DataFrame({"x": range(4), "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar(direction=-1)
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_theta_direction() == -1  # type: ignore[attr-defined]

    def test_polar_start_offset(self):
        df = pd.DataFrame({"x": range(4), "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar(start=np.pi / 2)
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_theta_offset() == pytest.approx(np.pi / 2)  # type: ignore[attr-defined]

    def test_plot_addition(self):
        """CoordPolar should be addable to a plot."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p2 = p + coord_polar()
        assert isinstance(p2.coord, CoordPolar)

    def test_radar_style(self):
        """Radar/spider chart pattern."""
        categories = list(range(5))
        values = [3, 4, 2, 5, 1]
        # Close the polygon
        df = pd.DataFrame(
            {
                "x": [*categories, categories[0]],
                "y": [*values, values[0]],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + coord_polar()
        fig = render(p)
        assert fig is not None


# --- from test_v13_coords_legend.py ---

"""Tests for v0.13.0 coord_trans and legend positioning."""


class TestCoordTrans:
    def test_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans()
        fig = render(p)
        assert fig is not None

    def test_sqrt_y(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 4, 9, 16]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(y="sqrt")
        fig = render(p)
        assert fig is not None

    def test_log10_x(self):
        df = pd.DataFrame({"x": [1, 10, 100, 1000], "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(x="log10")
        fig = render(p)
        assert fig is not None

    def test_callable_transform(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(y=lambda v: v**2)
        fig = render(p)
        assert fig is not None

    def test_reverse_transform(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(x="reverse")
        fig = render(p)
        assert fig is not None

    def test_unknown_transform_raises(self):
        ct = CoordTrans(x="bogus")
        with pytest.raises(ConfigError, match="Unknown transform"):
            ct._apply([1, 2, 3], "bogus")

    def test_transform_data(self):
        ct = CoordTrans(x="log10", y="sqrt")
        data = {"x": [10, 100], "y": [4, 9]}
        result = ct.transform_data(data, {})
        assert abs(result["x"][0] - 1.0) < 0.01
        assert abs(result["y"][0] - 2.0) < 0.01


class TestLegendPosition:
    def test_tuple_position(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_position=(0.8, 0.2))
        )
        fig = render(p)
        assert fig is not None

    def test_tuple_position_top_left(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_position=(0.1, 0.9))
        )
        fig = render(p)
        assert fig is not None

    def test_string_position_still_works(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "c"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point() + theme(legend_position="left")
        fig = render(p)
        assert fig is not None


# ---------------------------------------------------------------------------
# CoordFlip edge cases
# ---------------------------------------------------------------------------


class TestCoordFlipEdgeCases:
    """Test CoordFlip with data that has only x or only y."""

    def test_flip_resolved_x_only(self):
        """When layer data has only 'x', flip should rename to 'y'."""
        from plotten._render._structures import ResolvedLayer, ResolvedPanel, ResolvedPlot
        from plotten.coords._flip import CoordFlip
        from plotten.geoms._point import GeomPoint
        from plotten.themes._theme import Theme

        layer = ResolvedLayer(geom=GeomPoint(), data={"x": [1, 2, 3]}, params={})
        panel = ResolvedPanel(label="", layers=[layer], scales={})
        resolved = ResolvedPlot(
            panels=[panel],
            scales={},
            coord=CoordFlip(),
            theme=Theme(),
        )
        result = CoordFlip.flip_resolved(resolved)
        assert "y" in result.panels[0].layers[0].data
        assert "x" not in result.panels[0].layers[0].data

    def test_flip_resolved_y_only(self):
        """When layer data has only 'y', flip should rename to 'x'."""
        from plotten._render._structures import ResolvedLayer, ResolvedPanel, ResolvedPlot
        from plotten.coords._flip import CoordFlip
        from plotten.geoms._point import GeomPoint
        from plotten.themes._theme import Theme

        layer = ResolvedLayer(geom=GeomPoint(), data={"y": [1, 2, 3]}, params={})
        panel = ResolvedPanel(label="", layers=[layer], scales={})
        resolved = ResolvedPlot(
            panels=[panel],
            scales={},
            coord=CoordFlip(),
            theme=Theme(),
        )
        result = CoordFlip.flip_resolved(resolved)
        assert "x" in result.panels[0].layers[0].data
        assert "y" not in result.panels[0].layers[0].data

    def test_flip_transform_passthrough(self):
        """CoordFlip.transform() is a no-op identity."""
        from plotten.coords._flip import CoordFlip

        fig, ax = plt.subplots()
        coord = CoordFlip()
        data = {"x": [1, 2]}
        result = coord.transform(data, ax)
        assert result is data
        plt.close(fig)
