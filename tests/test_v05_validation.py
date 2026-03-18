"""Tests for v0.5 validation and error handling."""

from __future__ import annotations

import warnings

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import PlottenError, aes, geom_point, ggplot, scale_x_continuous


class TestValidateRequiredAes:
    def test_missing_y_raises(self):
        df = pl.DataFrame({"x": [1, 2, 3]})
        p = ggplot(df, aes(x="x")) + geom_point()
        with pytest.raises(PlottenError, match="not mapped or present in data"):
            p._repr_png_()

    def test_missing_x_raises(self):
        df = pl.DataFrame({"y": [1, 2, 3]})
        p = ggplot(df, aes(y="y")) + geom_point()
        with pytest.raises(PlottenError, match="not mapped or present in data"):
            p._repr_png_()

    def test_valid_plot_no_error(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0


class TestValidateBreaksLabels:
    def test_mismatched_lengths_raises(self):
        with pytest.raises(PlottenError, match="must have the same length"):
            scale_x_continuous(breaks=[1, 2, 3], labels=["a", "b"])

    def test_matching_lengths_ok(self):
        s = scale_x_continuous(breaks=[1, 2, 3], labels=["a", "b", "c"])
        assert s.get_labels() == ["a", "b", "c"]

    def test_none_ok(self):
        s = scale_x_continuous(breaks=[1, 2])
        assert s.get_breaks() == [1, 2]


class TestValidateDataType:
    def test_warns_continuous_on_string(self):
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleContinuous

        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match="non-numeric"):
            validate_data_type("x", s, scale)

    def test_no_warn_numeric_continuous(self):
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleContinuous

        s = pl.Series("x", [1, 2, 3])
        scale = ScaleContinuous(aesthetic="x")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            validate_data_type("x", s, scale)
