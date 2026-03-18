"""Tests for v0.8.0 new geoms: path, polygon, crossbar, pointrange, linerange, hex."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import (
    aes,
    geom_crossbar,
    geom_hex,
    geom_linerange,
    geom_path,
    geom_pointrange,
    geom_polygon,
    ggplot,
)
from plotten._render._mpl import render

matplotlib.use("Agg")


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
        import numpy as np

        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(100).tolist(), "y": np.random.randn(100).tolist()})
        p = ggplot(df, aes(x="x", y="y")) + geom_hex()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_hex_with_bins(self):
        import numpy as np

        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(50).tolist(), "y": np.random.randn(50).tolist()})
        p = ggplot(df, aes(x="x", y="y")) + geom_hex(bins=10)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_hex_no_group_splitting(self):
        from plotten.geoms._hex import GeomHex

        assert GeomHex.supports_group_splitting is False
