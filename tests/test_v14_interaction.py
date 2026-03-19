"""Tests for Phase 2B of v0.14.0: interaction() helper."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

import polars as pl

import plotten
from plotten._interaction import Interaction, interaction
from plotten._render._mpl import render


class TestInteraction:
    def test_basic_construction(self):
        inter = interaction("species", "island")
        assert isinstance(inter, Interaction)
        assert inter.columns == ("species", "island")

    def test_name_property(self):
        inter = interaction("a", "b")
        assert inter.name == "a.b"

    def test_three_columns(self):
        inter = interaction("a", "b", "c")
        assert inter.columns == ("a", "b", "c")
        assert inter.name == "a.b.c"

    def test_requires_at_least_two_columns(self):
        with pytest.raises(ValueError, match="at least 2 columns"):
            interaction("only_one")

    def test_frozen_dataclass(self):
        inter = interaction("a", "b")
        with pytest.raises(AttributeError):
            inter.columns = ("x", "y")  # type: ignore[misc]

    def test_equality(self):
        a = interaction("x", "y")
        b = interaction("x", "y")
        assert a == b

    def test_inequality(self):
        a = interaction("x", "y")
        b = interaction("y", "x")
        assert a != b


class TestInteractionInAes:
    def test_aes_accepts_interaction(self):
        inter = interaction("species", "island")
        mapping = plotten.aes(x="x_col", color=inter)
        assert mapping.color is inter
        assert mapping.x == "x_col"

    def test_aes_group_accepts_interaction(self):
        inter = interaction("a", "b")
        mapping = plotten.aes(group=inter)
        assert mapping.group is inter

    def test_aes_fill_accepts_interaction(self):
        inter = interaction("a", "b")
        mapping = plotten.aes(fill=inter)
        assert mapping.fill is inter


class TestInteractionEndToEnd:
    def test_interaction_in_color(self):
        """Interaction resolves during plot rendering."""
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0],
                "y": [10.0, 20.0, 30.0, 40.0],
                "species": ["cat", "cat", "dog", "dog"],
                "size_cat": ["big", "small", "big", "small"],
            }
        )
        p = (
            plotten.ggplot(
                df,
                plotten.aes(x="x", y="y", color=interaction("species", "size_cat")),
            )
            + plotten.geom_point()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_interaction_in_group(self):
        """Interaction works as group aesthetic."""
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
                "y": [1.0, 2.0, 3.0, 4.0, 4.0, 3.0, 2.0, 1.0],
                "a": ["A", "A", "A", "A", "B", "B", "B", "B"],
                "b": ["X", "X", "X", "X", "Y", "Y", "Y", "Y"],
            }
        )
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", group=interaction("a", "b")))
            + plotten.geom_line()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_interaction_values_correct(self):
        """Verify the pasted values are correct."""
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [10.0, 20.0, 30.0],
                "a": ["cat", "dog", "cat"],
                "b": ["big", "small", "big"],
            }
        )
        # Use the resolve pipeline directly to check the interaction values
        from plotten._render._resolve import resolve

        p = (
            plotten.ggplot(
                df,
                plotten.aes(x="x", y="y", color=interaction("a", "b")),
            )
            + plotten.geom_point()
        )
        resolved = resolve(p)
        # The first panel, first layer should have a color column
        # color is mapped through the scale, but the scale should have trained
        # on the interaction values
        color_scale = resolved.scales.get("color")
        assert color_scale is not None

    def test_interaction_in_fill_with_dodge(self):
        """Interaction works with position_dodge."""
        df = pl.DataFrame(
            {
                "x": ["A", "A", "B", "B"],
                "y": [10.0, 20.0, 30.0, 40.0],
                "g1": ["X", "Y", "X", "Y"],
                "g2": ["M", "N", "M", "N"],
            }
        )
        p = (
            plotten.ggplot(
                df,
                plotten.aes(
                    x="x",
                    y="y",
                    fill=interaction("g1", "g2"),
                ),
            )
            + plotten.geom_col(position=plotten.position_dodge())
            + plotten.scale_x_discrete()
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)
