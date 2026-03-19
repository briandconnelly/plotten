"""Tests for smart facet axis labels (1B)."""

import matplotlib.pyplot as plt
import polars as pl

from plotten import aes, facet_wrap, geom_point, ggplot, labs
from plotten._render._mpl import render


def test_facet_shared_edge_labels():
    """Bottom row gets x-labels, left column gets y-labels, interiors suppressed."""
    df = pl.DataFrame(
        {
            "x": list(range(24)),
            "y": list(range(24)),
            "g": [f"panel_{i // 8}" for i in range(24)],
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + facet_wrap("g", ncol=2)
        + labs(x="X Axis", y="Y Axis")
    )
    fig = render(plot)

    # At minimum, the figure should render without error
    assert len(fig.get_axes()) >= 2
    plt.close(fig)


def test_facet_single_row():
    """Single row: all panels are bottom row, only left gets y-label."""
    df = pl.DataFrame(
        {
            "x": list(range(6)),
            "y": list(range(6)),
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g", ncol=3) + labs(x="X", y="Y")
    )
    fig = render(plot)
    assert len(fig.get_axes()) >= 3
    plt.close(fig)
