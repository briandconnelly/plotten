"""Tests for v0.13.0 coord_trans and legend positioning."""

import pandas as pd
import pytest

from plotten import (
    Aes,
    coord_trans,
    geom_point,
    ggplot,
    theme,
)
from plotten._render._mpl import render
from plotten.coords._trans import CoordTrans


class TestCoordTrans:
    def test_identity(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans()
        fig = render(p)
        assert fig is not None

    def test_sqrt_y(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 4, 9, 16]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(y="sqrt")
        fig = render(p)
        assert fig is not None

    def test_log10_x(self):
        df = pd.DataFrame({"x": [1, 10, 100, 1000], "y": [1, 2, 3, 4]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(x="log10")
        fig = render(p)
        assert fig is not None

    def test_callable_transform(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(y=lambda v: v**2)
        fig = render(p)
        assert fig is not None

    def test_reverse_transform(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + coord_trans(x="reverse")
        fig = render(p)
        assert fig is not None

    def test_unknown_transform_raises(self):
        ct = CoordTrans(x="bogus")
        with pytest.raises(ValueError, match="Unknown transform"):
            ct._apply([1, 2, 3], "bogus")

    def test_transform_data(self):
        ct = CoordTrans(x="log10", y="sqrt")
        data = {"x": [10, 100], "y": [4, 9]}
        result = ct.transform_data(data, {})
        assert abs(result["x"][0] - 1.0) < 0.01
        assert abs(result["y"][0] - 2.0) < 0.01


class TestLegendPosition:
    def test_tuple_position(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_position=(0.8, 0.2))
        )
        fig = render(p)
        assert fig is not None

    def test_tuple_position_top_left(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 4, 2, 3],
                "g": ["a", "b", "a", "b"],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_position=(0.1, 0.9))
        )
        fig = render(p)
        assert fig is not None

    def test_string_position_still_works(self):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "g": ["a", "b", "c"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y", color="g")) + geom_point() + theme(legend_position="left")
        fig = render(p)
        assert fig is not None
