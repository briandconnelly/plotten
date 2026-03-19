"""Tests for Phase 1 of v0.14.0: geom_freqpoly, geom_area, geom_errorbarh."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

import polars as pl

import plotten
from plotten._layer import Layer
from plotten._render._mpl import render
from plotten.geoms._errorbarh import GeomErrorbarH
from plotten.geoms._freqpoly import GeomFreqpoly
from plotten.stats._bin import StatBin
from plotten.stats._identity import StatIdentity

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
        data = {"x": [1.0, 2.0, 3.0], "y": [5, 10, 3]}
        g.draw(data, ax, {})
        # Should produce one Line2D artist
        assert len(ax.lines) == 1
        plt.close(fig)

    def test_draw_with_color_and_params(self):
        g = GeomFreqpoly()
        fig, ax = plt.subplots()
        data = {"x": [1.0, 2.0, 3.0], "y": [5, 10, 3], "color": "red"}
        g.draw(data, ax, {"alpha": 0.5})
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
        data = {"y": [1.0, 2.0], "xmin": [0.5, 1.5], "xmax": [1.5, 2.5]}
        g.draw(data, ax, {})
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
