"""Tests for v0.11.0 scale additions: identity scales and grey scales."""

import pandas as pd

from plotten import (
    Aes,
    geom_col,
    geom_point,
    ggplot,
    scale_color_gray,
    scale_color_grey,
    scale_color_grey_continuous,
    scale_color_identity,
    scale_fill_grey,
    scale_fill_identity,
    scale_size_identity,
)
from plotten._render._mpl import render


class TestIdentityScales:
    def test_color_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "c": ["red", "blue", "green"]})
        p = ggplot(df, Aes(x="x", y="y", color="c")) + geom_point() + scale_color_identity()
        fig = render(p)
        assert fig is not None

    def test_fill_identity(self):
        df = pd.DataFrame({"x": ["a", "b"], "y": [1, 2], "f": ["#ff0000", "#0000ff"]})
        p = ggplot(df, Aes(x="x", y="y", fill="f")) + geom_col() + scale_fill_identity()
        fig = render(p)
        assert fig is not None

    def test_size_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "s": [10, 20, 30]})
        p = ggplot(df, Aes(x="x", y="y", size="s")) + geom_point() + scale_size_identity()
        fig = render(p)
        assert fig is not None

    def test_identity_no_legend(self):
        """Identity scales should produce no legend by default."""
        scale = scale_color_identity()
        assert scale.legend_entries() is None

    def test_identity_map_passthrough(self):
        """map_data should return values unchanged."""
        scale = scale_color_identity()
        values = ["red", "blue", "green"]
        # map_data should return the input as-is
        result = scale.map_data(pd.Series(values))
        # Since identity returns as-is, should be the same series
        assert list(result) == values


class TestGreyScales:
    def test_discrete_grey(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point() + scale_color_grey()
        fig = render(p)
        assert fig is not None

    def test_discrete_grey_custom_range(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_grey(start=0.0, end=1.0)
        )
        fig = render(p)
        assert fig is not None

    def test_fill_grey(self):
        df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, Aes(x="x", y="y", fill="g")) + geom_col() + scale_fill_grey()
        fig = render(p)
        assert fig is not None

    def test_gray_alias(self):
        """American spelling alias should work."""
        assert scale_color_gray is scale_color_grey

    def test_grey_legend_entries(self):
        scale = scale_color_grey(start=0.2, end=0.8)
        scale.train(pd.Series(["a", "b", "c"]))
        entries = scale.legend_entries()
        assert len(entries) == 3
        # Should be hex grey values
        for entry in entries:
            assert entry.color is not None
            assert entry.color.startswith("#")

    def test_continuous_grey(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "v": [0.0, 0.5, 1.0]})
        p = ggplot(df, Aes(x="x", y="y", color="v")) + geom_point() + scale_color_grey_continuous()
        fig = render(p)
        assert fig is not None

    def test_continuous_grey_maps_values(self):
        scale = scale_color_grey_continuous(start=0.0, end=1.0)
        scale.train(pd.Series([0.0, 10.0]))
        mapped = scale.map_data(pd.Series([0.0, 5.0, 10.0]))
        assert mapped[0] == "#000000"  # start=0.0 -> black
        assert mapped[2] == "#ffffff"  # end=1.0 -> white
