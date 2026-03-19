"""Tests for coord_cartesian (zoom without data loss)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest

from plotten import Aes, coord_cartesian, geom_point, ggplot
from plotten._render._mpl import render
from plotten.coords._cartesian import CoordCartesian


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
