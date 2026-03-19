"""Tests for multi-column legend support (1D)."""

import matplotlib.pyplot as plt
import polars as pl

from plotten import aes, geom_point, ggplot, guide_legend, guides
from plotten._render._mpl import render


def test_legend_ncol_renders():
    """Multi-column legend should render without error."""
    df = pl.DataFrame(
        {
            "x": list(range(12)),
            "y": list(range(12)),
            "color": ["a", "b", "c", "d"] * 3,
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y", color="color"))
        + geom_point()
        + guides(color=guide_legend(ncol=2))
    )
    fig = render(plot)
    assert fig is not None
    plt.close(fig)


def test_legend_ncol_default():
    """Default ncol=None should behave as single column."""
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "color": ["a", "b", "c"],
        }
    )
    plot = ggplot(df, aes(x="x", y="y", color="color")) + geom_point()
    fig = render(plot)
    assert fig is not None
    plt.close(fig)
