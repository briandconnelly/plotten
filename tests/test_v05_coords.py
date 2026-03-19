"""Tests for v0.5 coord_equal and coord_fixed."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

matplotlib.use("Agg")

from plotten import aes, coord_equal, coord_fixed, geom_point, ggplot
from plotten.coords._equal import CoordEqual, CoordFixed


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
