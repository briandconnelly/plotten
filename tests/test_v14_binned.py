"""Tests for Phase 4 of v0.14.0: binned scales and convenience factories."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

import polars as pl

import plotten
from plotten._render._mpl import render
from plotten.scales._base import LegendEntry
from plotten.scales._binned import (
    ScaleColorBinned,
    ScaleFillBinned,
    scale_color_fermenter,
    scale_color_steps,
    scale_fill_fermenter,
    scale_fill_steps,
)

# --- Bin computation ---


class TestBinComputation:
    def test_int_breaks_produces_correct_edges(self):
        s = ScaleColorBinned(breaks=4, limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert len(edges) == 5  # 4 bins => 5 edges
        assert edges[0] == 0.0
        assert edges[-1] == 10.0

    def test_list_breaks_used_directly(self):
        s = ScaleColorBinned(breaks=[0.0, 2.0, 5.0, 10.0], limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert edges == [0.0, 2.0, 5.0, 10.0]

    def test_edges_from_trained_data(self):
        s = ScaleColorBinned(breaks=3)
        series = pl.Series("val", [1.0, 5.0, 10.0])
        s.train(series)
        edges = s._bin_edges()
        assert len(edges) == 4
        assert abs(edges[0] - 1.0) < 1e-9
        assert abs(edges[-1] - 10.0) < 1e-9

    def test_single_bin(self):
        s = ScaleColorBinned(breaks=1, limits=(0.0, 10.0))
        edges = s._bin_edges()
        assert len(edges) == 2


# --- Value mapping ---


class TestValueMapping:
    def test_maps_values_to_hex_colors(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 4.0, 7.0])
        colors = s.map_data(series)
        assert len(colors) == 3
        assert all(c.startswith("#") for c in colors)

    def test_different_bins_get_different_colors(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 4.0, 7.0])
        colors = s.map_data(series)
        # With 3 bins covering [0,3), [3,6), [6,9], these should be different
        assert colors[0] != colors[2]

    def test_same_bin_same_color(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [1.0, 2.0])
        colors = s.map_data(series)
        assert colors[0] == colors[1]

    def test_na_value_for_none(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0), na_value="#aabbcc")
        series = pl.Series("val", [1.0, None, 7.0])
        colors = s.map_data(series)
        assert colors[1] == "#aabbcc"

    def test_boundary_values_assigned(self):
        """Values exactly on boundaries should not crash."""
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        series = pl.Series("val", [0.0, 3.0, 6.0, 9.0])
        colors = s.map_data(series)
        assert len(colors) == 4
        assert all(c.startswith("#") for c in colors)


# --- Legend entries ---


class TestLegendEntries:
    def test_one_entry_per_bin(self):
        s = ScaleColorBinned(breaks=4, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert len(entries) == 4

    def test_entries_are_legend_entry_objects(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        entries = s.legend_entries()
        for e in entries:
            assert isinstance(e, LegendEntry)

    def test_labels_contain_range(self):
        s = ScaleColorBinned(breaks=3, limits=(0.0, 9.0))
        entries = s.legend_entries()
        # Labels should contain en-dash separating range bounds
        for e in entries:
            assert "\u2013" in e.label

    def test_color_aesthetic_sets_color_field(self):
        s = ScaleColorBinned(aesthetic="color", breaks=2, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert all(e.color is not None for e in entries)
        assert all(e.fill is None for e in entries)

    def test_fill_aesthetic_sets_fill_field(self):
        s = ScaleFillBinned(breaks=2, limits=(0.0, 10.0))
        entries = s.legend_entries()
        assert all(e.fill is not None for e in entries)
        assert all(e.color is None for e in entries)


# --- ScaleFillBinned ---


class TestScaleFillBinned:
    def test_aesthetic_is_fill(self):
        s = ScaleFillBinned(breaks=3)
        assert s.aesthetic == "fill"

    def test_map_data_works(self):
        s = ScaleFillBinned(breaks=3, limits=(0.0, 9.0))
        colors = s.map_data(pl.Series("val", [1.0, 4.0, 7.0]))
        assert len(colors) == 3


# --- Convenience factories ---


class TestConvenienceFactories:
    def test_scale_color_steps_returns_binned(self):
        s = scale_color_steps(n=5, cmap="viridis")
        assert isinstance(s, ScaleColorBinned)
        assert s.aesthetic == "color"

    def test_scale_fill_steps_returns_binned(self):
        s = scale_fill_steps(n=5, cmap="viridis")
        assert isinstance(s, ScaleFillBinned)
        assert s.aesthetic == "fill"

    def test_scale_color_fermenter_returns_binned(self):
        s = scale_color_fermenter(n=5, palette="Blues")
        assert isinstance(s, ScaleColorBinned)

    def test_scale_fill_fermenter_returns_binned(self):
        s = scale_fill_fermenter(n=5, palette="Blues")
        assert isinstance(s, ScaleFillBinned)

    def test_factories_exported_from_plotten(self):
        assert hasattr(plotten, "scale_color_steps")
        assert hasattr(plotten, "scale_fill_steps")
        assert hasattr(plotten, "scale_color_fermenter")
        assert hasattr(plotten, "scale_fill_fermenter")

    def test_classes_exported_from_plotten(self):
        assert hasattr(plotten, "ScaleColorBinned")
        assert hasattr(plotten, "ScaleFillBinned")


# --- End-to-end rendering ---


class TestEndToEnd:
    def test_scatter_with_binned_color(self):
        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [2.0, 4.0, 1.0, 3.0, 5.0],
                "val": [10.0, 20.0, 30.0, 40.0, 50.0],
            }
        )
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", color="val"))
            + plotten.geom_point()
            + scale_color_steps(n=3)
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bar_with_binned_fill(self):
        df = pl.DataFrame({"x": ["a", "b", "c"], "y": [3.0, 7.0, 5.0], "val": [1.0, 5.0, 9.0]})
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", fill="val"))
            + plotten.geom_col()
            + scale_fill_steps(n=3)
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_fermenter_with_brewer_palette(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0], "z": [10.0, 50.0, 90.0]})
        p = (
            plotten.ggplot(df, plotten.aes(x="x", y="y", color="z"))
            + plotten.geom_point()
            + scale_color_fermenter(n=4, palette="Blues")
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)
