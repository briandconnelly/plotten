"""Tests for v0.7.0 computed aesthetics: after_stat, after_scale, stage."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl
import pytest

from plotten import (
    Aes,
    AfterScale,
    AfterStat,
    after_scale,
    after_stat,
    geom_bar,
    geom_histogram,
    ggplot,
    stage,
)
from plotten._computed import AfterScale as _AfterScale
from plotten._computed import AfterStat as _AfterStat
from plotten._render._mpl import render
from plotten.stats._bin import StatBin
from plotten.stats._count import StatCount

matplotlib.use("Agg")


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
        result = nw.from_native(StatBin(bins=10).compute(df))
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
        import narwhals as nw

        df = pl.DataFrame({"x": ["a", "b", "a", "c"]})
        result = nw.from_native(StatCount().compute(df))
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
        from plotten import geom_point

        # Map fill to the same values as color after scale mapping
        p = ggplot(df, Aes(x="x", y="y", color="c", fill=after_scale("color"))) + geom_point()
        fig = render(p)
        assert fig is not None
        plt.close(fig)
