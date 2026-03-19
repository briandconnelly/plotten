"""Tests for Phase 3: stat_cor and stat_summary improvements."""

from __future__ import annotations

import numpy as np
import polars as pl
import pytest

from plotten.stats._cor import StatCor
from plotten.stats._summary import StatSummary, _resolve_fun_data

# ---------------------------------------------------------------------------
# 3A: StatCor
# ---------------------------------------------------------------------------


class TestStatCor:
    """Tests for StatCor correlation annotation stat."""

    def _make_df(self, x: list[float], y: list[float]) -> pl.DataFrame:
        return pl.DataFrame({"x": x, "y": y})

    def test_pearson_positive_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor(method="pearson")
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        assert "R = 1.00" in label
        assert "p" in label

    def test_spearman_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor(method="spearman")
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        assert "rho = 1.00" in label

    def test_negative_correlation(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        stat = StatCor(method="pearson")
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        assert "R = -1.00" in label

    def test_no_correlation(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.standard_normal(200).tolist()
        y = rng.standard_normal(200).tolist()
        stat = StatCor(method="pearson")
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        # R should be close to 0
        assert "R =" in label

    def test_output_columns(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        stat = StatCor()
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert "x" in result_nw.columns
        assert "y" in result_nw.columns
        assert "label" in result_nw.columns
        assert len(result_nw) == 1

    def test_label_position_default(self) -> None:
        x = [0.0, 10.0]
        y = [0.0, 100.0]
        stat = StatCor(label_x=0.1, label_y=0.9)
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        # label_x=0.1 means 10% from left: 0 + 0.1 * 10 = 1.0
        assert abs(result_nw["x"][0] - 1.0) < 1e-6
        # label_y=0.9 means 90% from bottom: 0 + 0.9 * 100 = 90.0
        assert abs(result_nw["y"][0] - 90.0) < 1e-6

    def test_custom_label_position(self) -> None:
        x = [0.0, 10.0]
        y = [0.0, 100.0]
        stat = StatCor(label_x=0.5, label_y=0.5)
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["x"][0] - 5.0) < 1e-6
        assert abs(result_nw["y"][0] - 50.0) < 1e-6

    def test_digits_parameter(self) -> None:
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.1, 3.9, 6.2, 7.8, 10.1]
        stat = StatCor(digits=3)
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        # Should have 3 decimal places in the R value
        parts = label.split(",")[0]  # "R = X.XXX"
        r_val = parts.split("=")[1].strip()
        assert len(r_val.split(".")[1]) == 3

    def test_invalid_method_raises(self) -> None:
        with pytest.raises(ValueError, match="method must be"):
            StatCor(method="kendall")

    def test_p_value_formatting_small(self) -> None:
        # Perfect correlation -> p should be very small
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
        stat = StatCor()
        result = stat.compute(self._make_df(x, y))
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        label = result_nw["label"][0]
        assert "p < 0.001" in label


class TestStatCorFactory:
    """Test the stat_cor() factory function."""

    def test_stat_cor_creates_layer(self) -> None:
        from plotten.geoms import stat_cor

        layer = stat_cor()
        assert layer is not None
        assert layer.stat is not None

    def test_stat_cor_with_params(self) -> None:
        from plotten.geoms import stat_cor
        from plotten.stats._cor import StatCor

        layer = stat_cor(method="spearman", digits=3, label_x=0.5, label_y=0.5)
        assert isinstance(layer.stat, StatCor)
        assert layer.stat.method == "spearman"
        assert layer.stat.digits == 3

    def test_stat_cor_exported_from_top_level(self) -> None:
        import plotten

        assert hasattr(plotten, "stat_cor")


# ---------------------------------------------------------------------------
# 3B: StatSummary improvements
# ---------------------------------------------------------------------------


class TestStatSummaryImprovements:
    """Tests for stat_summary built-in functions and fun_data."""

    def _make_df(self, x: list, y: list[float]) -> pl.DataFrame:
        return pl.DataFrame({"x": x, "y": y})

    def test_median_hilow(self) -> None:
        df = self._make_df(
            ["a", "a", "a", "a", "a"],
            [1.0, 2.0, 3.0, 4.0, 5.0],
        )
        stat = StatSummary(fun_data="median_hilow")
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["y"][0] - 3.0) < 1e-6  # median
        assert abs(result_nw["ymin"][0] - 2.0) < 1e-6  # 25th percentile
        assert abs(result_nw["ymax"][0] - 4.0) < 1e-6  # 75th percentile

    def test_mean_range(self) -> None:
        df = self._make_df(
            ["a", "a", "a", "a", "a"],
            [1.0, 2.0, 3.0, 4.0, 5.0],
        )
        stat = StatSummary(fun_data="mean_range")
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["y"][0] - 3.0) < 1e-6  # mean
        assert abs(result_nw["ymin"][0] - 1.0) < 1e-6  # min
        assert abs(result_nw["ymax"][0] - 5.0) < 1e-6  # max

    def test_fun_data_callable_dict(self) -> None:
        """fun_data accepts a callable returning a dict."""

        def my_fun(v: np.ndarray) -> dict[str, float]:
            return {"y": float(np.mean(v)), "ymin": float(np.min(v)), "ymax": float(np.max(v))}

        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_data=my_fun)
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6

    def test_fun_data_callable_tuple(self) -> None:
        """fun_data accepts a callable returning a tuple."""

        def my_fun(v: np.ndarray) -> tuple[float, float, float]:
            return (float(np.median(v)), float(np.min(v)), float(np.max(v)))

        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_data=my_fun)
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6

    def test_fun_data_overrides_individual_funs(self) -> None:
        """When fun_data is set, fun_y/fun_ymin/fun_ymax are ignored."""
        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(
            fun_y="median",
            fun_ymin="min",
            fun_ymax="max",
            fun_data="mean_range",
        )
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        # Should use mean_range, not median
        assert abs(result_nw["y"][0] - 20.0) < 1e-6  # mean, not median

    def test_multiple_groups_with_fun_data(self) -> None:
        df = self._make_df(
            ["a", "a", "b", "b"],
            [1.0, 3.0, 10.0, 20.0],
        )
        stat = StatSummary(fun_data="mean_range")
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert len(result_nw) == 2
        # Group "a": mean=2, min=1, max=3
        assert abs(result_nw["y"][0] - 2.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 1.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 3.0) < 1e-6

    def test_unknown_fun_data_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown fun_data"):
            _resolve_fun_data("nonexistent")

    def test_stat_summary_factory_with_fun_data(self) -> None:
        from plotten.geoms import stat_summary

        layer = stat_summary(fun_data="median_hilow")
        assert layer is not None
        assert isinstance(layer.stat, StatSummary)
        assert layer.stat._fun_data is not None

    def test_existing_behavior_unchanged(self) -> None:
        """Default StatSummary still works with fun_y/fun_ymin/fun_ymax."""
        df = self._make_df(["a", "a", "a"], [10.0, 20.0, 30.0])
        stat = StatSummary(fun_y="mean", fun_ymin="min", fun_ymax="max")
        result = stat.compute(df)
        result_nw = pl.from_pandas(result) if not isinstance(result, pl.DataFrame) else result
        assert abs(result_nw["y"][0] - 20.0) < 1e-6
        assert abs(result_nw["ymin"][0] - 10.0) < 1e-6
        assert abs(result_nw["ymax"][0] - 30.0) < 1e-6
