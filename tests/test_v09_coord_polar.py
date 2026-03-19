"""Tests for coord_polar."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from plotten import Aes, coord_polar, geom_bar, geom_line, geom_point, ggplot
from plotten._render._mpl import render
from plotten.coords._polar import CoordPolar


class TestCoordPolar:
    def test_factory(self):
        c = coord_polar()
        assert isinstance(c, CoordPolar)
        assert c.theta == "x"
        assert c.start == 0
        assert c.direction == 1

    def test_theta_y(self):
        c = coord_polar(theta="y")
        assert c.theta == "y"

    def test_custom_start(self):
        c = coord_polar(start=np.pi / 2)
        assert c.start == pytest.approx(np.pi / 2)

    def test_counterclockwise(self):
        c = coord_polar(direction=-1)
        assert c.direction == -1

    def test_polar_axes_created(self):
        df = pd.DataFrame({"x": range(6), "y": [1, 2, 3, 4, 5, 6]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar()
        fig = render(p)
        ax = fig.axes[0]
        assert ax.name == "polar"

    def test_polar_with_line(self):
        angles = np.linspace(0, 2 * np.pi, 50)
        df = pd.DataFrame({"x": angles, "y": np.abs(np.sin(2 * angles))})
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + coord_polar()
        fig = render(p)
        assert fig is not None
        assert fig.axes[0].name == "polar"

    def test_polar_with_bar(self):
        """Pie-chart style: bars in polar coords."""
        df = pd.DataFrame({"x": ["A", "B", "C"], "y": [30, 50, 20]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_bar() + coord_polar()
        fig = render(p)
        assert fig is not None
        assert fig.axes[0].name == "polar"

    def test_polar_direction(self):
        df = pd.DataFrame({"x": range(4), "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar(direction=-1)
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_theta_direction() == -1

    def test_polar_start_offset(self):
        df = pd.DataFrame({"x": range(4), "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_polar(start=np.pi / 2)
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_theta_offset() == pytest.approx(np.pi / 2)

    def test_plot_addition(self):
        """CoordPolar should be addable to a plot."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        p2 = p + coord_polar()
        assert isinstance(p2.coord, CoordPolar)

    def test_radar_style(self):
        """Radar/spider chart pattern."""
        categories = list(range(5))
        values = [3, 4, 2, 5, 1]
        # Close the polygon
        df = pd.DataFrame(
            {
                "x": [*categories, categories[0]],
                "y": [*values, values[0]],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + coord_polar()
        fig = render(p)
        assert fig is not None
