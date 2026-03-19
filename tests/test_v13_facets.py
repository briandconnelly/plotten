"""Tests for v0.13.0 facet enhancements."""

import pandas as pd
import pytest

from plotten import (
    Aes,
    facet_grid,
    facet_wrap,
    geom_point,
    ggplot,
    label_value,
    labeller_both,
    labeller_wrap,
)
from plotten._render._mpl import render


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 3, 5, 2],
            "group": ["A", "A", "B", "B", "C", "C"],
        }
    )


class TestCustomLabeller:
    def test_labeller_both(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=labeller_both("group"))
        )
        fig = render(p)
        assert fig is not None

    def test_labeller_wrap(self, sample_df):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [1, 2, 3, 4],
                "cat": [
                    "Very Long Category Name",
                    "Very Long Category Name",
                    "Another Long Name Here",
                    "Another Long Name Here",
                ],
            }
        )
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("cat", labeller=labeller_wrap(12))
        )
        fig = render(p)
        assert fig is not None

    def test_custom_lambda_labeller(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=lambda v: f"Group {v}")
        )
        fig = render(p)
        assert fig is not None

    def test_label_value_default(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", labeller=label_value)
        )
        fig = render(p)
        assert fig is not None

    def test_labeller_on_facet_grid(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_grid(cols="group", labeller=labeller_both("group"))
        )
        fig = render(p)
        assert fig is not None


class TestStripPosition:
    def test_strip_bottom(self, sample_df):
        p = (
            ggplot(sample_df, Aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("group", strip_position="bottom")
        )
        fig = render(p)
        assert fig is not None

    def test_strip_top_default(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group")
        fig = render(p)
        assert fig is not None


class TestDropParameter:
    def test_drop_true_default(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group", drop=True)
        fig = render(p)
        assert fig is not None

    def test_drop_false(self, sample_df):
        p = ggplot(sample_df, Aes(x="x", y="y")) + geom_point() + facet_wrap("group", drop=False)
        fig = render(p)
        assert fig is not None
