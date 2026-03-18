"""Tests for v0.5 aesthetic scales (size, alpha, shape, linetype)."""

from __future__ import annotations

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import (
    aes,
    geom_line,
    geom_point,
    ggplot,
    scale_alpha_continuous,
    scale_alpha_discrete,
    scale_alpha_manual,
    scale_linetype_discrete,
    scale_linetype_manual,
    scale_shape_discrete,
    scale_shape_manual,
    scale_size_continuous,
    scale_size_discrete,
    scale_size_manual,
)
from plotten.scales._base import auto_scale


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
