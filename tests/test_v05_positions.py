"""Tests for v0.5 position adjustments."""

from __future__ import annotations

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import (
    aes,
    geom_col,
    geom_point,
    ggplot,
    position_dodge,
    position_fill,
    position_identity,
    position_jitter,
    position_nudge,
    position_stack,
)
from plotten.positions import (
    PositionDodge,
    PositionFill,
    PositionIdentity,
    PositionJitter,
    PositionNudge,
    PositionStack,
)


class TestPositionIdentity:
    def test_no_op(self):
        data = {"x": [1, 2, 3], "y": [4, 5, 6]}
        result = PositionIdentity().adjust(data, {})
        assert result is data

    def test_convenience(self):
        pos = position_identity()
        assert isinstance(pos, PositionIdentity)


class TestPositionDodge:
    def test_offsets_per_group(self):
        data = {
            "x": [1, 1, 2, 2],
            "y": [10, 20, 30, 40],
            "fill": ["a", "b", "a", "b"],
        }
        params: dict = {}
        result = PositionDodge(width=0.9).adjust(data, params)
        # Group "a" should be offset left, "b" right
        assert result["x"][0] < 1  # a at x=1
        assert result["x"][1] > 1  # b at x=1
        assert result["x"][2] < 2  # a at x=2
        assert result["x"][3] > 2  # b at x=2
        assert "width" in params

    def test_no_group_key(self):
        data = {"x": [1, 2], "y": [3, 4]}
        result = PositionDodge().adjust(data, {})
        assert result["x"] == [1, 2]

    def test_single_group(self):
        data = {"x": [1, 2], "y": [3, 4], "fill": ["a", "a"]}
        result = PositionDodge().adjust(data, {})
        assert result["x"] == [1, 2]

    def test_uses_color_group(self):
        data = {"x": [1, 1], "y": [10, 20], "color": ["r", "b"]}
        result = PositionDodge().adjust(data, {})
        assert result["x"][0] != result["x"][1]

    def test_convenience(self):
        pos = position_dodge(width=0.8)
        assert isinstance(pos, PositionDodge)
        assert pos.width == 0.8


class TestPositionStack:
    def test_cumulative_y(self):
        data = {
            "x": [1, 1, 2, 2],
            "y": [10, 20, 30, 40],
            "fill": ["a", "b", "a", "b"],
        }
        result = PositionStack().adjust(data, {})
        # At x=1: a gets ymin=0, y=10; b gets ymin=10, y=30
        assert result["ymin"][0] == 0
        assert result["y"][0] == 10
        assert result["ymin"][1] == 10
        assert result["y"][1] == 30
        # At x=2: a gets ymin=0, y=30; b gets ymin=30, y=70
        assert result["ymin"][2] == 0
        assert result["y"][2] == 30
        assert result["ymin"][3] == 30
        assert result["y"][3] == 70

    def test_no_groups(self):
        data = {"x": [1, 2], "y": [3, 4]}
        result = PositionStack().adjust(data, {})
        assert result == data

    def test_convenience(self):
        pos = position_stack()
        assert isinstance(pos, PositionStack)


class TestPositionFill:
    def test_normalizes_to_01(self):
        data = {
            "x": [1, 1],
            "y": [30, 70],
            "fill": ["a", "b"],
        }
        result = PositionFill().adjust(data, {})
        assert result["ymin"][0] == pytest.approx(0.0)
        assert result["y"][0] == pytest.approx(0.3)
        assert result["ymin"][1] == pytest.approx(0.3)
        assert result["y"][1] == pytest.approx(1.0)

    def test_convenience(self):
        pos = position_fill()
        assert isinstance(pos, PositionFill)


class TestPositionJitter:
    def test_changes_values(self):
        data = {"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]}
        result = PositionJitter(width=0.4, seed=42).adjust(data, {})
        assert result["x"] != data["x"]
        # y should be unchanged with height=0
        assert result["y"] == data["y"]

    def test_reproducible_with_seed(self):
        data = {"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]}
        r1 = PositionJitter(width=0.4, seed=42).adjust(data, {})
        r2 = PositionJitter(width=0.4, seed=42).adjust(data, {})
        assert r1["x"] == r2["x"]

    def test_height_jitter(self):
        data = {"x": [1.0], "y": [1.0]}
        result = PositionJitter(width=0, height=0.5, seed=1).adjust(data, {})
        assert result["x"] == data["x"]
        assert result["y"] != data["y"]

    def test_convenience(self):
        pos = position_jitter(width=0.2, height=0.1, seed=99)
        assert isinstance(pos, PositionJitter)
        assert pos.width == 0.2


class TestPositionNudge:
    def test_shifts_exact(self):
        data = {"x": [1, 2, 3], "y": [10, 20, 30]}
        result = PositionNudge(x=0.5, y=-1).adjust(data, {})
        assert result["x"] == [1.5, 2.5, 3.5]
        assert result["y"] == [9, 19, 29]

    def test_no_shift(self):
        data = {"x": [1], "y": [2]}
        result = PositionNudge().adjust(data, {})
        assert result["x"] == [1]
        assert result["y"] == [2]

    def test_convenience(self):
        pos = position_nudge(x=1, y=2)
        assert isinstance(pos, PositionNudge)
        assert pos.x == 1
        assert pos.y == 2


class TestPositionIntegration:
    """Integration tests: render with position adjustments."""

    @pytest.fixture
    def grouped_data(self):
        return pl.DataFrame(
            {
                "x": ["a", "a", "b", "b"],
                "y": [10, 20, 30, 40],
                "g": ["X", "Y", "X", "Y"],
            }
        )

    def test_dodge_col_renders(self, grouped_data):
        p = ggplot(grouped_data, aes(x="x", y="y", fill="g")) + geom_col(position=position_dodge())
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_stack_col_renders(self, grouped_data):
        p = ggplot(grouped_data, aes(x="x", y="y", fill="g")) + geom_col(position=position_stack())
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_jitter_point_renders(self):
        df = pl.DataFrame({"x": [1, 1, 1, 2, 2, 2], "y": [1, 2, 3, 1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point(position=position_jitter(seed=42))
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_fill_col_renders(self, grouped_data):
        p = ggplot(grouped_data, aes(x="x", y="y", fill="g")) + geom_col(position=position_fill())
        fig = p._repr_png_()
        assert len(fig) > 0
