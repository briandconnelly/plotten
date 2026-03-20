from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

matplotlib.use("Agg")

from plotten import aes, geom_boxplot, ggplot
from plotten._render._mpl import render
from plotten._validation import StatError
from plotten.geoms import geom_signif
from plotten.stats._signif import StatSignif, _adjust_pvalues, _format_pvalue


class TestStatSignif:
    def setup_method(self):
        self.df = pd.DataFrame(
            {
                "x": ["a"] * 20 + ["b"] * 20 + ["c"] * 20,
                "y": list(range(20)) + list(range(5, 25)) + list(range(10, 30)),
            }
        )

    def test_compute_returns_expected_columns(self):
        stat = StatSignif(comparisons=[("a", "b")], test="t-test")
        result = stat.compute(self.df)
        df_result = pd.DataFrame(result)
        assert "_signif_xmin" in df_result.columns
        assert "_signif_xmax" in df_result.columns
        assert "y" in df_result.columns
        assert "p_value" in df_result.columns
        assert "label" in df_result.columns

    def test_compute_multiple_comparisons(self):
        stat = StatSignif(comparisons=[("a", "b"), ("a", "c"), ("b", "c")])
        result = stat.compute(self.df)
        df_result = pd.DataFrame(result)
        assert len(df_result) == 3

    def test_bracket_stacking(self):
        stat = StatSignif(
            comparisons=[("a", "b"), ("a", "c")],
            step_increase=0.1,
        )
        result = stat.compute(self.df)
        df_result = pd.DataFrame(result)
        assert df_result["y"].iloc[1] > df_result["y"].iloc[0]

    def test_mann_whitney(self):
        stat = StatSignif(comparisons=[("a", "b")], test="mann-whitney")
        result = stat.compute(self.df)
        df_result = pd.DataFrame(result)
        assert 0 <= df_result["p_value"].iloc[0] <= 1

    def test_unknown_test_raises(self):
        stat = StatSignif(comparisons=[("a", "b")], test="invalid")
        with pytest.raises(StatError, match="Unknown test"):
            stat.compute(self.df)


class TestPValueAdjustment:
    def test_bonferroni(self):
        pvals = [0.01, 0.04, 0.03]
        adj = _adjust_pvalues(pvals, "bonferroni")
        assert adj[0] == pytest.approx(0.03)
        assert adj[1] == pytest.approx(0.12)
        assert adj[2] == pytest.approx(0.09)

    def test_holm(self):
        pvals = [0.01, 0.04, 0.03]
        adj = _adjust_pvalues(pvals, "holm")
        assert all(0 <= p <= 1 for p in adj)
        assert adj[0] <= adj[1]  # smallest stays smallest

    def test_fdr(self):
        pvals = [0.01, 0.04, 0.03]
        adj = _adjust_pvalues(pvals, "fdr")
        assert all(0 <= p <= 1 for p in adj)

    def test_none_returns_original(self):
        pvals = [0.01, 0.04]
        assert _adjust_pvalues(pvals, None) == pvals

    def test_unknown_method_raises(self):
        with pytest.raises(StatError, match="Unknown p_adjust"):
            _adjust_pvalues([0.05], "invalid")


class TestPValueFormatting:
    def test_stars(self):
        assert _format_pvalue(0.0001) == "***"
        assert _format_pvalue(0.005) == "**"
        assert _format_pvalue(0.03) == "*"
        assert _format_pvalue(0.1) == "ns"


class TestGeomSignifRendering:
    def setup_method(self):
        self.df = pd.DataFrame(
            {
                "g": ["a"] * 20 + ["b"] * 20,
                "v": list(range(20)) + list(range(5, 25)),
            }
        )

    def test_basic_rendering(self):
        p = (
            ggplot(self.df, aes(x="g", y="v"))
            + geom_boxplot()
            + geom_signif(comparisons=[("a", "b")])
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_pvalue_format(self):
        p = (
            ggplot(self.df, aes(x="g", y="v"))
            + geom_boxplot()
            + geom_signif(comparisons=[("a", "b")], text_format="p-value")
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_multiple_comparisons_render(self):
        df = pd.DataFrame(
            {
                "g": ["a"] * 15 + ["b"] * 15 + ["c"] * 15,
                "v": list(range(15)) + list(range(5, 20)) + list(range(10, 25)),
            }
        )
        p = (
            ggplot(df, aes(x="g", y="v"))
            + geom_boxplot()
            + geom_signif(comparisons=[("a", "b"), ("a", "c"), ("b", "c")])
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_with_bonferroni_correction(self):
        df = pd.DataFrame(
            {
                "g": ["a"] * 15 + ["b"] * 15 + ["c"] * 15,
                "v": list(range(15)) + list(range(5, 20)) + list(range(10, 25)),
            }
        )
        p = (
            ggplot(df, aes(x="g", y="v"))
            + geom_boxplot()
            + geom_signif(
                comparisons=[("a", "b"), ("a", "c")],
                p_adjust="bonferroni",
            )
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)
