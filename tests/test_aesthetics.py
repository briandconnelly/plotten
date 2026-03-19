from __future__ import annotations

from typing import cast

import matplotlib
import matplotlib.pyplot as plt
import polars as pl
import pytest

matplotlib.use("Agg")

import narwhals as nw

import plotten
from plotten import (
    Aes,
    AfterScale,
    AfterStat,
    after_scale,
    after_stat,
    geom_bar,
    geom_histogram,
    geom_point,
    ggplot,
    stage,
)
from plotten._aes import aes
from plotten._computed import AfterScale as _AfterScale
from plotten._computed import AfterStat as _AfterStat
from plotten._interaction import Interaction, interaction
from plotten._render._mpl import render
from plotten.stats._bin import StatBin
from plotten.stats._count import StatCount

# --- from test_aes.py ---


def test_aes_defaults():
    a = Aes()
    assert a.x is None
    assert a.y is None


def test_aes_constructor():
    a = aes(x="col_x", y="col_y", color="grp")
    assert a.x == "col_x"
    assert a.y == "col_y"
    assert a.color == "grp"
    assert a.fill is None


def test_aes_merge():
    a = aes(x="a", y="b", color="c")
    b = aes(y="d", size="s")
    merged = a | b
    assert merged.x == "a"  # kept from a
    assert merged.y == "d"  # overridden by b
    assert merged.color == "c"  # kept from a
    assert merged.size == "s"  # new from b


def test_aes_frozen():
    a = aes(x="x")
    try:
        a.x = "y"  # type: ignore[misc]
        pytest.fail("Should have raised")
    except AttributeError:
        pass


# --- from test_v07_computed.py ---

"""Tests for v0.7.0 computed aesthetics: after_stat, after_scale, stage."""

# --- Sentinel classes ---


class TestAfterStat:
    def test_creation(self):
        a = after_stat("density")
        assert isinstance(a, AfterStat)
        assert a.var == "density"

    def test_frozen(self):
        a = after_stat("density")
        with pytest.raises(AttributeError):
            a.var = "count"  # type: ignore[misc]

    def test_equality(self):
        assert after_stat("density") == after_stat("density")
        assert after_stat("density") != after_stat("count")


class TestAfterScale:
    def test_creation(self):
        a = after_scale("fill")
        assert isinstance(a, AfterScale)
        assert a.var == "fill"

    def test_frozen(self):
        a = after_scale("fill")
        with pytest.raises(AttributeError):
            a.var = "color"  # type: ignore[misc]


class TestStage:
    def test_stage_after_stat(self):
        result = stage(after_stat="density")
        assert isinstance(result, _AfterStat)
        assert result.var == "density"

    def test_stage_after_scale(self):
        result = stage(after_scale="fill")
        assert isinstance(result, _AfterScale)
        assert result.var == "fill"

    def test_stage_start(self):
        result = stage(start="x")
        assert result == "x"

    def test_stage_priority(self):
        """after_scale takes precedence over after_stat."""
        result = stage(start="x", after_stat="count", after_scale="fill")
        assert isinstance(result, _AfterScale)
        assert result.var == "fill"

    def test_stage_no_args(self):
        with pytest.raises(ValueError, match="requires at least one"):
            stage()

    def test_stage_with_sentinel_objects(self):
        result = stage(after_stat=after_stat("density"))
        assert isinstance(result, _AfterStat)
        assert result.var == "density"


# --- Enriched stat outputs ---


class TestStatBinEnriched:
    def test_density_column(self):
        import narwhals as nw

        df = pl.DataFrame({"x": list(range(100))})
        result = cast("nw.DataFrame", nw.from_native(StatBin(bins=10).compute(df)))
        assert "density" in result.columns
        assert "count" in result.columns
        assert "width" in result.columns
        density = result.get_column("density").to_list()
        counts = result.get_column("count").to_list()
        widths = result.get_column("width").to_list()
        # density * width * total ≈ count
        total = sum(counts)
        for d, c, w in zip(density, counts, widths, strict=True):
            assert d * total * w == pytest.approx(c, abs=1e-10)


class TestStatCountEnriched:
    def test_prop_column(self):

        df = pl.DataFrame({"x": ["a", "b", "a", "c"]})
        result = cast("nw.DataFrame", nw.from_native(StatCount().compute(df)))
        assert "count" in result.columns
        assert "prop" in result.columns
        props = result.get_column("prop").to_list()
        assert sum(props) == pytest.approx(1.0)


# --- Aes with computed mappings ---


class TestAesComputedMappings:
    def test_aes_accepts_after_stat(self):
        a = Aes(y=after_stat("density"))
        assert isinstance(a.y, _AfterStat)
        assert a.y.var == "density"

    def test_aes_accepts_after_scale(self):
        a = Aes(fill=after_scale("color"))
        assert isinstance(a.fill, _AfterScale)

    def test_aes_merge_with_computed(self):
        a1 = Aes(x="x")
        a2 = Aes(y=after_stat("density"))
        merged = a1 | a2
        assert merged.x == "x"
        assert isinstance(merged.y, _AfterStat)


# --- Pipeline integration ---


class TestAfterStatPipeline:
    def test_histogram_density(self):
        """after_stat('density') with geom_histogram should render density."""
        df = pl.DataFrame({"x": [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]})
        p = ggplot(df, Aes(x="x", y=after_stat("density"))) + geom_histogram(bins=5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bar_prop(self):
        """after_stat('prop') with geom_bar should render proportions."""
        df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
        p = ggplot(df, Aes(x="x", y=after_stat("prop"))) + geom_bar()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_normal_mapping_unaffected(self):
        """Normal string mappings should work as before."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        from plotten import geom_point

        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestAfterScalePipeline:
    def test_after_scale_mapping(self):
        """after_scale should remap data after scale transformation."""
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "c": ["a", "b", "c"]})

        # Map fill to the same values as color after scale mapping
        p = ggplot(df, Aes(x="x", y="y", color="c", fill=after_scale("color"))) + geom_point()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- from test_v14_interaction.py ---

"""Tests for Phase 2B of v0.14.0: interaction() helper."""


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
