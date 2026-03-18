"""Tests for v0.8.0 new stats: ECDF, QQ, Bin2d."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from plotten import aes, geom_bin2d, geom_qq, geom_qq_line, ggplot, stat_ecdf
from plotten._render._mpl import render
from plotten.stats._bin2d import StatBin2d
from plotten.stats._ecdf import StatECDF
from plotten.stats._qq import StatQQ, StatQQLine

matplotlib.use("Agg")


class TestStatECDF:
    def test_compute_polars(self):
        df = pl.DataFrame({"x": [3.0, 1.0, 2.0, 5.0, 4.0]})
        stat = StatECDF()
        result = stat.compute(df)
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 5
        assert result_df["x"].to_list() == [1.0, 2.0, 3.0, 4.0, 5.0]
        assert result_df["y"].to_list() == [0.2, 0.4, 0.6, 0.8, 1.0]

    def test_compute_pandas(self):
        import pandas as pd

        df = pd.DataFrame({"x": [3.0, 1.0, 2.0]})
        stat = StatECDF()
        result = stat.compute(df)
        assert list(result["x"]) == [1.0, 2.0, 3.0]
        np.testing.assert_allclose(list(result["y"]), [1 / 3, 2 / 3, 1.0])

    def test_stat_ecdf_render(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
        p = ggplot(df, aes(x="x")) + stat_ecdf()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatQQ:
    def test_compute_qq(self):
        np.random.seed(42)
        data = np.random.randn(50)
        df = pl.DataFrame({"x": data.tolist()})
        stat = StatQQ()
        result = stat.compute(df)
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 50
        assert "x" in result_df.columns
        assert "y" in result_df.columns
        # y should be sorted sample values
        assert result_df["y"].to_list() == sorted(data.tolist())

    def test_compute_qq_line(self):
        np.random.seed(42)
        data = np.random.randn(50)
        df = pl.DataFrame({"x": data.tolist()})
        stat = StatQQLine()
        result = stat.compute(df)
        result_df = pl.DataFrame(result)
        assert result_df.shape[0] == 2
        assert "x" in result_df.columns
        assert "y" in result_df.columns

    def test_geom_qq_render(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(30).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_geom_qq_line_render(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(30).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq_line()
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_qq_combined(self):
        np.random.seed(42)
        df = pl.DataFrame({"x": np.random.randn(50).tolist()})
        p = ggplot(df, aes(x="x")) + geom_qq() + geom_qq_line()
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatBin2d:
    def test_compute_bin2d(self):
        np.random.seed(42)
        df = pl.DataFrame(
            {
                "x": np.random.randn(100).tolist(),
                "y": np.random.randn(100).tolist(),
            }
        )
        stat = StatBin2d(bins=5)
        result = stat.compute(df)
        result_df = pl.DataFrame(result)
        assert "x" in result_df.columns
        assert "y" in result_df.columns
        assert "fill" in result_df.columns
        assert all(f > 0 for f in result_df["fill"].to_list())

    def test_geom_bin2d_render(self):
        np.random.seed(42)
        df = pl.DataFrame(
            {
                "x": np.random.randn(100).tolist(),
                "y": np.random.randn(100).tolist(),
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_bin2d(bins=5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bin2d_pandas(self):
        import pandas as pd

        np.random.seed(42)
        df = pd.DataFrame(
            {
                "x": np.random.randn(50),
                "y": np.random.randn(50),
            }
        )
        stat = StatBin2d(bins=5)
        result = stat.compute(df)
        assert "x" in result.columns
        assert "fill" in result.columns
