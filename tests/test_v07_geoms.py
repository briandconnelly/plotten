"""Tests for v0.7.0 new geoms: segment, rect, step, rug, jitter."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import (
    aes,
    geom_jitter,
    geom_point,
    geom_rect,
    geom_rug,
    geom_segment,
    geom_step,
    ggplot,
)
from plotten._render._mpl import render

matplotlib.use("Agg")


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
