"""Tests for v0.8.0 scale polish: reverse, sqrt, label formatters."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    label_comma,
    label_dollar,
    label_number,
    label_percent,
    label_scientific,
    scale_x_reverse,
    scale_x_sqrt,
    scale_y_continuous,
    scale_y_reverse,
    scale_y_sqrt,
)
from plotten._render._mpl import render
from plotten.scales._reverse import ScaleReverse

matplotlib.use("Agg")


class TestScaleReverse:
    def test_reverse_limits(self):
        scale = ScaleReverse(aesthetic="x")
        import pandas as pd

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
        from plotten.scales._position import ScaleContinuous

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
