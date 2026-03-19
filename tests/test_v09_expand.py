"""Tests for expand parameter on continuous and discrete scales."""

from __future__ import annotations

import matplotlib
import pytest

matplotlib.use("Agg")

import pandas as pd

from plotten import (
    Aes,
    geom_bar,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_x_discrete,
    scale_y_continuous,
)
from plotten._render._mpl import render
from plotten.scales._position import ScaleContinuous, ScaleDiscrete


class TestContinuousExpand:
    def test_default_expand_matches_default_padding(self):
        s = ScaleContinuous()
        assert s._expand == (0.05, 0)

    def test_expand_overrides_padding(self):
        s = ScaleContinuous(expand=(0.1, 0.5))
        assert s._expand == (0.1, 0.5)

    def test_expand_mult_and_add(self):
        s = ScaleContinuous(expand=(0.1, 2.0))
        s.train(pd.Series([0, 100]))
        lo, hi = s.get_limits()
        # span=100, pad = 100*0.1 + 2.0 = 12.0
        assert lo == pytest.approx(-12.0)
        assert hi == pytest.approx(112.0)

    def test_expand_zero(self):
        s = ScaleContinuous(expand=(0, 0))
        s.train(pd.Series([10, 20]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(10.0)
        assert hi == pytest.approx(20.0)

    def test_expand_add_only(self):
        s = ScaleContinuous(expand=(0, 1.0))
        s.train(pd.Series([5, 15]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(4.0)
        assert hi == pytest.approx(16.0)

    def test_padding_and_expand_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            ScaleContinuous(padding=0.1, expand=(0.1, 0))

    def test_default_padding_with_expand_ok(self):
        # Default padding=0.05 should not conflict with expand
        s = ScaleContinuous(expand=(0.2, 0))
        assert s._expand == (0.2, 0)

    def test_scale_factory_accepts_expand(self):
        s = scale_x_continuous(expand=(0, 5))
        assert s._expand == (0, 5)
        assert s.aesthetic == "x"

    def test_scale_y_factory_accepts_expand(self):
        s = scale_y_continuous(expand=(0.1, 1))
        assert s._expand == (0.1, 1)
        assert s.aesthetic == "y"

    def test_expand_in_plot(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + scale_x_continuous(expand=(0, 0))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_xlim()
        assert lo == pytest.approx(1.0)
        assert hi == pytest.approx(3.0)

    def test_backward_compat_padding(self):
        s = ScaleContinuous(padding=0.1)
        assert s._expand == (0.1, 0)
        s.train(pd.Series([0, 100]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(-10.0)
        assert hi == pytest.approx(110.0)


class TestDiscreteExpand:
    def test_default_expand(self):
        s = ScaleDiscrete()
        assert s._expand == (0, 0.6)

    def test_custom_expand(self):
        s = ScaleDiscrete(expand=(0.1, 0.5))
        assert s._expand == (0.1, 0.5)

    def test_default_expand_limits(self):
        s = ScaleDiscrete()
        s.train(pd.Series(["a", "b", "c"]))
        lo, hi = s.get_limits()
        # n=3, mult=0, add=0.6 → lo=-0.6, hi=2+0.6=2.6
        assert lo == pytest.approx(-0.6)
        assert hi == pytest.approx(2.6)

    def test_expand_with_mult(self):
        s = ScaleDiscrete(expand=(0.5, 0))
        s.train(pd.Series(["a", "b", "c"]))
        lo, hi = s.get_limits()
        # n=3, lo = -0.5*2 - 0 = -1.0, hi = 2 + 0.5*2 + 0 = 3.0
        assert lo == pytest.approx(-1.0)
        assert hi == pytest.approx(3.0)

    def test_expand_zero(self):
        s = ScaleDiscrete(expand=(0, 0))
        s.train(pd.Series(["a", "b"]))
        lo, hi = s.get_limits()
        assert lo == pytest.approx(0)
        assert hi == pytest.approx(1.0)

    def test_single_level(self):
        s = ScaleDiscrete()
        s.train(pd.Series(["a"]))
        lo, hi = s.get_limits()
        # n=1, lo = -0*0 - 0.6 = -0.6, hi = 0 + 0*0 + 0.6 = 0.6
        assert lo == pytest.approx(-0.6)
        assert hi == pytest.approx(0.6)

    def test_empty_levels(self):
        s = ScaleDiscrete()
        lo, hi = s.get_limits()
        assert lo == pytest.approx(-0.5)
        assert hi == pytest.approx(0.5)

    def test_factory_accepts_expand(self):
        s = scale_x_discrete(expand=(0, 1.0))
        assert s._expand == (0, 1.0)

    def test_discrete_expand_in_plot(self):
        df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_bar() + scale_x_discrete(expand=(0, 0))
        fig = render(p)
        ax = fig.axes[0]
        lo, hi = ax.get_xlim()
        assert lo == pytest.approx(0)
        assert hi == pytest.approx(2.0)
