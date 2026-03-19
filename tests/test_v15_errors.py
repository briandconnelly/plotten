"""Tests for v0.15 error message quality improvements."""

from __future__ import annotations

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import PlottenError, aes, geom_point, ggplot
from plotten.themes._theme import theme


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
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleContinuous

        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match=r"non-numeric data \(dtype:"):
            validate_data_type("x", s, scale)

    def test_continuous_scale_string_data_warns_with_column_name(self):
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleContinuous

        s = pl.Series("x", ["a", "b", "c"])
        scale = ScaleContinuous(aesthetic="x")
        with pytest.warns(match="column 'original_col'"):
            validate_data_type("x", s, scale, column_name="original_col")

    def test_discrete_scale_numeric_data_warns_with_dtype(self):
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleDiscrete

        s = pl.Series("x", [1, 2, 3])
        scale = ScaleDiscrete(aesthetic="x")
        with pytest.warns(match=r"numeric data \(dtype:"):
            validate_data_type("x", s, scale)

    def test_discrete_scale_numeric_data_warns_with_column_name(self):
        from plotten._validation import validate_data_type
        from plotten.scales._position import ScaleDiscrete

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
