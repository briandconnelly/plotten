"""Tests for geom_density_ridges."""

import narwhals as nw
import numpy as np
import pandas as pd

from plotten import Aes, geom_density_ridges, ggplot
from plotten._render._mpl import render
from plotten.stats._density_ridges import StatDensityRidges


class TestStatDensityRidges:
    def test_compute_produces_groups(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(3, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        stat = StatDensityRidges()
        result = stat.compute(df)
        frame = nw.from_native(result)
        assert "x" in frame.columns
        assert "ymin" in frame.columns
        assert "ymax" in frame.columns
        groups = set(frame.get_column("group").to_list())
        assert "A" in groups
        assert "B" in groups

    def test_baselines_offset(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(0, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        stat = StatDensityRidges()
        result = stat.compute(df)
        frame = nw.from_native(result)
        ymin_vals = frame.get_column("ymin").to_list()
        groups = frame.get_column("group").to_list()
        # Group A baseline should be 0, Group B baseline should be 1
        a_baselines = {ymin_vals[i] for i, g in enumerate(groups) if g == "A"}
        b_baselines = {ymin_vals[i] for i, g in enumerate(groups) if g == "B"}
        assert 0.0 in a_baselines
        assert 1.0 in b_baselines


class TestGeomDensityRidges:
    def test_renders(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate(
                    [
                        rng.normal(0, 1, 100),
                        rng.normal(2, 1, 100),
                        rng.normal(4, 1, 100),
                    ]
                ),
                "y": ["Group A"] * 100 + ["Group B"] * 100 + ["Group C"] * 100,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges()
        fig = render(p)
        assert fig is not None

    def test_custom_bandwidth(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": np.concatenate([rng.normal(0, 1, 50), rng.normal(3, 1, 50)]),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges(bandwidth=0.5)
        fig = render(p)
        assert fig is not None

    def test_custom_alpha(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame(
            {
                "x": rng.normal(0, 1, 100),
                "y": ["A"] * 50 + ["B"] * 50,
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_density_ridges(alpha=0.3)
        fig = render(p)
        assert fig is not None
