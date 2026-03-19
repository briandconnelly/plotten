"""Tests for v0.8.0 group splitting and multi-series rendering."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import (
    aes,
    geom_area,
    geom_density,
    geom_line,
    geom_point,
    geom_step,
    ggplot,
)
from plotten._render._mpl import render
from plotten._render._resolve import _detect_group_key, _split_by_group, resolve

matplotlib.use("Agg")


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
        from plotten.geoms._point import GeomPoint

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
