from __future__ import annotations

import os
import tempfile

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

import plotten
from plotten import (
    Aes,
    ScaleGradient2,
    ScaleGradientN,
    ScaleReverse,
    aes,
    dup_axis,
    geom_col,
    geom_line,
    geom_point,
    ggplot,
    label_comma,
    label_dollar,
    label_number,
    label_percent,
    label_scientific,
    scale_alpha_continuous,
    scale_alpha_discrete,
    scale_alpha_manual,
    scale_color_brewer,
    scale_color_distiller,
    scale_color_gradient,
    scale_color_gradient2,
    scale_color_gradientn,
    scale_color_gray,
    scale_color_grey,
    scale_color_grey_continuous,
    scale_color_identity,
    scale_fill_brewer,
    scale_fill_continuous,
    scale_fill_discrete,
    scale_fill_distiller,
    scale_fill_gradient,
    scale_fill_gradient2,
    scale_fill_gradientn,
    scale_fill_grey,
    scale_fill_identity,
    scale_linetype_discrete,
    scale_linetype_manual,
    scale_shape_discrete,
    scale_shape_manual,
    scale_size_continuous,
    scale_size_discrete,
    scale_size_identity,
    scale_size_manual,
    scale_x_continuous,
    scale_x_log10,
    scale_x_reverse,
    scale_x_sqrt,
    scale_y_continuous,
    scale_y_log10,
    scale_y_reverse,
    scale_y_sqrt,
    sec_axis,
)
from plotten._render._mpl import render
from plotten.scales import (
    ScaleColorContinuous,
    ScaleColorDiscrete,
    ScaleContinuous,
    ScaleDiscrete,
    scale_color_manual,
    scale_fill_manual,
    scale_x_discrete,
    scale_y_discrete,
)
from plotten.scales._base import LegendEntry, auto_scale
from plotten.scales._binned import (
    ScaleColorBinned,
    ScaleFillBinned,
    scale_color_fermenter,
    scale_color_steps,
    scale_fill_fermenter,
    scale_fill_steps,
)
from plotten.scales._brewer import ScaleBrewerContinuous, ScaleBrewerDiscrete
from plotten.scales._gradient import ScaleGradient
from plotten.scales._log import ScaleLog
from plotten.scales._sec_axis import SecAxis

# --- from test_scales.py ---


def test_continuous_train_and_limits():
    s = ScaleContinuous("x")
    series = pl.Series("x", [1.0, 5.0, 10.0])
    s.train(series)
    lo, hi = s.get_limits()
    assert lo < 1.0  # padded
    assert hi > 10.0  # padded


def test_continuous_breaks():
    s = ScaleContinuous("y")
    series = pl.Series("y", [0.0, 100.0])
    s.train(series)
    breaks = s.get_breaks()
    assert len(breaks) == 6


def test_discrete_train_and_map():
    s = ScaleDiscrete("x")
    series = pl.Series("x", ["b", "a", "c", "a"])
    s.train(series)
    assert s._levels == ["a", "b", "c"]
    mapped = s.map_data(pl.Series("x", ["c", "a"]))
    assert mapped == [2, 0]


def test_discrete_labels():
    s = ScaleDiscrete("x")
    s.train(pl.Series("x", ["cat", "dog"]))
    assert s.get_labels() == ["cat", "dog"]


def test_color_continuous():
    s = ScaleColorContinuous()
    series = pl.Series("v", [0.0, 0.5, 1.0])
    s.train(series)
    colors = s.map_data(series)
    assert len(colors) == 3
    assert all(c.startswith("#") for c in colors)


def test_color_discrete():
    s = ScaleColorDiscrete()
    series = pl.Series("g", ["a", "b", "c"])
    s.train(series)
    colors = s.map_data(series)
    assert len(colors) == 3
    assert all(c.startswith("#") for c in colors)


def test_auto_scale_numeric():
    series = pl.Series("x", [1, 2, 3])
    s = auto_scale("x", series)
    assert isinstance(s, ScaleContinuous)


def test_auto_scale_string():
    series = pl.Series("x", ["a", "b"])
    s = auto_scale("x", series)
    assert isinstance(s, ScaleDiscrete)


def test_auto_scale_color_numeric():
    series = pl.Series("color", [1.0, 2.0])
    s = auto_scale("color", series)
    assert isinstance(s, ScaleColorContinuous)


def test_auto_scale_color_string():
    series = pl.Series("color", ["a", "b"])
    s = auto_scale("color", series)
    assert isinstance(s, ScaleColorDiscrete)


# --- from test_log_scales.py ---


def test_scale_log_breaks():
    s = ScaleLog(aesthetic="x", base=10)

    s.train(pd.Series([1, 100, 10000]))
    breaks = s.get_breaks()
    assert 1 in breaks
    assert 100 in breaks
    assert 10000 in breaks


def test_scale_log_limits():
    s = ScaleLog(aesthetic="y", base=10)

    s.train(pd.Series([10, 1000]))
    lo, hi = s.get_limits()
    assert lo == 10
    assert hi == 1000


def test_scale_y_log10_render():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 100, 1000, 10000, 100000]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_log10()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_scale_x_log10_render():
    df = pl.DataFrame({"x": [1, 10, 100, 1000], "y": [1, 2, 3, 4]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_log10()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


# --- from test_v04_scales.py ---


def test_continuous_manual_breaks():
    s = ScaleContinuous("x", breaks=[0, 5, 10])
    s.train(pl.Series("x", [0.0, 10.0]))
    assert s.get_breaks() == [0, 5, 10]


def test_continuous_manual_limits():
    s = ScaleContinuous("x", limits=(0, 100))
    s.train(pl.Series("x", [10.0, 20.0]))
    assert s.get_limits() == (0, 100)


def test_continuous_manual_labels():
    s = ScaleContinuous("x", breaks=[0, 5, 10], labels=["low", "mid", "high"])
    s.train(pl.Series("x", [0.0, 10.0]))
    assert s.get_labels() == ["low", "mid", "high"]


def test_continuous_default_labels_from_breaks():
    s = ScaleContinuous("x", breaks=[1, 2, 3])
    s.train(pl.Series("x", [1.0, 3.0]))
    assert s.get_labels() == ["1", "2", "3"]


def test_discrete_manual_labels_dict():
    s = ScaleDiscrete("x", labels={"a": "Alpha", "b": "Beta"})
    s.train(pl.Series("x", ["a", "b"]))
    assert s.get_labels() == ["Alpha", "Beta"]


def test_discrete_manual_labels_list():
    s = ScaleDiscrete("x", labels=["Cat", "Dog"])
    s.train(pl.Series("x", ["a", "b"]))
    assert s.get_labels() == ["Cat", "Dog"]


def test_color_discrete_manual_palette():
    s = ScaleColorDiscrete(values={"a": "#ff0000", "b": "#0000ff"})
    s.train(pl.Series("g", ["a", "b"]))
    colors = s.map_data(pl.Series("g", ["a", "b", "a"]))
    assert colors == ["#ff0000", "#0000ff", "#ff0000"]


def test_color_discrete_manual_legend_entries():
    s = ScaleColorDiscrete(values={"a": "#ff0000", "b": "#0000ff"})
    s.train(pl.Series("g", ["a", "b"]))
    entries = s.legend_entries()
    assert len(entries) == 2
    assert entries[0].color == "#ff0000"
    assert entries[1].color == "#0000ff"


def test_color_discrete_manual_fallback():
    s = ScaleColorDiscrete(values={"a": "#ff0000"})
    s.train(pl.Series("g", ["a", "b"]))
    colors = s.map_data(pl.Series("g", ["a", "b"]))
    assert colors[0] == "#ff0000"
    assert colors[1] == "#000000"  # fallback


def test_color_continuous_manual_breaks():
    s = ScaleColorContinuous(breaks=[0, 50, 100])
    s.train(pl.Series("v", [0.0, 100.0]))
    assert s.get_breaks() == [0, 50, 100]


def test_color_continuous_manual_limits():
    s = ScaleColorContinuous(limits=(0, 200))
    s.train(pl.Series("v", [10.0, 50.0]))
    assert s.get_limits() == (0, 200)


def test_scale_x_continuous_convenience():
    s = scale_x_continuous(breaks=[1, 2, 3], limits=(0, 4))
    assert s.aesthetic == "x"
    assert s._breaks == [1, 2, 3]
    assert s._limits == (0, 4)


def test_scale_y_continuous_convenience():
    s = scale_y_continuous(breaks=[10, 20])
    assert s.aesthetic == "y"
    assert s._breaks == [10, 20]


def test_scale_x_discrete_convenience():
    s = scale_x_discrete(labels={"a": "Alpha"})
    assert s.aesthetic == "x"


def test_scale_y_discrete_convenience():
    s = scale_y_discrete()
    assert s.aesthetic == "y"


def test_scale_color_manual_convenience():
    s = scale_color_manual(values={"a": "red", "b": "blue"})
    assert s.aesthetic == "color"
    assert s._manual_values == {"a": "red", "b": "blue"}


def test_scale_fill_manual_convenience():
    s = scale_fill_manual(values={"x": "#123456"})
    assert s.aesthetic == "fill"


def test_render_with_manual_breaks():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + scale_x_continuous(breaks=[1, 3, 5], limits=(0, 6))
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_render_with_color_manual():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [2, 4, 1, 5],
            "g": ["a", "b", "a", "b"],
        }
    )
    p = (
        ggplot(df, aes(x="x", y="y", color="g"))
        + geom_point()
        + scale_color_manual(values={"a": "red", "b": "blue"})
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


# --- from test_v05_aesthetic_scales.py ---

"""Tests for v0.5 aesthetic scales (size, alpha, shape, linetype)."""


class TestScaleSizeContinuous:
    def test_train_and_map(self):
        scale = scale_size_continuous(range=(2, 20))
        s = pl.Series("size", [1, 5, 10])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped[0] == pytest.approx(2.0)
        assert mapped[2] == pytest.approx(20.0)

    def test_breaks(self):
        scale = scale_size_continuous()
        s = pl.Series("size", [0, 100])
        scale.train(s)
        breaks = scale.get_breaks()
        assert len(breaks) == 5

    def test_legend_entries(self):
        scale = scale_size_continuous()
        s = pl.Series("size", [0, 10])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) > 0
        assert entries[0].size is not None


class TestScaleSizeDiscrete:
    def test_train_and_map(self):
        scale = scale_size_discrete()
        s = pl.Series("size", ["small", "large"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert isinstance(mapped, list)
        assert len(mapped) == 2

    def test_manual(self):
        scale = scale_size_manual(values={"small": 2.0, "large": 10.0})
        s = pl.Series("size", ["small", "large", "small"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == [2.0, 10.0, 2.0]


class TestScaleAlphaContinuous:
    def test_train_and_map(self):
        scale = scale_alpha_continuous()
        s = pl.Series("alpha", [0, 50, 100])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped[0] == pytest.approx(0.1)
        assert mapped[2] == pytest.approx(1.0)

    def test_legend_entries(self):
        scale = scale_alpha_continuous()
        s = pl.Series("alpha", [0, 1])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) > 0
        assert entries[0].alpha is not None


class TestScaleAlphaDiscrete:
    def test_train_and_map(self):
        scale = scale_alpha_discrete()
        s = pl.Series("alpha", ["lo", "hi"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert len(mapped) == 2

    def test_manual(self):
        scale = scale_alpha_manual(values={"lo": 0.2, "hi": 0.9})
        s = pl.Series("alpha", ["lo", "hi"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == [0.2, 0.9]


class TestScaleShapeDiscrete:
    def test_train_and_map(self):
        scale = scale_shape_discrete()
        s = pl.Series("shape", ["a", "b", "c"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == ["o", "s", "^"]

    def test_manual(self):
        scale = scale_shape_manual(values={"a": "x", "b": "+"})
        s = pl.Series("shape", ["a", "b"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == ["x", "+"]

    def test_legend_entries(self):
        scale = scale_shape_discrete()
        s = pl.Series("shape", ["cat", "dog"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert entries[0].shape is not None


class TestScaleLinetypeDiscrete:
    def test_train_and_map(self):
        scale = scale_linetype_discrete()
        s = pl.Series("linetype", ["a", "b"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == ["solid", "dashed"]

    def test_manual(self):
        scale = scale_linetype_manual(values={"a": "dotted", "b": "dashdot"})
        s = pl.Series("linetype", ["a", "b"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == ["dotted", "dashdot"]

    def test_legend_entries(self):
        scale = scale_linetype_discrete()
        s = pl.Series("linetype", ["x", "y"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert entries[0].linetype is not None


class TestAutoScale:
    def test_size_numeric(self):
        s = pl.Series("size", [1, 2, 3])
        from plotten.scales._size import ScaleSizeContinuous

        scale = auto_scale("size", s)
        assert isinstance(scale, ScaleSizeContinuous)

    def test_size_categorical(self):
        s = pl.Series("size", ["small", "large"])
        from plotten.scales._size import ScaleSizeDiscrete

        scale = auto_scale("size", s)
        assert isinstance(scale, ScaleSizeDiscrete)

    def test_alpha_numeric(self):
        s = pl.Series("alpha", [0.1, 0.5])
        from plotten.scales._alpha import ScaleAlphaContinuous

        scale = auto_scale("alpha", s)
        assert isinstance(scale, ScaleAlphaContinuous)

    def test_shape_categorical(self):
        s = pl.Series("shape", ["a", "b"])
        from plotten.scales._shape import ScaleShapeDiscrete

        scale = auto_scale("shape", s)
        assert isinstance(scale, ScaleShapeDiscrete)

    def test_linetype_categorical(self):
        s = pl.Series("linetype", ["x", "y"])
        from plotten.scales._linetype import ScaleLinetypeDiscrete

        scale = auto_scale("linetype", s)
        assert isinstance(scale, ScaleLinetypeDiscrete)


class TestAestheticScaleIntegration:
    def test_size_point_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [10, 20, 30]})
        p = ggplot(df, aes(x="x", y="y", size="z")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_shape_point_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", shape="g")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_linetype_line_renders(self):
        df = pl.DataFrame(
            {
                "x": [1, 2, 3, 1, 2, 3],
                "y": [1, 2, 3, 3, 2, 1],
                "g": ["a", "a", "a", "b", "b", "b"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_alpha_point_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "z": [10, 50, 100]})
        p = ggplot(df, aes(x="x", y="y", alpha="z")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0


# --- from test_v06_fill_scales.py ---

"""Tests for v0.6.0 fill scales, gradients, and Brewer palettes."""

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


# --- from test_v08_scales.py ---

"""Tests for v0.8.0 scale polish: reverse, sqrt, label formatters."""


class TestScaleReverse:
    def test_reverse_limits(self):
        scale = ScaleReverse(aesthetic="x")

        scale.train(pd.Series([1, 5, 10]))
        lo, hi = scale.get_limits()
        assert lo > hi  # reversed

    def test_scale_x_reverse_render(self):
        df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_reverse()
        fig = render(p)
        ax = fig.axes[0]
        xlim = ax.get_xlim()
        assert xlim[0] > xlim[1]  # reversed
        plt.close(fig)

    def test_scale_y_reverse_render(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_reverse()
        fig = render(p)
        ax = fig.axes[0]
        ylim = ax.get_ylim()
        assert ylim[0] > ylim[1]
        plt.close(fig)

    def test_reverse_with_explicit_limits(self):
        scale = ScaleReverse(aesthetic="x", limits=(0, 100))
        lo, hi = scale.get_limits()
        assert lo == 100
        assert hi == 0


class TestScaleSqrt:
    def test_sqrt_scale_render(self):
        df = pl.DataFrame({"x": [1, 4, 9, 16, 25], "y": [1, 2, 3, 4, 5]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_sqrt()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_y_sqrt_scale_render(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_sqrt()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_sqrt_limits_clamp_to_zero(self):
        """Sqrt scale must not produce negative lower limits (sqrt of negative = NaN)."""

        from plotten.scales._sqrt import ScaleSqrt

        scale = ScaleSqrt(aesthetic="y")
        scale.train(pd.Series([5, 15, 45, 90]))
        lo, _hi = scale.get_limits()
        assert lo >= 0

    def test_sqrt_render_data_visible(self):
        """Regression: sqrt panel previously rendered blank due to NaN limits."""
        df = pl.DataFrame(
            {
                "area": [1, 10, 100, 500, 1000, 5000, 10000, 50000],
                "species": [5, 15, 45, 90, 130, 250, 340, 550],
            }
        )
        p = ggplot(df, aes(x="area", y="species")) + geom_point() + scale_y_sqrt()
        fig = render(p)
        ax = fig.axes[0]
        # Data must be visible — check scatter has children
        assert len(ax.collections) > 0
        plt.close(fig)


class TestLabelFormatters:
    def test_label_comma(self):
        fmt = label_comma()
        assert fmt(1000) == "1,000"
        assert fmt(1234567) == "1,234,567"
        assert fmt(500) == "500"

    def test_label_percent(self):
        fmt = label_percent()
        assert fmt(0.5) == "50.0%"
        assert fmt(1.0) == "100.0%"
        assert fmt(0.0) == "0.0%"

    def test_label_percent_accuracy(self):
        fmt = label_percent(accuracy=2)
        assert fmt(0.1234) == "12.34%"

    def test_label_dollar(self):
        fmt = label_dollar()
        assert fmt(1000) == "$1,000.00"
        assert fmt(42.5) == "$42.50"

    def test_label_dollar_prefix(self):
        fmt = label_dollar(prefix="€")
        assert fmt(100) == "€100.00"

    def test_label_scientific(self):
        fmt = label_scientific()
        assert fmt(1000) == "1.00e+03"
        assert fmt(0.001) == "1.00e-03"

    def test_label_number(self):
        fmt = label_number(accuracy=2)
        assert fmt(1234.5678) == "1,234.57"

    def test_label_number_no_decimals(self):
        fmt = label_number()
        assert fmt(1234) == "1,234"

    def test_label_number_negative(self):
        fmt = label_number()
        assert fmt(-1234) == "-1,234"


class TestCallableLabels:
    def test_continuous_scale_callable_labels(self):

        scale = ScaleContinuous(aesthetic="y", breaks=[0, 500, 1000], labels=label_comma())
        labels = scale.get_labels()
        assert labels == ["0", "500", "1,000"]

    def test_render_with_callable_labels(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1000, 2000, 3000]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_continuous(labels=label_comma())
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_with_percent_labels(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [0.1, 0.5, 0.9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(labels=label_percent())
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- from test_v11_scales.py ---

"""Tests for v0.11.0 scale additions: identity scales and grey scales."""


class TestIdentityScales:
    def test_color_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "c": ["red", "blue", "green"]})
        p = ggplot(df, Aes(x="x", y="y", color="c")) + geom_point() + scale_color_identity()
        fig = render(p)
        assert fig is not None

    def test_fill_identity(self):
        df = pd.DataFrame({"x": ["a", "b"], "y": [1, 2], "f": ["#ff0000", "#0000ff"]})
        p = ggplot(df, Aes(x="x", y="y", fill="f")) + geom_col() + scale_fill_identity()
        fig = render(p)
        assert fig is not None

    def test_size_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "s": [10, 20, 30]})
        p = ggplot(df, Aes(x="x", y="y", size="s")) + geom_point() + scale_size_identity()
        fig = render(p)
        assert fig is not None

    def test_identity_no_legend(self):
        """Identity scales should produce no legend by default."""
        scale = scale_color_identity()
        assert scale.legend_entries() is None

    def test_identity_map_passthrough(self):
        """map_data should return values unchanged."""
        scale = scale_color_identity()
        values = ["red", "blue", "green"]
        # map_data should return the input as-is
        result = scale.map_data(pd.Series(values))
        # Since identity returns as-is, should be the same series
        assert list(result) == values


class TestGreyScales:
    def test_discrete_grey(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point() + scale_color_grey()
        fig = render(p)
        assert fig is not None

    def test_discrete_grey_custom_range(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_grey(start=0.0, end=1.0)
        )
        fig = render(p)
        assert fig is not None

    def test_fill_grey(self):
        df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, Aes(x="x", y="y", fill="g")) + geom_col() + scale_fill_grey()
        fig = render(p)
        assert fig is not None

    def test_gray_alias(self):
        """American spelling alias should work."""
        assert scale_color_gray is scale_color_grey

    def test_grey_legend_entries(self):
        scale = scale_color_grey(start=0.2, end=0.8)
        scale.train(pd.Series(["a", "b", "c"]))
        entries = scale.legend_entries()
        assert len(entries) == 3
        # Should be hex grey values
        for entry in entries:
            assert entry.color is not None
            assert entry.color.startswith("#")

    def test_continuous_grey(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "v": [0.0, 0.5, 1.0]})
        p = ggplot(df, Aes(x="x", y="y", color="v")) + geom_point() + scale_color_grey_continuous()
        fig = render(p)
        assert fig is not None

    def test_continuous_grey_maps_values(self):
        scale = scale_color_grey_continuous(start=0.0, end=1.0)
        scale.train(pd.Series([0.0, 10.0]))
        mapped = scale.map_data(pd.Series([0.0, 5.0, 10.0]))
        assert mapped[0] == "#000000"  # start=0.0 -> black
        assert mapped[2] == "#ffffff"  # end=1.0 -> white


# --- from test_v110_scales.py ---

"""Tests for v1.1.0 scale additions: gradient2, gradientn, reverse."""

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


# --- from test_v14_binned.py ---

"""Tests for Phase 4 of v0.14.0: binned scales and convenience factories."""

# --- Bin computation ---


class TestBinComputation:
    def test_int_breaks_produces_correct_edges(self):
        s = ScaleColorBinned(breaks=4, limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert len(edges) == 5  # 4 bins => 5 edges
        assert edges[0] == 0.0
        assert edges[-1] == 10.0

    def test_list_breaks_used_directly(self):
        s = ScaleColorBinned(breaks=[0.0, 2.0, 5.0, 10.0], limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert edges == [0.0, 2.0, 5.0, 10.0]

    def test_edges_from_trained_data(self):
        s = ScaleColorBinned(breaks=3)
        series = pl.Series("val", [1.0, 5.0, 10.0])
        s.train(series)
        edges = s._bin_edges()
        assert len(edges) == 4
        assert abs(edges[0] - 1.0) < 1e-9
        assert abs(edges[-1] - 10.0) < 1e-9

    def test_single_bin(self):
        s = ScaleColorBinned(breaks=1, limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert len(edges) == 2


# --- Value mapping ---


class TestValueMapping:
    def test_maps_values_to_hex_colors(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 4.0, 7.0])
        colors = s.map_data(series)
        assert len(colors) == 3
        assert all(c.startswith("#") for c in colors)

    def test_different_bins_get_different_colors(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 4.0, 7.0])
        colors = s.map_data(series)
        # With 3 bins covering [0,3), [3,6), [6,9], these should be different
        assert colors[0] != colors[2]

    def test_same_bin_same_color(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 2.0])
        colors = s.map_data(series)
        assert colors[0] == colors[1]

    def test_na_value_for_none(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0), na_value="#aabbcc")
        series = pl.Series("val", [1.0, None, 7.0])
        colors = s.map_data(series)
        assert colors[1] == "#aabbcc"

    def test_boundary_values_assigned(self):
        """Values exactly on boundaries should not crash."""
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [0.0, 3.0, 6.0, 9.0])
        colors = s.map_data(series)
        assert len(colors) == 4
        assert all(c.startswith("#") for c in colors)


# --- Legend entries ---


class TestLegendEntries:
    def test_one_entry_per_bin(self):
        s = ScaleColorBinned(breaks=4, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert len(entries) == 4

    def test_entries_are_legend_entry_objects(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        entries = s.legend_entries()
        for e in entries:
            assert isinstance(e, LegendEntry)

    def test_labels_contain_range(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        entries = s.legend_entries()
        # Labels should contain en-dash separating range bounds
        for e in entries:
            assert "\u2013" in e.label

    def test_color_aesthetic_sets_color_field(self):
        s = ScaleColorBinned(aesthetic="color", breaks=2, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert all(e.color is not None for e in entries)
        assert all(e.fill is None for e in entries)

    def test_fill_aesthetic_sets_fill_field(self):
        s = ScaleFillBinned(breaks=2, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)
        assert all(e.color is None for e in entries)


# --- ScaleFillBinned ---


class TestScaleFillBinned:
    def test_aesthetic_is_fill(self):
        s = ScaleFillBinned(breaks=3)
        assert s.aesthetic == "fill"

    def test_map_data_works(self):
        s = ScaleFillBinned(breaks=3, limits=(0.0, 9.0))
        colors = s.map_data(pl.Series("val", [1.0, 4.0, 7.0]))
        assert len(colors) == 3


# --- Convenience factories ---


class TestConvenienceFactories:
    def test_scale_color_steps_returns_binned(self):
        s = scale_color_steps(n=5, cmap="viridis")
        assert isinstance(s, ScaleColorBinned)
        assert s.aesthetic == "color"

    def test_scale_fill_steps_returns_binned(self):
        s = scale_fill_steps(n=5, cmap="viridis")
        assert isinstance(s, ScaleFillBinned)
        assert s.aesthetic == "fill"

    def test_scale_color_fermenter_returns_binned(self):
        s = scale_color_fermenter(n=5, palette="Blues")
        assert isinstance(s, ScaleColorBinned)

    def test_scale_fill_fermenter_returns_binned(self):
        s = scale_fill_fermenter(n=5, palette="Blues")
        assert isinstance(s, ScaleFillBinned)

    def test_factories_exported_from_plotten(self):
        assert hasattr(plotten, "scale_color_steps")
        assert hasattr(plotten, "scale_fill_steps")
        assert hasattr(plotten, "scale_color_fermenter")
        assert hasattr(plotten, "scale_fill_fermenter")

    def test_classes_exported_from_plotten(self):
        assert hasattr(plotten, "ScaleColorBinned")
        assert hasattr(plotten, "ScaleFillBinned")


# --- End-to-end rendering ---


class TestEndToEnd:
    def test_scatter_with_binned_color(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [2.0, 4.0, 1.0, 3.0, 5.0],
                "val": [10.0, 20.0, 30.0, 40.0, 50.0],
            }
        )
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", color="val"))
            + plotten.geom_point()
            + scale_color_steps(n=3)
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bar_with_binned_fill(self):
        df = pl.DataFrame({"x": ["a", "b", "c"], "y": [3.0, 7.0, 5.0], "val": [1.0, 5.0, 9.0]})
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", fill="val"))
            + plotten.geom_col()
            + scale_fill_steps(n=3)
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_fermenter_with_brewer_palette(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0], "z": [10.0, 50.0, 90.0]})
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", color="z"))
            + plotten.geom_point()
            + scale_color_fermenter(n=4, palette="Blues")
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- from test_v11_breaks.py ---

"""Tests for callable breaks in continuous scales."""


class TestCallableBreaks:
    def test_callable_breaks(self):
        """A function should be accepted as breaks."""

        def my_breaks(limits):
            lo, hi = limits
            return [lo, (lo + hi) / 2, hi]

        scale = ScaleContinuous("x", breaks=my_breaks)
        scale.train(pd.Series([0, 100]))
        breaks = scale.get_breaks()
        assert len(breaks) == 3
        assert breaks[0] == pytest.approx(-5.0, abs=1)  # with padding
        assert breaks[2] == pytest.approx(105.0, abs=1)

    def test_callable_breaks_in_plot(self):
        """Callable breaks should work end-to-end."""
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + scale_x_continuous(breaks=lambda lim: [0, 5, 10])
        )
        fig = render(p)
        assert fig is not None

    def test_numpy_arange_breaks(self):
        """Common pattern: np.arange for even spacing."""
        scale = ScaleContinuous("x", breaks=lambda lim: np.arange(lim[0], lim[1], 2).tolist())
        scale.train(pd.Series([0, 10]))
        breaks = scale.get_breaks()
        assert len(breaks) > 0

    def test_list_breaks_still_work(self):
        """Existing list[float] breaks should still work."""
        scale = ScaleContinuous("x", breaks=[0, 5, 10])
        scale.train(pd.Series([0, 10]))
        breaks = scale.get_breaks()
        assert breaks == [0, 5, 10]

    def test_none_breaks_default(self):
        """None breaks should produce default linspace."""
        scale = ScaleContinuous("x")
        scale.train(pd.Series([0, 10]))
        breaks = scale.get_breaks()
        assert len(breaks) == 6  # default linspace(lo, hi, 6)

    def test_callable_labels(self):
        """Callable labels should still work."""
        scale = ScaleContinuous("x", labels=lambda v: f"${v:.0f}")
        scale.train(pd.Series([0, 100]))
        labels = scale.get_labels()
        assert all(lab.startswith("$") for lab in labels)


# --- from test_v09_sec_axis.py ---

"""Tests for secondary axes (sec_axis, dup_axis)."""


class TestSecAxis:
    def test_sec_axis_creation(self):
        sa = sec_axis(trans=lambda x: x * 1.8 + 32, inverse=lambda x: (x - 32) / 1.8)
        assert isinstance(sa, SecAxis)
        assert sa.name is None

    def test_sec_axis_with_name(self):
        sa = sec_axis(
            trans=lambda x: x * 1.8 + 32,
            inverse=lambda x: (x - 32) / 1.8,
            name="Fahrenheit",
        )
        assert sa.name == "Fahrenheit"

    def test_dup_axis(self):
        sa = dup_axis()
        assert isinstance(sa, SecAxis)
        # Identity transform
        assert sa.trans(5) == 5
        assert sa.inverse(5) == 5

    def test_dup_axis_with_name(self):
        sa = dup_axis(name="Also Y")
        assert sa.name == "Also Y"

    def test_sec_axis_transforms(self):
        sa = sec_axis(
            trans=lambda x: x * 2,
            inverse=lambda x: x / 2,
        )
        assert sa.trans(10) == 20
        assert sa.inverse(20) == 10

    def test_sec_axis_breaks_and_labels(self):
        sa = sec_axis(
            trans=lambda x: x,
            inverse=lambda x: x,
            breaks=[0, 50, 100],
            labels=["low", "mid", "high"],
        )
        assert sa.breaks == [0, 50, 100]
        assert sa.labels == ["low", "mid", "high"]

    def _find_sec_axis(self, ax):
        """Find SecondaryAxis child of an axes."""
        from matplotlib.axes._secondary_axes import SecondaryAxis

        for child in ax.get_children():
            if isinstance(child, SecondaryAxis):
                return child
        return None

    def test_sec_axis_rendering_y(self):
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        sa = sec_axis(
            trans=lambda x: x * 1.8 + 32,
            inverse=lambda x: (x - 32) / 1.8,
            name="Fahrenheit",
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + scale_y_continuous(sec_axis=sa)
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is not None
        assert sec.get_ylabel() == "Fahrenheit"

    def test_sec_axis_rendering_with_dup(self):
        df = pd.DataFrame({"x": range(5), "y": range(5)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_line()
            + scale_y_continuous(sec_axis=dup_axis(name="Copy"))
        )
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is not None
        assert sec.get_ylabel() == "Copy"

    def test_no_sec_axis_by_default(self):
        df = pd.DataFrame({"x": range(5), "y": range(5)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_line()
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is None


# --- ScaleSizeArea tests ---


class TestScaleSizeArea:
    def test_zero_maps_to_zero(self):
        from plotten.scales._size import ScaleSizeArea

        s = ScaleSizeArea(max_size=10)
        s.train(pd.Series([0, 5, 10]))
        mapped = s.map_data(pd.Series([0, 5, 10]))
        assert mapped[0] == 0.0

    def test_proportional(self):
        from plotten.scales._size import ScaleSizeArea

        s = ScaleSizeArea(max_size=20)
        s.train(pd.Series([0, 10, 20]))
        mapped = s.map_data(pd.Series([0, 10, 20]))
        assert mapped[0] == 0.0
        assert mapped[1] == pytest.approx(10.0)
        assert mapped[2] == pytest.approx(20.0)

    def test_negative_clamps_to_zero(self):
        from plotten.scales._size import ScaleSizeArea

        s = ScaleSizeArea(max_size=10)
        s.train(pd.Series([-5, 0, 10]))
        mapped = s.map_data(pd.Series([-5]))
        assert mapped[0] == 0.0

    def test_legend_entries(self):
        from plotten.scales._size import ScaleSizeArea

        s = ScaleSizeArea(max_size=10)
        s.train(pd.Series([0, 10]))
        entries = s.legend_entries()
        assert len(entries) > 0
        assert entries[0].size == pytest.approx(0.0, abs=0.1)

    def test_factory(self):
        from plotten import scale_size_area

        s = scale_size_area(max_size=15)
        assert isinstance(s, plotten.ScaleSizeArea)

    def test_render(self):
        from plotten import scale_size_area

        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [0, 5, 10]})
        p = ggplot(df, aes(x="x", y="y", size="v")) + geom_point() + scale_size_area()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- ScaleRadius tests ---


class TestScaleRadius:
    def test_linear_mapping(self):
        from plotten.scales._size import ScaleRadius

        s = ScaleRadius(range=(1, 10))
        s.train(pd.Series([0, 10]))
        mapped = s.map_data(pd.Series([0, 5, 10]))
        assert mapped[0] == pytest.approx(1.0)
        assert mapped[1] == pytest.approx(5.5)
        assert mapped[2] == pytest.approx(10.0)

    def test_factory(self):
        from plotten import scale_radius

        s = scale_radius(range=(2, 8))
        assert isinstance(s, plotten.ScaleRadius)

    def test_render(self):
        from plotten import scale_radius

        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
        p = ggplot(df, aes(x="x", y="y", size="v")) + geom_point() + scale_radius()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- ScaleBinnedPosition tests ---


class TestScaleBinnedPosition:
    def test_values_snap_to_centers(self):
        from plotten.scales._binned_position import ScaleBinnedPosition

        s = ScaleBinnedPosition(aesthetic="x", n_bins=2, limits=(0, 10))
        s.train(pd.Series([0, 5, 10]))
        mapped = s.map_data(pd.Series([1, 6, 9]))
        # With 2 bins: edges at 0, 5, 10 → centers at 2.5, 7.5
        assert mapped[0] == pytest.approx(2.5)
        assert mapped[1] == pytest.approx(7.5)
        assert mapped[2] == pytest.approx(7.5)

    def test_labels_format(self):
        from plotten.scales._binned_position import ScaleBinnedPosition

        s = ScaleBinnedPosition(n_bins=3, limits=(0, 9))
        labels = s.get_labels()
        assert len(labels) == 3
        assert labels[0].startswith("[")
        assert labels[0].endswith(")")

    def test_factory_x(self):
        from plotten import scale_x_binned

        s = scale_x_binned(n_bins=5)
        assert s.aesthetic == "x"

    def test_factory_y(self):
        from plotten import scale_y_binned

        s = scale_y_binned(n_bins=5)
        assert s.aesthetic == "y"

    def test_render(self):
        from plotten import scale_x_binned

        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_binned(n_bins=3)
        fig = render(p)
        assert fig is not None
        plt.close(fig)
