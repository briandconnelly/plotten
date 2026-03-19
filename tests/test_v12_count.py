"""Tests for geom_count / stat_sum."""

import narwhals as nw
import pandas as pd

from plotten import Aes, geom_count, ggplot, stat_sum
from plotten._render._mpl import render
from plotten.stats._count_overlap import StatCountOverlap


class TestStatCountOverlap:
    def test_compute_counts(self):
        df = pd.DataFrame({"x": [1, 1, 2, 2, 2, 3], "y": [1, 1, 2, 2, 2, 3]})
        stat = StatCountOverlap()
        result = stat.compute(df)
        frame = nw.from_native(result)
        assert "n" in frame.columns
        counts = dict(
            zip(
                frame.get_column("x").to_list(),
                frame.get_column("n").to_list(),
                strict=True,
            )
        )
        assert counts[1] == 2
        assert counts[2] == 3
        assert counts[3] == 1

    def test_unique_points(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        stat = StatCountOverlap()
        result = stat.compute(df)
        frame = nw.from_native(result)
        assert all(n == 1 for n in frame.get_column("n").to_list())


class TestGeomCount:
    def test_renders(self):
        df = pd.DataFrame(
            {
                "x": [1, 1, 1, 2, 2, 3],
                "y": [1, 1, 1, 2, 2, 3],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_count()
        fig = render(p)
        assert fig is not None

    def test_stat_sum_alias(self):
        """stat_sum should produce the same result as geom_count."""
        df = pd.DataFrame({"x": [1, 1, 2], "y": [1, 1, 2]})
        p = ggplot(df, Aes(x="x", y="y")) + stat_sum()
        fig = render(p)
        assert fig is not None
