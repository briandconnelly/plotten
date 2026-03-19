"""Tests for callable breaks in continuous scales."""

import numpy as np
import pandas as pd
import pytest

from plotten import Aes, geom_point, ggplot, scale_x_continuous
from plotten._render._mpl import render
from plotten.scales._position import ScaleContinuous


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
