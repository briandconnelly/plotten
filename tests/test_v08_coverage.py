"""Extra coverage tests for v0.8.0 features."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import aes, geom_path, geom_step, ggplot
from plotten._render._mpl import render
from plotten.geoms._path import GeomPath

matplotlib.use("Agg")


class TestGeomPathCoverage:
    def test_path_with_size_param(self):
        df = pl.DataFrame({"x": [0.0, 1.0, 2.0], "y": [0.0, 1.0, 0.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_path(size=2)
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_path_default_stat(self):
        from plotten.stats._identity import StatIdentity

        g = GeomPath()
        assert isinstance(g.default_stat(), StatIdentity)


class TestGeomStepCoverage:
    def test_step_with_all_params(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_step(
            color="red", alpha=0.5, linetype="--", size=2
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


class TestStatQQCoveragePandas:
    def test_qq_pandas(self):
        import numpy as np
        import pandas as pd

        from plotten.stats._qq import StatQQ, StatQQLine

        np.random.seed(42)
        df = pd.DataFrame({"x": np.random.randn(20)})
        result = StatQQ().compute(df)
        assert "x" in result.columns
        assert "y" in result.columns

        result2 = StatQQLine().compute(df)
        assert len(result2) == 2


class TestLabelNumberBigMark:
    def test_label_number_default_big_mark(self):
        from plotten.scales._labels import label_number

        fmt = label_number(accuracy=1)
        assert fmt(12345.6) == "12,345.6"
