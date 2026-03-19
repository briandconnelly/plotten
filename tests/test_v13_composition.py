"""Tests for v0.13.0 composition features."""

import pandas as pd

from plotten import (
    Aes,
    geom_point,
    ggplot,
    inset_element,
    plot_grid,
)
from plotten._composition import render_grid
from plotten._render._mpl import render


class TestInsetElement:
    def test_inset_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        inset = ggplot(df, Aes(x="x", y="y")) + geom_point(color="red")
        p = main + inset_element(inset, left=0.6, bottom=0.6, width=0.3, height=0.3)
        fig = render(p)
        # Should have at least 2 axes (main + inset)
        assert len(fig.get_axes()) >= 2

    def test_inset_custom_position(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        inset = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p = main + inset_element(inset, left=0.1, bottom=0.1, width=0.4, height=0.4)
        fig = render(p)
        assert fig is not None

    def test_multiple_insets(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        main = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p = (
            main
            + inset_element(ggplot(df, Aes(x="x", y="y")) + geom_point(), left=0.6, bottom=0.6)
            + inset_element(ggplot(df, Aes(x="x", y="y")) + geom_point(), left=0.1, bottom=0.6)
        )
        fig = render(p)
        assert len(fig.get_axes()) >= 3


class TestSharedLegends:
    def test_collect_legends(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p1 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        p2 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        grid = plot_grid(p1, p2, ncol=2, guides="collect")
        fig = render_grid(grid)
        assert fig is not None

    def test_no_collect_default(self):
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": ["a", "b"]})
        p1 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        p2 = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point()
        grid = plot_grid(p1, p2, ncol=2)
        fig = render_grid(grid)
        assert fig is not None
