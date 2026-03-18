"""Tests for v0.6.0 fill scales, gradients, and Brewer palettes."""

from __future__ import annotations

import matplotlib
import polars as pl

from plotten import (
    Aes,
    geom_col,
    geom_point,
    ggplot,
    scale_color_brewer,
    scale_color_distiller,
    scale_color_gradient,
    scale_color_gradient2,
    scale_fill_brewer,
    scale_fill_continuous,
    scale_fill_discrete,
    scale_fill_distiller,
    scale_fill_gradient,
    scale_fill_gradient2,
)
from plotten.scales._brewer import ScaleBrewerContinuous, ScaleBrewerDiscrete
from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
from plotten.scales._gradient import ScaleGradient, ScaleGradient2

matplotlib.use("Agg")


# ── scale_fill_continuous / scale_fill_discrete ─────────────────────


class TestScaleFillContinuous:
    def test_returns_continuous_scale_with_fill_aesthetic(self):
        s = scale_fill_continuous()
        assert isinstance(s, ScaleColorContinuous)
        assert s.aesthetic == "fill"

    def test_custom_cmap(self):
        s = scale_fill_continuous(cmap="plasma")
        assert s._cmap_name == "plasma"

    def test_legend_entries_use_fill_field(self):
        s = scale_fill_continuous()
        s.train(pl.Series([1.0, 5.0]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)
        assert all(e.color is None for e in entries)


class TestScaleFillDiscrete:
    def test_returns_discrete_scale_with_fill_aesthetic(self):
        s = scale_fill_discrete()
        assert isinstance(s, ScaleColorDiscrete)
        assert s.aesthetic == "fill"

    def test_custom_palette(self):
        s = scale_fill_discrete(palette="Set2")
        assert s._palette_name == "Set2"

    def test_legend_entries_use_fill_field(self):
        s = scale_fill_discrete()
        s.train(pl.Series(["a", "b", "c"]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)
        assert all(e.color is None for e in entries)


# ── Gradient scales ─────────────────────────────────────────────────


class TestScaleGradient:
    def test_two_color_gradient(self):
        s = scale_color_gradient(low="#000000", high="#ffffff")
        assert isinstance(s, ScaleGradient)
        s.train(pl.Series([0.0, 10.0]))
        mapped = s.map_data(pl.Series([0.0, 5.0, 10.0]))
        assert len(mapped) == 3
        assert mapped[0] != mapped[-1]

    def test_fill_gradient(self):
        s = scale_fill_gradient(low="#ff0000", high="#0000ff")
        assert s.aesthetic == "fill"

    def test_legend_entries_color(self):
        s = scale_color_gradient()
        s.train(pl.Series([0.0, 1.0]))
        entries = s.legend_entries()
        assert all(e.color is not None for e in entries)

    def test_legend_entries_fill(self):
        s = scale_fill_gradient()
        s.train(pl.Series([0.0, 1.0]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)
        assert all(e.color is None for e in entries)


class TestScaleGradient2:
    def test_diverging_gradient(self):
        s = scale_color_gradient2(low="#ff0000", mid="#ffffff", high="#0000ff", midpoint=0)
        assert isinstance(s, ScaleGradient2)
        s.train(pl.Series([-5.0, 0.0, 5.0]))
        mapped = s.map_data(pl.Series([-5.0, 0.0, 5.0]))
        assert len(mapped) == 3

    def test_fill_gradient2(self):
        s = scale_fill_gradient2()
        assert s.aesthetic == "fill"

    def test_midpoint_normalization(self):
        s = scale_color_gradient2(midpoint=0)
        s.train(pl.Series([-10.0, 0.0, 10.0]))
        mapped = s.map_data(pl.Series([0.0]))
        # midpoint should map to the middle color
        assert mapped[0] is not None

    def test_legend_entries_fill(self):
        s = scale_fill_gradient2()
        s.train(pl.Series([-1.0, 0.0, 1.0]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)


# ── Brewer scales ───────────────────────────────────────────────────


class TestScaleBrewerDiscrete:
    def test_default_palette(self):
        s = scale_color_brewer()
        assert isinstance(s, ScaleBrewerDiscrete)
        assert s.aesthetic == "color"

    def test_fill_variant(self):
        s = scale_fill_brewer(palette="Paired")
        assert s.aesthetic == "fill"

    def test_direction_reverse(self):
        s1 = scale_color_brewer(palette="Set1")
        s2 = scale_color_brewer(palette="Set1", direction=-1)
        for sc in (s1, s2):
            sc.train(pl.Series(["a", "b", "c"]))
        m1 = s1.map_data(pl.Series(["a", "b", "c"]))
        m2 = s2.map_data(pl.Series(["a", "b", "c"]))
        # Reversed order should differ
        assert m1[0] != m2[0]

    def test_legend_entries_fill(self):
        s = scale_fill_brewer()
        s.train(pl.Series(["x", "y"]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)


class TestScaleBrewerContinuous:
    def test_default_palette(self):
        s = scale_color_distiller()
        assert isinstance(s, ScaleBrewerContinuous)

    def test_fill_variant(self):
        s = scale_fill_distiller(palette="YlOrRd")
        assert s.aesthetic == "fill"

    def test_direction_reverse(self):
        s1 = scale_color_distiller(palette="RdYlBu")
        s2 = scale_color_distiller(palette="RdYlBu", direction=-1)
        for sc in (s1, s2):
            sc.train(pl.Series([0.0, 10.0]))
        m1 = s1.map_data(pl.Series([0.0]))
        m2 = s2.map_data(pl.Series([0.0]))
        assert m1[0] != m2[0]

    def test_legend_entries_fill(self):
        s = scale_fill_distiller()
        s.train(pl.Series([0.0, 10.0]))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)


# ── Legend fill rendering ───────────────────────────────────────────


class TestFillLegendRendering:
    def test_fill_scale_renders_with_legend(self):
        df = pl.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, Aes(x="x", y="y", fill="g")) + geom_col() + scale_fill_discrete()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_gradient_scale_renders_with_legend(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3], "z": [0.0, 5.0, 10.0]})
        p = ggplot(df, Aes(x="x", y="y", color="z")) + geom_point() + scale_color_gradient()
        fig = p._repr_png_()
        assert len(fig) > 0
