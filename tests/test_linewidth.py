from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

matplotlib.use("Agg")

from plotten import (
    ScaleLinewidthContinuous,
    ScaleLinewidthDiscrete,
    aes,
    geom_area,
    geom_line,
    geom_path,
    geom_ribbon,
    geom_step,
    ggplot,
    scale_linewidth_continuous,
    scale_linewidth_discrete,
    scale_linewidth_manual,
)
from plotten._render._mpl import render
from plotten.scales._base import LegendEntry, auto_scale


class TestScaleLinewidthContinuous:
    def test_train_and_map(self):
        scale = ScaleLinewidthContinuous(range=(0.5, 3.0))
        s = pd.Series([1, 2, 3, 4, 5])
        scale.train(s)
        mapped = scale.map_data(s)
        assert len(mapped) == 5
        assert mapped[0] == pytest.approx(0.5)
        assert mapped[-1] == pytest.approx(3.0)

    def test_legend_entries(self):
        scale = ScaleLinewidthContinuous(range=(0.5, 3.0))
        s = pd.Series([0, 10])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) > 0
        assert all(isinstance(e, LegendEntry) for e in entries)
        assert all(e.linewidth is not None for e in entries)

    def test_auto_scale_numeric(self):
        s = pd.Series([1.0, 2.0, 3.0])
        scale = auto_scale("linewidth", s)
        assert isinstance(scale, ScaleLinewidthContinuous)

    def test_auto_scale_discrete(self):
        s = pd.Series(["a", "b", "c"])
        scale = auto_scale("linewidth", s)
        assert isinstance(scale, ScaleLinewidthDiscrete)


class TestScaleLinewidthDiscrete:
    def test_train_and_map(self):
        scale = ScaleLinewidthDiscrete()
        s = pd.Series(["a", "b", "c"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert len(mapped) == 3
        assert mapped[0] == pytest.approx(0.5)
        assert mapped[-1] == pytest.approx(3.0)

    def test_manual_values(self):
        scale = ScaleLinewidthDiscrete(values={"a": 1.0, "b": 2.0})
        s = pd.Series(["a", "b"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == [1.0, 2.0]

    def test_legend_entries(self):
        scale = ScaleLinewidthDiscrete()
        s = pd.Series(["x", "y"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert entries[0].linewidth is not None


class TestLinewidthFactories:
    def test_scale_linewidth_continuous_factory(self):
        s = scale_linewidth_continuous(range=(1, 5))
        assert isinstance(s, ScaleLinewidthContinuous)

    def test_scale_linewidth_discrete_factory(self):
        s = scale_linewidth_discrete()
        assert isinstance(s, ScaleLinewidthDiscrete)

    def test_scale_linewidth_manual_factory(self):
        s = scale_linewidth_manual({"a": 1, "b": 2})
        assert isinstance(s, ScaleLinewidthDiscrete)


class TestLinewidthGeomRendering:
    def test_geom_line_with_linewidth_param(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(linewidth=2.5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_line_with_linewidth_aes(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "w": [0.5, 1.5, 3.0]})
        p = ggplot(df, aes(x="x", y="y", linewidth="w")) + geom_line()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_path_with_linewidth(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(linewidth=2.0)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_step_with_linewidth(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step(linewidth=2.0)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_area_with_linewidth(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_area(linewidth=1.5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_ribbon_with_linewidth(self):
        df = pd.DataFrame({"x": [1, 2, 3], "lo": [0, 1, 2], "hi": [2, 5, 10]})
        p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_ribbon(linewidth=1.5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_backward_compat_size_as_linewidth(self):
        """size still works as linewidth fallback for line geoms."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_line(size=2.0)
        fig = render(p)
        assert fig is not None
        plt.close(fig)
