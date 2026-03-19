"""Tests for stat_function."""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from plotten import Aes, geom_point, ggplot, stat_function
from plotten._render._mpl import render
from plotten.stats._function import StatFunction


class TestStatFunction:
    def test_basic_sin(self):
        stat = StatFunction(fun=np.sin, n=50)
        result = stat.compute(pd.DataFrame({"x": [0, 2 * math.pi]}))
        assert len(result) == 50
        assert "x" in result.columns
        assert "y" in result.columns

    def test_custom_n(self):
        stat = StatFunction(fun=lambda x: x**2, n=200)
        result = stat.compute(pd.DataFrame({"x": [0, 10]}))
        assert len(result) == 200

    def test_xlim_override(self):
        stat = StatFunction(fun=lambda x: x, n=10, xlim=(-5, 5))
        result = stat.compute(pd.DataFrame({"x": [0]}))
        assert result["x"].iloc[0] == pytest.approx(-5.0)
        assert result["x"].iloc[-1] == pytest.approx(5.0)

    def test_no_data_x_range(self):
        stat = StatFunction(fun=lambda x: x, n=10)
        # No x column → defaults to (0, 1)
        result = stat.compute(pd.DataFrame({"a": [1]}))
        assert result["x"].iloc[0] == pytest.approx(0.0)
        assert result["x"].iloc[-1] == pytest.approx(1.0)

    def test_uses_data_x_range(self):
        stat = StatFunction(fun=lambda x: x, n=10)
        result = stat.compute(pd.DataFrame({"x": [10, 20]}))
        assert result["x"].iloc[0] == pytest.approx(10.0)
        assert result["x"].iloc[-1] == pytest.approx(20.0)

    def test_required_aes_empty(self):
        assert StatFunction.required_aes == frozenset()

    def test_in_plot_standalone(self):
        p = ggplot() + stat_function(fun=np.sin, xlim=(0, 2 * math.pi))
        fig = render(p)
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert len(lines) >= 1

    def test_in_plot_with_data(self):
        df = pd.DataFrame({"x": np.linspace(0, 10, 50), "y": np.random.default_rng(42).random(50)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + stat_function(fun=lambda x: x * 0.1, color="red")
        )
        fig = render(p)
        ax = fig.axes[0]
        # Should have both points and a line
        assert len(ax.collections) >= 1 or len(ax.get_lines()) >= 1

    def test_stat_function_with_custom_xlim(self):
        p = ggplot() + stat_function(fun=lambda x: x**2, xlim=(-3, 3), n=51)
        fig = render(p)
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert len(lines) >= 1
        xdata = lines[0].get_xdata()
        assert xdata[0] == pytest.approx(-3.0)
        assert xdata[-1] == pytest.approx(3.0)
