"""Tests for Phase 3: New Geoms & Stats (3A-3D)."""

import math

import matplotlib.pyplot as plt
import polars as pl

from plotten import aes, geom_curve, geom_dotplot, geom_spoke, ggplot, stat_summary_bin
from plotten._render._mpl import render
from plotten.geoms._curve import GeomCurve
from plotten.geoms._spoke import GeomSpoke
from plotten.stats._dotplot import StatDotplot
from plotten.stats._summary_bin import StatSummaryBin

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
        import pandas as pd

        df = pd.DataFrame({"x": [1.0, 1.1, 2.0, 2.1, 2.2, 3.0]})
        stat = StatDotplot(bins=3)
        result = stat.compute(df)
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
        import pandas as pd

        df = pd.DataFrame(
            {
                "x": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                "y": [10.0, 12.0, 20.0, 22.0, 30.0, 32.0],
            }
        )
        stat = StatSummaryBin(bins=3)
        result = stat.compute(df)
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
