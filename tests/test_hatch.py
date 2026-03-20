from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

from plotten import (
    ScaleHatchDiscrete,
    aes,
    geom_area,
    geom_bar,
    geom_boxplot,
    geom_col,
    geom_density,
    geom_histogram,
    geom_polygon,
    geom_rect,
    geom_ribbon,
    geom_tile,
    geom_violin,
    ggplot,
    scale_hatch_discrete,
    scale_hatch_manual,
)
from plotten._render._mpl import render
from plotten.scales._base import LegendEntry, auto_scale
from plotten.scales._hatch import DEFAULT_HATCH_CYCLE


class TestScaleHatchDiscrete:
    def test_train_and_map(self):
        scale = ScaleHatchDiscrete()
        s = pd.Series(["a", "b", "c"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert len(mapped) == 3
        assert mapped[0] == DEFAULT_HATCH_CYCLE[0]
        assert mapped[1] == DEFAULT_HATCH_CYCLE[1]
        assert mapped[2] == DEFAULT_HATCH_CYCLE[2]

    def test_manual_values(self):
        scale = ScaleHatchDiscrete(values={"a": "//", "b": "xx"})
        s = pd.Series(["a", "b"])
        scale.train(s)
        mapped = scale.map_data(s)
        assert mapped == ["//", "xx"]

    def test_legend_entries(self):
        scale = ScaleHatchDiscrete()
        s = pd.Series(["x", "y"])
        scale.train(s)
        entries = scale.legend_entries()
        assert len(entries) == 2
        assert all(isinstance(e, LegendEntry) for e in entries)
        assert all(e.hatch is not None for e in entries)

    def test_auto_scale(self):
        s = pd.Series(["a", "b"])
        scale = auto_scale("hatch", s)
        assert isinstance(scale, ScaleHatchDiscrete)


class TestHatchFactories:
    def test_scale_hatch_discrete_factory(self):
        s = scale_hatch_discrete()
        assert isinstance(s, ScaleHatchDiscrete)

    def test_scale_hatch_manual_factory(self):
        s = scale_hatch_manual({"a": "//", "b": "xx"})
        assert isinstance(s, ScaleHatchDiscrete)


class TestHatchGeomRendering:
    def test_geom_bar_hatch_param(self):
        df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_col(hatch="//")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_bar_hatch_mapped(self):
        df = pd.DataFrame({"x": ["a", "a", "b", "b"], "g": ["x", "x", "y", "y"]})
        p = ggplot(df, aes(x="x", hatch="g")) + geom_bar()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_area_hatch(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_area(hatch="\\\\")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_ribbon_hatch(self):
        df = pd.DataFrame({"x": [1, 2, 3], "lo": [0, 1, 2], "hi": [2, 5, 10]})
        p = ggplot(df, aes(x="x", ymin="lo", ymax="hi")) + geom_ribbon(hatch="||")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_density_hatch(self):
        df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4]})
        p = ggplot(df, aes(x="x")) + geom_density(hatch="//")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_histogram_hatch(self):
        df = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3]})
        p = ggplot(df, aes(x="x")) + geom_histogram(hatch="+")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_boxplot_hatch(self):
        df = pd.DataFrame({"g": ["a"] * 5 + ["b"] * 5, "v": list(range(10))})
        p = ggplot(df, aes(x="g", y="v")) + geom_boxplot(hatch="x")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_violin_hatch(self):
        df = pd.DataFrame({"g": ["a"] * 10 + ["b"] * 10, "v": list(range(20))})
        p = ggplot(df, aes(x="g", y="v")) + geom_violin(hatch="o")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_rect_hatch(self):
        df = pd.DataFrame({"x0": [0], "x1": [2], "y0": [0], "y1": [3]})
        p = ggplot(df, aes(xmin="x0", xmax="x1", ymin="y0", ymax="y1")) + geom_rect(hatch="//")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_tile_hatch(self, tmp_path):
        df = pd.DataFrame({"x": [0, 1, 0, 1], "y": [0, 0, 1, 1]})
        p = ggplot(df, aes(x="x", y="y")) + geom_tile(fill="steelblue", hatch="x")
        path = tmp_path / "tile_hatch.png"
        p.save(str(path))
        assert path.stat().st_size > 0

    def test_geom_polygon_hatch(self):
        df = pd.DataFrame({"x": [0, 1, 0.5], "y": [0, 0, 1], "g": [1, 1, 1]})
        p = ggplot(df, aes(x="x", y="y", group="g")) + geom_polygon(hatch="//")
        fig = render(p)
        assert fig is not None
        plt.close(fig)
