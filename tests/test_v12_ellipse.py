"""Tests for stat_ellipse confidence ellipses."""

import narwhals as nw
import numpy as np
import pandas as pd

from plotten import Aes, geom_point, ggplot, stat_ellipse
from plotten._render._mpl import render
from plotten.stats._ellipse import StatEllipse


class TestStatEllipse:
    def test_renders(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 50), "y": rng.normal(0, 1, 50)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_ellipse()
        fig = render(p)
        assert fig is not None

    def test_custom_level(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 50), "y": rng.normal(0, 1, 50)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_ellipse(level=0.99)
        fig = render(p)
        assert fig is not None

    def test_compute_returns_ellipse_points(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({"x": rng.normal(0, 1, 100), "y": rng.normal(0, 1, 100)})
        stat = StatEllipse(level=0.95, segments=51)
        result = stat.compute(df)
        frame = nw.from_native(result)
        assert len(frame) == 51
        assert "x" in frame.columns
        assert "y" in frame.columns

    def test_ellipse_centered_near_mean(self):
        rng = np.random.default_rng(42)
        x = rng.normal(5, 1, 200)
        y = rng.normal(10, 1, 200)
        df = pd.DataFrame({"x": x, "y": y})
        stat = StatEllipse()
        result = stat.compute(df)
        frame = nw.from_native(result)
        ex = frame.get_column("x").to_list()
        ey = frame.get_column("y").to_list()
        # Center of ellipse should be near (5, 10)
        assert abs(np.mean(ex) - 5) < 0.5
        assert abs(np.mean(ey) - 10) < 0.5

    def test_too_few_points(self):
        """With fewer than 3 points, return empty frame."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        stat = StatEllipse()
        result = stat.compute(df)
        frame = nw.from_native(result)
        assert len(frame) == 0

    def test_correlated_data(self):
        """Ellipse for correlated data should be elongated."""
        rng = np.random.default_rng(42)
        x = rng.normal(0, 1, 200)
        y = x * 2 + rng.normal(0, 0.1, 200)
        df = pd.DataFrame({"x": x, "y": y})
        stat = StatEllipse()
        result = stat.compute(df)
        frame = nw.from_native(result)
        ex = np.array(frame.get_column("x").to_list())
        ey = np.array(frame.get_column("y").to_list())
        # The y range should be much larger than x range
        assert (ey.max() - ey.min()) > (ex.max() - ex.min())
