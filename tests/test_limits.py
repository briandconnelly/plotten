from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

from plotten import ScaleContinuous, aes, geom_point, ggplot, xlim, ylim
from plotten._render._mpl import render

# --- Unit tests ---


def test_xlim_returns_scale_continuous():
    s = xlim(0, 10)
    assert isinstance(s, ScaleContinuous)
    assert s.aesthetic == "x"
    assert s.get_limits() == (0, 10)


def test_ylim_returns_scale_continuous():
    s = ylim(-5, 5)
    assert isinstance(s, ScaleContinuous)
    assert s.aesthetic == "y"
    assert s.get_limits() == (-5, 5)


# --- Integration render tests ---


def test_xlim_render():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + xlim(0, 5)
    fig = render(p)
    assert fig is not None
    ax = fig.axes[0]
    assert ax.get_xlim()[0] <= 0
    assert ax.get_xlim()[1] >= 5
    plt.close(fig)


def test_ylim_render():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + ylim(0, 20)
    fig = render(p)
    assert fig is not None
    ax = fig.axes[0]
    assert ax.get_ylim()[0] <= 0
    assert ax.get_ylim()[1] >= 20
    plt.close(fig)


def test_xlim_ylim_combined():
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + xlim(-10, 10) + ylim(-10, 10)
    fig = render(p)
    assert fig is not None
    plt.close(fig)
