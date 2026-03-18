"""Additional tests to bring v0.5 coverage to 95%+."""

from __future__ import annotations

import datetime

import matplotlib
import polars as pl

matplotlib.use("Agg")

from plotten import (
    aes,
    geom_col,
    geom_histogram,
    geom_line,
    geom_point,
    ggplot,
    scale_alpha_continuous,
    scale_linetype_discrete,
    scale_shape_discrete,
)
from plotten.positions import PositionDodge, PositionFill, PositionStack
from plotten.scales._base import auto_scale


class TestGeomPointBranches:
    def test_shape_with_color_list(self):
        """Test per-point shapes with per-point colors."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 2, 3, 4],
                "g": ["a", "b", "a", "b"],
                "z": [10, 20, 30, 40],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", color="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_shape_with_size_list(self):
        """Test per-point shapes with per-point sizes."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "a"],
                "z": [10, 20, 30],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", size="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_shape_with_alpha_list(self):
        """Test per-point shapes with per-point alpha."""
        df = pl.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "a"],
                "z": [10, 50, 100],
            }
        )
        p = ggplot(df, aes(x="x", y="y", shape="g", alpha="z")) + geom_point()
        assert len(p._repr_png_()) > 0

    def test_point_with_param_size(self):
        """Test geom_point with size as a param, not aesthetic."""
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point(size=50)
        assert len(p._repr_png_()) > 0

    def test_point_with_param_alpha(self):
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point(alpha=0.5)
        assert len(p._repr_png_()) > 0


class TestGeomLineBranches:
    def test_line_with_alpha_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(alpha=0.5)
        assert len(p._repr_png_()) > 0

    def test_line_with_linetype_mapped(self):
        """Mapped linetype (list of strings)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "a", "a"]})
        p = ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line()
        assert len(p._repr_png_()) > 0

    def test_line_with_size_mapped(self):
        """Mapped size as linewidth."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [1.0, 1.0, 1.0]})
        p = ggplot(df, aes(x="x", y="y", size="z")) + geom_line()
        assert len(p._repr_png_()) > 0

    def test_line_with_linetype_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(linetype="dashed")
        assert len(p._repr_png_()) > 0

    def test_line_with_size_param(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(size=3)
        assert len(p._repr_png_()) > 0

    def test_line_with_color_mapped(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(color="red")
        assert len(p._repr_png_()) > 0


class TestAutoScaleFallbacks:
    def test_unknown_aesthetic_numeric(self):
        """Non-special aesthetic with numeric data should get ScaleContinuous."""
        from plotten.scales._position import ScaleContinuous

        s = pl.Series("weight", [1.0, 2.0, 3.0])
        scale = auto_scale("weight", s)
        assert isinstance(scale, ScaleContinuous)

    def test_unknown_aesthetic_categorical(self):
        """Non-special aesthetic with string data should get ScaleDiscrete."""
        from plotten.scales._position import ScaleDiscrete

        s = pl.Series("category", ["a", "b", "c"])
        scale = auto_scale("category", s)
        assert isinstance(scale, ScaleDiscrete)


class TestScaleAlphaDiscreteLegend:
    def test_legend_entries(self):
        scale = scale_alpha_continuous()
        s = pl.Series("alpha", [0, 100])
        scale.train(s)
        entries = scale.legend_entries()
        assert all(e.alpha is not None for e in entries)

    def test_discrete_legend(self):
        from plotten.scales._alpha import ScaleAlphaDiscrete

        scale = ScaleAlphaDiscrete()
        s = pl.Series("alpha", ["lo", "hi"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2


class TestScaleSizeDiscreteLegend:
    def test_legend_entries(self):
        from plotten.scales._size import ScaleSizeDiscrete

        scale = ScaleSizeDiscrete()
        s = pl.Series("size", ["sm", "lg"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert entries[0].size is not None


class TestScaleLinetypeLegend:
    def test_get_labels(self):
        scale = scale_linetype_discrete()
        s = pl.Series("linetype", ["a", "b"])
        scale.train(s)
        labels = scale.get_labels()
        assert labels == ["a", "b"]


class TestScaleShapeLegend:
    def test_get_labels(self):
        scale = scale_shape_discrete()
        s = pl.Series("shape", ["cat", "dog"])
        scale.train(s)
        labels = scale.get_labels()
        assert labels == ["cat", "dog"]


class TestDateScaleBranches:
    def test_scale_y_date(self):
        from plotten import scale_y_date

        scale = scale_y_date()
        assert scale.aesthetic == "y"

    def test_scale_x_datetime(self):
        from plotten import scale_x_datetime

        scale = scale_x_datetime()
        assert scale.aesthetic == "x"

    def test_scale_y_datetime(self):
        from plotten import scale_y_datetime

        scale = scale_y_datetime()
        assert scale.aesthetic == "y"

    def test_date_with_limits(self):
        from plotten.scales._date import ScaleDateContinuous

        scale = ScaleDateContinuous(
            aesthetic="x",
            limits=(datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)),
        )
        lo, hi = scale.get_limits()
        assert lo < hi


class TestPositionNoXY:
    def test_dodge_no_x(self):
        data = {"y": [1, 2]}
        result = PositionDodge().adjust(data, {})
        assert result == data

    def test_stack_no_x(self):
        data = {"y": [1, 2]}
        result = PositionStack().adjust(data, {})
        assert result == data

    def test_fill_no_x(self):
        data = {"y": [1, 2]}
        result = PositionFill().adjust(data, {})
        assert result == data


class TestHistogramWithPosition:
    def test_histogram_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3, 4, 5, 1, 2, 3]})
        p = ggplot(df, aes(x="x")) + geom_histogram(bins=5)
        assert len(p._repr_png_()) > 0


class TestGeomPointShapeBranches:
    """Test uncommon branches when shapes are mapped."""

    def test_shape_with_param_size(self):
        """Shape mapped, size as param (not aesthetic)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(size=50)
        assert len(p._repr_png_()) > 0

    def test_shape_with_param_alpha(self):
        """Shape mapped, alpha as param (not aesthetic)."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(alpha=0.5)
        assert len(p._repr_png_()) > 0

    def test_shape_with_single_color_string(self):
        """Shape mapped, color is a fixed string."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point(color="red")
        assert len(p._repr_png_()) > 0


class TestGeomLineMappedBranches:
    def test_line_with_alpha_mapped(self):
        """Alpha mapped as aesthetic on line."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [10, 50, 100]})
        p = ggplot(df, aes(x="x", y="y", alpha="z")) + geom_line()
        assert len(p._repr_png_()) > 0


class TestColWithFillBranches:
    def test_col_with_color_string(self):
        df = pl.DataFrame({"x": ["a", "b"], "y": [10, 20]})
        p = ggplot(df, aes(x="x", y="y")) + geom_col(color="blue")
        assert len(p._repr_png_()) > 0

    def test_col_with_alpha(self):
        df = pl.DataFrame({"x": ["a", "b"], "y": [10, 20]})
        p = ggplot(df, aes(x="x", y="y")) + geom_col(alpha=0.5)
        assert len(p._repr_png_()) > 0
