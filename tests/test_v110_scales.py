"""Tests for v1.1.0 scale additions: gradient2, gradientn, reverse."""

from __future__ import annotations

import pandas as pd
import pytest

from plotten import (
    Aes,
    ScaleGradient2,
    ScaleGradientN,
    ScaleReverse,
    geom_point,
    ggplot,
    scale_color_gradient2,
    scale_color_gradientn,
    scale_fill_gradient2,
    scale_fill_gradientn,
    scale_x_reverse,
    scale_y_reverse,
)
from plotten._render._mpl import render

# ---------------------------------------------------------------------------
# 2A: scale_x_reverse / scale_y_reverse (already exist — verify behavior)
# ---------------------------------------------------------------------------


class TestReverseScales:
    def test_scale_x_reverse_creates_instance(self):
        s = scale_x_reverse()
        assert isinstance(s, ScaleReverse)
        assert s.aesthetic == "x"

    def test_scale_y_reverse_creates_instance(self):
        s = scale_y_reverse()
        assert isinstance(s, ScaleReverse)
        assert s.aesthetic == "y"

    def test_reverse_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + scale_x_reverse()
        fig = render(p)
        assert fig is not None

    def test_reverse_y_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + scale_y_reverse()
        fig = render(p)
        assert fig is not None


# ---------------------------------------------------------------------------
# 2B: scale_color_gradient2 / scale_fill_gradient2 (already exist — verify)
# ---------------------------------------------------------------------------


class TestGradient2Scales:
    def test_color_gradient2_factory(self):
        s = scale_color_gradient2()
        assert isinstance(s, ScaleGradient2)
        assert s.aesthetic == "color"

    def test_fill_gradient2_factory(self):
        s = scale_fill_gradient2()
        assert isinstance(s, ScaleGradient2)
        assert s.aesthetic == "fill"

    def test_gradient2_custom_colors(self):
        s = scale_color_gradient2(low="blue", mid="white", high="red", midpoint=0)
        assert s._low == "blue"
        assert s._mid == "white"
        assert s._high == "red"
        assert s._midpoint == 0

    def test_gradient2_map_data_below_midpoint(self):
        s = scale_color_gradient2(low="#ff0000", mid="#ffffff", high="#0000ff", midpoint=0)
        s.train(pd.Series([-10.0, 10.0]))
        mapped = s.map_data(pd.Series([-10.0]))
        assert mapped[0].startswith("#")

    def test_gradient2_map_data_above_midpoint(self):
        s = scale_color_gradient2(low="#ff0000", mid="#ffffff", high="#0000ff", midpoint=0)
        s.train(pd.Series([-10.0, 10.0]))
        mapped = s.map_data(pd.Series([10.0]))
        assert mapped[0].startswith("#")

    def test_gradient2_map_data_at_midpoint(self):
        s = scale_color_gradient2(low="#ff0000", mid="#ffffff", high="#0000ff", midpoint=0)
        s.train(pd.Series([-10.0, 10.0]))
        mapped = s.map_data(pd.Series([0.0]))
        # At midpoint should be close to mid color (#ffffff)
        assert mapped[0].startswith("#")

    def test_gradient2_legend_entries_color(self):
        s = scale_color_gradient2()
        s.train(pd.Series([-5.0, 5.0]))
        entries = s.legend_entries()
        assert len(entries) > 0
        for e in entries:
            assert e.color is not None
            assert e.color.startswith("#")

    def test_gradient2_legend_entries_fill(self):
        s = scale_fill_gradient2()
        s.train(pd.Series([-5.0, 5.0]))
        entries = s.legend_entries()
        assert len(entries) > 0
        for e in entries:
            assert e.fill is not None
            assert e.fill.startswith("#")

    def test_gradient2_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "v": [-1.0, 0.0, 1.0]})
        p = (
            ggplot(df, Aes(x="x", y="y", color="v"))
            + geom_point()
            + scale_color_gradient2(low="blue", mid="white", high="red", midpoint=0)
        )
        fig = render(p)
        assert fig is not None


# ---------------------------------------------------------------------------
# 2C: scale_color_gradientn / scale_fill_gradientn (new)
# ---------------------------------------------------------------------------


class TestGradientNScales:
    def test_color_gradientn_factory(self):
        s = scale_color_gradientn(colors=["red", "white", "blue"])
        assert isinstance(s, ScaleGradientN)
        assert s.aesthetic == "color"

    def test_fill_gradientn_factory(self):
        s = scale_fill_gradientn(colors=["red", "white", "blue"])
        assert isinstance(s, ScaleGradientN)
        assert s.aesthetic == "fill"

    def test_gradientn_default_colors(self):
        s = scale_color_gradientn()
        assert isinstance(s, ScaleGradientN)
        assert s._colors == ["#132B43", "#56B1F7"]

    def test_gradientn_custom_colors(self):
        colors = ["#ff0000", "#00ff00", "#0000ff"]
        s = scale_color_gradientn(colors=colors)
        assert s._colors == colors

    def test_gradientn_with_values(self):
        colors = ["red", "green", "blue"]
        values = [0.0, 0.3, 1.0]
        s = scale_color_gradientn(colors=colors, values=values)
        assert s._values == values

    def test_gradientn_values_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="Length of values"):
            scale_color_gradientn(colors=["red", "blue"], values=[0.0, 0.5, 1.0])

    def test_gradientn_map_data(self):
        s = scale_color_gradientn(colors=["red", "white", "blue"])
        s.train(pd.Series([0.0, 10.0]))
        mapped = s.map_data(pd.Series([0.0, 5.0, 10.0]))
        assert len(mapped) == 3
        for c in mapped:
            assert c.startswith("#")

    def test_gradientn_map_data_with_values(self):
        s = scale_color_gradientn(
            colors=["red", "green", "blue"],
            values=[0.0, 0.2, 1.0],
        )
        s.train(pd.Series([0.0, 100.0]))
        mapped = s.map_data(pd.Series([0.0, 20.0, 100.0]))
        assert len(mapped) == 3
        for c in mapped:
            assert c.startswith("#")

    def test_gradientn_legend_entries_color(self):
        s = scale_color_gradientn(colors=["red", "yellow", "green"])
        s.train(pd.Series([0.0, 100.0]))
        entries = s.legend_entries()
        assert len(entries) > 0
        for e in entries:
            assert e.color is not None
            assert e.color.startswith("#")

    def test_gradientn_legend_entries_fill(self):
        s = scale_fill_gradientn(colors=["red", "yellow", "green"])
        s.train(pd.Series([0.0, 100.0]))
        entries = s.legend_entries()
        assert len(entries) > 0
        for e in entries:
            assert e.fill is not None
            assert e.fill.startswith("#")

    def test_gradientn_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 3, 4], "v": [0.0, 3.0, 7.0, 10.0]})
        p = (
            ggplot(df, Aes(x="x", y="y", color="v"))
            + geom_point()
            + scale_color_gradientn(colors=["blue", "cyan", "yellow", "red"])
        )
        fig = render(p)
        assert fig is not None

    def test_fill_gradientn_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 2, 3, 4], "v": [0.0, 3.0, 7.0, 10.0]})
        p = (
            ggplot(df, Aes(x="x", y="y", color="v"))
            + geom_point()
            + scale_fill_gradientn(colors=["purple", "orange", "green"])
        )
        fig = render(p)
        assert fig is not None

    def test_gradientn_many_colors(self):
        """Test with a large number of color stops."""
        colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]
        s = scale_color_gradientn(colors=colors)
        s.train(pd.Series([0.0, 1.0]))
        mapped = s.map_data(pd.Series([0.0, 0.5, 1.0]))
        assert len(mapped) == 3

    def test_gradientn_with_limits(self):
        s = scale_color_gradientn(colors=["red", "blue"], limits=(0, 100))
        s.train(pd.Series([10.0, 90.0]))
        lo, hi = s.get_limits()
        assert lo == 0
        assert hi == 100

    def test_gradientn_with_breaks(self):
        s = scale_color_gradientn(colors=["red", "blue"], breaks=[0, 25, 50, 75, 100])
        s.train(pd.Series([0.0, 100.0]))
        breaks = s.get_breaks()
        assert breaks == [0, 25, 50, 75, 100]

    def test_gradientn_get_limits_from_training(self):
        s = scale_color_gradientn(colors=["red", "blue"])
        s.train(pd.Series([5.0, 15.0]))
        lo, hi = s.get_limits()
        assert lo == 5.0
        assert hi == 15.0
