"""Tests for contour, raster, and density 2d geoms/stats."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd

from plotten import (
    Aes,
    geom_contour,
    geom_contour_filled,
    geom_raster,
    ggplot,
    stat_density_2d,
    stat_density_2d_filled,
)
from plotten._render._mpl import render
from plotten.stats._contour import StatContour
from plotten.stats._density2d import StatDensity2d


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
        result = stat.compute(df)
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
        result = stat.compute(df)
        assert "x" in result.columns
        assert "y" in result.columns
        assert "z" in result.columns
        assert len(result) == 50 * 50

    def test_required_aes(self):
        assert StatDensity2d.required_aes == frozenset({"x", "y"})

    def test_custom_n(self):
        df = _scatter_data()
        stat = StatDensity2d(n=30)
        result = stat.compute(df)
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
        from plotten._aes import Aes

        a = Aes(z="elevation")
        assert a.z == "elevation"

    def test_z_default_none(self):
        from plotten._aes import Aes

        a = Aes()
        assert a.z is None
