from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl
import pytest

matplotlib.use("Agg")

import plotten
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
from plotten._render._mpl import render
from plotten.positions import (
    PositionDodge,
    PositionFill,
    PositionIdentity,
    PositionJitter,
    PositionNudge,
    PositionStack,
)
from plotten.positions._jitterdodge import PositionJitterDodge

# --- from test_v05_positions.py ---

"""Tests for v0.5 position adjustments."""


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


# --- from test_v14_positions.py ---

"""Tests for Phase 2A of v0.14.0: position_jitterdodge."""


class TestPositionJitterDodge:
    def test_basic_construction(self):
        pos = PositionJitterDodge()
        assert pos.dodge_width == 0.75
        assert pos.jitter_width == 0.1
        assert pos.jitter_height == 0.0
        assert pos.seed is None

    def test_custom_params(self):
        pos = PositionJitterDodge(dodge_width=0.5, jitter_width=0.2, jitter_height=0.1, seed=42)
        assert pos.dodge_width == 0.5
        assert pos.jitter_width == 0.2
        assert pos.jitter_height == 0.1
        assert pos.seed == 42

    def test_no_x_returns_unchanged(self):
        pos = PositionJitterDodge()
        data = {"y": [1.0, 2.0, 3.0]}
        result = pos.adjust(data, {})
        assert result == data

    def test_no_group_key_applies_jitter_only(self):
        pos = PositionJitterDodge(jitter_width=0.1, seed=42)
        data = {"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]}
        result = pos.adjust(data, {})
        # x should be jittered (slightly different)
        for orig, adjusted in zip(data["x"], result["x"], strict=True):
            assert abs(adjusted - orig) <= 0.05  # jitter_width / 2
        # y should be unchanged (jitter_height=0)
        assert result["y"] == data["y"]

    def test_dodge_with_groups(self):
        pos = PositionJitterDodge(dodge_width=0.75, jitter_width=0.0, seed=42)
        data = {
            "x": [1.0, 1.0, 2.0, 2.0],
            "y": [10.0, 20.0, 30.0, 40.0],
            "fill": ["A", "B", "A", "B"],
        }
        params: dict = {}
        result = pos.adjust(data, params)

        # With 2 groups and dodge_width=0.75, group_width=0.375
        # Group A (idx 0): offset = (0 - 0.5) * 0.375 = -0.1875
        # Group B (idx 1): offset = (1 - 0.5) * 0.375 = 0.1875
        assert result["x"][0] < 1.0  # A dodged left
        assert result["x"][1] > 1.0  # B dodged right
        assert result["x"][2] < 2.0  # A dodged left
        assert result["x"][3] > 2.0  # B dodged right

    def test_dodge_and_jitter_combined(self):
        pos = PositionJitterDodge(dodge_width=0.75, jitter_width=0.1, jitter_height=0.05, seed=42)
        data = {
            "x": [1.0, 1.0, 1.0, 1.0],
            "y": [10.0, 20.0, 30.0, 40.0],
            "color": ["A", "A", "B", "B"],
        }
        result = pos.adjust(data, {})

        # All x values should be modified (dodge + jitter)
        for orig, adjusted in zip(data["x"], result["x"], strict=True):
            assert orig != adjusted

        # y values should be jittered
        for orig, adjusted in zip(data["y"], result["y"], strict=True):
            assert abs(adjusted - orig) <= 0.025  # jitter_height / 2

    def test_seed_reproducibility(self):
        pos1 = PositionJitterDodge(jitter_width=0.1, seed=123)
        pos2 = PositionJitterDodge(jitter_width=0.1, seed=123)
        data = {"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]}
        result1 = pos1.adjust(data, {})
        result2 = pos2.adjust(data, {})
        assert result1["x"] == result2["x"]

    def test_single_group_jitter_only(self):
        pos = PositionJitterDodge(jitter_width=0.1, seed=42)
        data = {
            "x": [1.0, 2.0, 3.0],
            "y": [4.0, 5.0, 6.0],
            "fill": ["A", "A", "A"],
        }
        result = pos.adjust(data, {})
        # Single group: only jitter, no dodge
        for orig, adjusted in zip(data["x"], result["x"], strict=True):
            assert abs(adjusted - orig) <= 0.05

    def test_group_key_detection_order(self):
        """fill is checked before color."""
        pos = PositionJitterDodge(dodge_width=0.75, jitter_width=0.0, seed=42)
        data = {
            "x": [1.0, 1.0],
            "y": [10.0, 20.0],
            "fill": ["A", "B"],
            "color": ["X", "X"],
        }
        result = pos.adjust(data, {})
        # Should dodge by fill (2 groups), not color (1 group)
        assert result["x"][0] != result["x"][1]

    def test_params_width_set(self):
        pos = PositionJitterDodge(dodge_width=0.75, jitter_width=0.0)
        data = {
            "x": [1.0, 1.0],
            "y": [10.0, 20.0],
            "fill": ["A", "B"],
        }
        params: dict = {}
        pos.adjust(data, params)
        assert "width" in params


class TestPositionJitterdodgeFactory:
    def test_returns_position_jitterdodge(self):
        pos = plotten.position_jitterdodge()
        assert isinstance(pos, PositionJitterDodge)

    def test_factory_params(self):
        pos = plotten.position_jitterdodge(
            dodge_width=0.5, jitter_width=0.2, jitter_height=0.1, seed=42
        )
        assert pos.dodge_width == 0.5
        assert pos.jitter_width == 0.2
        assert pos.jitter_height == 0.1
        assert pos.seed == 42

    def test_end_to_end_render(self):
        """Ensure position_jitterdodge works in a full plot render."""
        df = pl.DataFrame(
            {
                "category": ["A", "A", "B", "B", "A", "A", "B", "B"],
                "group": ["X", "Y", "X", "Y", "X", "Y", "X", "Y"],
                "value": [1.0, 2.0, 3.0, 4.0, 1.5, 2.5, 3.5, 4.5],
            }
        )
        p = (
            plotten.ggplot(df, plotten.aes(x="category", y="value", fill="group"))
            + plotten.geom_point(position=plotten.position_jitterdodge(seed=42))
            + plotten.scale_x_discrete()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- position_beeswarm ---


class TestPositionBeeswarm:
    def test_basic(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm(spacing=0.1)
        data = {"x": [1.0, 1.0, 1.0], "y": [1.0, 1.05, 1.1]}
        result = pb.adjust(data, {})
        xs = result["x"]
        # Points should have been offset to avoid overlap
        assert len(set(xs)) > 1

    def test_single_point_unchanged(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm()
        data = {"x": [1.0], "y": [2.0]}
        result = pb.adjust(data, {})
        assert result["x"] == [1.0]

    def test_no_overlap_no_adjustment(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm(spacing=0.05)
        data = {"x": [1.0, 1.0], "y": [1.0, 2.0]}  # far apart
        result = pb.adjust(data, {})
        assert result["x"] == [1.0, 1.0]

    def test_side_left(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm(spacing=0.1, side="left")
        data = {"x": [1.0, 1.0, 1.0], "y": [1.0, 1.01, 1.02]}
        result = pb.adjust(data, {})
        for x in result["x"]:
            assert x <= 1.0

    def test_side_right(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm(spacing=0.1, side="right")
        data = {"x": [1.0, 1.0, 1.0], "y": [1.0, 1.01, 1.02]}
        result = pb.adjust(data, {})
        for x in result["x"]:
            assert x >= 1.0

    def test_multiple_groups(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm(spacing=0.1)
        data = {"x": [1.0, 1.0, 2.0, 2.0], "y": [1.0, 1.01, 1.0, 1.01]}
        result = pb.adjust(data, {})
        # Group 1 and group 2 adjusted independently
        assert len(result["x"]) == 4

    def test_missing_keys(self):
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = PositionBeeswarm()
        data = {"x": [1.0, 2.0]}  # no y
        result = pb.adjust(data, {})
        assert result == data

    def test_factory_function(self):
        from plotten import position_beeswarm
        from plotten.positions._beeswarm import PositionBeeswarm

        pb = position_beeswarm(spacing=0.2, side="left")
        assert isinstance(pb, PositionBeeswarm)
        assert pb.spacing == 0.2
        assert pb.side == "left"

    def test_integration_with_geom_point(self):
        df = pl.DataFrame(
            {
                "x": ["A", "A", "A", "A", "B", "B", "B", "B"],
                "y": [1.0, 1.1, 1.2, 1.3, 2.0, 2.1, 2.2, 2.3],
            }
        )
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point(position=plotten.position_beeswarm(spacing=0.1))
            + plotten.scale_x_discrete()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)
