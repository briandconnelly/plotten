from __future__ import annotations

import warnings

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import PlottenError, aes, geom_point, ggplot, scale_x_continuous
from plotten._validation import validate_data_type
from plotten.scales._position import ScaleContinuous, ScaleDiscrete
from plotten.themes._theme import theme

# --- from test_v05_validation.py ---

"""Tests for v0.5 validation and error handling."""


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
        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match="non-numeric"):
            validate_data_type("x", s, scale)

    def test_no_warn_numeric_continuous(self):

        s = pl.Series("x", [1, 2, 3])
        scale = ScaleContinuous(aesthetic="x")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            validate_data_type("x", s, scale)


# --- from test_v15_errors.py ---

"""Tests for v0.15 error message quality improvements."""


class TestMissingAestheticSuggestsColumns:
    """2A: When a mapped column doesn't exist, suggest similar column names."""

    def test_typo_column_suggests_correction(self):
        df = pl.DataFrame({"height": [1, 2, 3], "weight": [4, 5, 6]})
        p = ggplot(df, aes(x="heght", y="weight")) + geom_point()
        with pytest.raises(PlottenError, match=r"(?i)did you mean.*height"):
            p._repr_png_()

    def test_typo_column_shows_available(self):
        df = pl.DataFrame({"height": [1, 2, 3], "weight": [4, 5, 6]})
        p = ggplot(df, aes(x="heght", y="weight")) + geom_point()
        with pytest.raises(PlottenError, match=r"(?i)available columns"):
            p._repr_png_()

    def test_no_suggestion_when_column_exists(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        # Should not raise
        fig = p._repr_png_()
        assert len(fig) > 0


class TestScaleDataMismatch:
    """2B: Scale/data mismatch messages include column name and dtype."""

    def test_continuous_scale_string_data_warns_with_dtype(self):

        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match=r"non-numeric data \(dtype:"):
            validate_data_type("x", s, scale)

    def test_continuous_scale_string_data_warns_with_column_name(self):

        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match="column 'original_col'"):
            validate_data_type("x", s, scale, column_name="original_col")

    def test_discrete_scale_numeric_data_warns_with_dtype(self):
        s = pl.Series("x", [1, 2, 3])
        scale = ScaleDiscrete(aesthetic="x")
        with pytest.warns(match=r"numeric data \(dtype:"):
            validate_data_type("x", s, scale)

    def test_discrete_scale_numeric_data_warns_with_column_name(self):

        s = pl.Series("x", [1, 2, 3])
        scale = ScaleDiscrete(aesthetic="x")
        with pytest.warns(match="column 'my_numbers'"):
            validate_data_type("x", s, scale, column_name="my_numbers")


class TestThemeTypoSuggestion:
    """2C: Theme property typo suggests correct property name."""

    def test_typo_suggests_correct_property(self):
        with pytest.raises(TypeError, match=r"did you mean.*title_size"):
            theme(titel_size=20)

    def test_typo_suggests_closest_match(self):
        with pytest.raises(TypeError, match=r"did you mean.*background"):
            theme(backgrund="#fff")

    def test_completely_wrong_name_no_suggestion(self):
        with pytest.raises(TypeError, match="Unknown theme properties"):
            theme(zzzzz_nonexistent=42)

    def test_valid_property_no_error(self):
        t = theme(title_size=20)
        assert t.title_size == 20
