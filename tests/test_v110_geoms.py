"""Tests for Phase 3 of v1.1.0: geom_quantile, stat_quantile, position_dodge2."""

from __future__ import annotations

import numpy as np

from plotten.geoms._quantile import GeomQuantile
from plotten.positions._dodge import PositionDodge
from plotten.positions._dodge2 import PositionDodge2, position_dodge2
from plotten.stats._quantile import StatQuantile

# ---------------------------------------------------------------------------
# StatQuantile
# ---------------------------------------------------------------------------


class TestStatQuantile:
    def test_default_quantiles(self):
        stat = StatQuantile()
        assert stat.quantiles == [0.25, 0.5, 0.75]
        assert stat.n_points == 100

    def test_custom_quantiles(self):
        stat = StatQuantile(quantiles=[0.1, 0.9], n_points=50)
        assert stat.quantiles == [0.1, 0.9]
        assert stat.n_points == 50

    def test_required_aes(self):
        stat = StatQuantile()
        assert stat.required_aes == frozenset({"x", "y"})

    def test_compute_produces_correct_columns(self):
        import narwhals as nw

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        stat = StatQuantile(quantiles=[0.25, 0.5, 0.75], n_points=20)
        result = nw.from_native(stat.compute(df))

        cols = set(result.columns)
        assert "x" in cols
        assert "y" in cols
        assert "group" in cols

    def test_compute_output_length(self):
        import narwhals as nw

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        n_points = 20
        quantiles = [0.25, 0.5, 0.75]
        stat = StatQuantile(quantiles=quantiles, n_points=n_points)
        result = nw.from_native(stat.compute(df))

        expected_len = n_points * len(quantiles)
        assert len(result) == expected_len

    def test_compute_groups_match_quantiles(self):
        import narwhals as nw

        rng = np.random.default_rng(42)
        x = rng.uniform(0, 10, 50).tolist()
        y = [2 * xi + rng.normal(0, 1) for xi in x]
        df = nw.to_native(nw.from_dict({"x": x, "y": y}, backend="polars"))

        quantiles = [0.1, 0.5, 0.9]
        stat = StatQuantile(quantiles=quantiles, n_points=20)
        result = nw.from_native(stat.compute(df))

        groups = sorted(set(result.get_column("group").to_list()))
        assert groups == sorted(quantiles)

    def test_quantile_regression_linear_data(self):
        """With perfectly linear data, all quantile lines should have similar slopes."""
        x = np.arange(0.0, 10.0, 0.1)
        y = 3.0 * x + 5.0
        slope, intercept = StatQuantile._quantile_regression(x, y, 0.5)
        assert abs(slope - 3.0) < 0.1
        assert abs(intercept - 5.0) < 0.5

    def test_median_quantile_close_to_ols_for_symmetric_noise(self):
        """For symmetric noise, median regression should be close to OLS."""
        rng = np.random.default_rng(123)
        x = np.linspace(0, 10, 200)
        y = 2.0 * x + 1.0 + rng.normal(0, 0.5, 200)
        slope, intercept = StatQuantile._quantile_regression(x, y, 0.5)
        assert abs(slope - 2.0) < 0.3
        assert abs(intercept - 1.0) < 1.0


# ---------------------------------------------------------------------------
# GeomQuantile
# ---------------------------------------------------------------------------


class TestGeomQuantile:
    def test_required_aes(self):
        geom = GeomQuantile()
        assert geom.required_aes == frozenset({"x", "y"})

    def test_supports_group_splitting(self):
        geom = GeomQuantile()
        assert geom.supports_group_splitting is True

    def test_default_stat_is_stat_quantile(self):
        geom = GeomQuantile()
        stat = geom.default_stat()
        assert isinstance(stat, StatQuantile)
        assert stat.quantiles == [0.25, 0.5, 0.75]

    def test_custom_quantiles_passed_to_stat(self):
        geom = GeomQuantile(quantiles=[0.1, 0.9], n_points=50)
        stat = geom.default_stat()
        assert stat.quantiles == [0.1, 0.9]
        assert stat.n_points == 50

    def test_draw(self):
        """GeomQuantile.draw should call ax.plot."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        geom = GeomQuantile()
        data = {"x": [1, 2, 3], "y": [2, 4, 6]}
        geom.draw(data, ax, {})
        # Should have drawn one line
        assert len(ax.lines) == 1
        plt.close(fig)

    def test_draw_with_params(self):
        """GeomQuantile.draw should pass through aesthetic params."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        geom = GeomQuantile()
        data = {"x": [1, 2, 3], "y": [2, 4, 6]}
        geom.draw(data, ax, {"color": "red", "alpha": 0.5, "size": 2})
        line = ax.lines[0]
        assert line.get_alpha() == 0.5
        assert line.get_linewidth() == 2
        plt.close(fig)


# ---------------------------------------------------------------------------
# PositionDodge2
# ---------------------------------------------------------------------------


class TestPositionDodge2:
    def test_default_params(self):
        pos = PositionDodge2()
        assert pos.width == 0.9
        assert pos.padding == 0.1

    def test_custom_params(self):
        pos = PositionDodge2(width=0.8, padding=0.2)
        assert pos.width == 0.8
        assert pos.padding == 0.2

    def test_no_x_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"y": [1, 2, 3]}
        result = pos.adjust(data, {})
        assert result == data

    def test_no_group_key_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"x": [1, 2, 3]}
        result = pos.adjust(data, {})
        assert result == data

    def test_single_group_returns_unchanged(self):
        pos = PositionDodge2()
        data = {"x": [1, 2, 3], "fill": ["a", "a", "a"]}
        result = pos.adjust(data, {})
        assert result["x"] == [1, 2, 3]

    def test_two_groups_dodge(self):
        pos = PositionDodge2(width=0.9, padding=0.0)
        data = {"x": [1, 1], "fill": ["a", "b"]}
        params: dict = {}
        result = pos.adjust(data, params)
        # With padding=0, element_width = 0.9 / 2 = 0.45
        # offsets: -0.225, +0.225
        assert len(result["x"]) == 2
        assert result["x"][0] < 1.0
        assert result["x"][1] > 1.0
        # Check symmetry
        assert abs((result["x"][0] + result["x"][1]) / 2 - 1.0) < 1e-10
        # Check that width is set in params
        assert "width" in params

    def test_dodge2_narrower_than_dodge_with_padding(self):
        """With padding > 0, dodge2 element width should be narrower than dodge."""
        dodge = PositionDodge(width=0.9)
        dodge2 = PositionDodge2(width=0.9, padding=0.3)

        data = {"x": [1, 1, 1], "fill": ["a", "b", "c"]}
        params_d: dict = {}
        params_d2: dict = {}
        dodge.adjust(dict(data), params_d)
        dodge2.adjust(dict(data), params_d2)

        # dodge width = 0.9 / 3 = 0.3
        # dodge2 width = 0.9 * (1 - 0.3) / 3 = 0.21
        assert params_d2["width"] < params_d["width"]

    def test_position_dodge2_factory(self):
        pos = position_dodge2(width=0.8, padding=0.15)
        assert isinstance(pos, PositionDodge2)
        assert pos.width == 0.8
        assert pos.padding == 0.15


# ---------------------------------------------------------------------------
# geom_quantile factory
# ---------------------------------------------------------------------------


class TestGeomQuantileFactory:
    def test_geom_quantile_returns_layer(self):
        from plotten._layer import Layer
        from plotten.geoms import geom_quantile

        layer = geom_quantile()
        assert isinstance(layer, Layer)
        assert isinstance(layer.geom, GeomQuantile)
        assert isinstance(layer.stat, StatQuantile)

    def test_geom_quantile_custom_quantiles(self):
        from plotten.geoms import geom_quantile

        layer = geom_quantile(quantiles=[0.1, 0.9])
        assert isinstance(layer.stat, StatQuantile)
        assert layer.stat.quantiles == [0.1, 0.9]

    def test_geom_quantile_custom_n_points(self):
        from plotten.geoms import geom_quantile

        layer = geom_quantile(n_points=50)
        assert isinstance(layer.stat, StatQuantile)
        assert layer.stat.n_points == 50


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------


class TestExports:
    def test_stat_quantile_in_stats_init(self):
        from plotten.stats import StatQuantile as _S

        assert _S is StatQuantile

    def test_geom_quantile_in_geoms_init(self):
        from plotten.geoms import GeomQuantile as _G

        assert _G is GeomQuantile

    def test_position_dodge2_in_positions_init(self):
        from plotten.positions import PositionDodge2 as _P
        from plotten.positions import position_dodge2 as _f

        assert _P is PositionDodge2
        assert _f is position_dodge2

    def test_top_level_exports(self):
        import plotten

        assert hasattr(plotten, "geom_quantile")
        assert hasattr(plotten, "PositionDodge2")
        assert hasattr(plotten, "position_dodge2")
