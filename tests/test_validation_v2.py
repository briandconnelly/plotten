"""Tests for validation improvements: param warnings, aesthetic checks, strict mode."""

from __future__ import annotations

import warnings

import pandas as pd
import pytest

from plotten._validation import (
    PlottenWarning,
    RenderError,
    ValidationError,
    plotten_warn,
    set_strict,
    validate_aesthetic_value,
    validate_alpha,
    validate_color,
    validate_geom_params,
    validate_size,
)

# ---------------------------------------------------------------------------
# plotten_warn + strict mode
# ---------------------------------------------------------------------------


class TestPlottenWarn:
    def test_warn_issues_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            plotten_warn("test warning")
        assert len(w) == 1
        assert issubclass(w[0].category, PlottenWarning)
        assert "test warning" in str(w[0].message)

    def test_strict_mode_raises(self):
        set_strict(True)
        try:
            with pytest.raises(ValidationError, match="test error"):
                plotten_warn("test error")
        finally:
            set_strict(False)

    def test_strict_disable(self):
        set_strict(True)
        set_strict(False)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            plotten_warn("not an error")
        assert len(w) == 1


# ---------------------------------------------------------------------------
# Unknown geom params
# ---------------------------------------------------------------------------


class TestValidateGeomParams:
    def test_no_warning_for_valid_params(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_geom_params(
                "geom_point",
                {"color": "red", "size": 50},
                frozenset({"color", "size", "alpha", "shape"}),
            )
        assert len(w) == 0

    def test_warning_for_unknown_param(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_geom_params(
                "geom_point",
                {"siz": 50},
                frozenset({"color", "size", "alpha", "shape"}),
            )
        assert len(w) == 1
        assert "siz" in str(w[0].message)
        assert "size" in str(w[0].message)

    def test_warning_includes_valid_params(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_geom_params(
                "geom_point",
                {"unknown_param": 1},
                frozenset({"color", "size"}),
            )
        assert len(w) == 1
        assert "Valid parameters" in str(w[0].message)

    def test_strict_mode_raises_for_unknown_param(self):
        set_strict(True)
        try:
            with pytest.raises(ValidationError, match="siz"):
                validate_geom_params(
                    "geom_point",
                    {"siz": 50},
                    frozenset({"color", "size", "alpha"}),
                )
        finally:
            set_strict(False)


# ---------------------------------------------------------------------------
# Aesthetic value validation
# ---------------------------------------------------------------------------


class TestValidateAestheticValue:
    def test_valid_shape(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("shape", "o")
        assert len(w) == 0

    def test_invalid_shape(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("shape", "triangle")
        assert len(w) == 1
        assert "Invalid shape" in str(w[0].message)

    def test_valid_linetype(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("linetype", "dashed")
        assert len(w) == 0

    def test_invalid_linetype(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("linetype", "daashed")
        assert len(w) == 1
        assert "Invalid linetype" in str(w[0].message)

    def test_valid_hatch(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("hatch", "//")
        assert len(w) == 0

    def test_invalid_hatch(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("hatch", "invalid")
        assert len(w) == 1
        assert "Invalid hatch" in str(w[0].message)

    def test_non_string_shape_skipped(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_aesthetic_value("shape", 42)
        assert len(w) == 0


# ---------------------------------------------------------------------------
# Color validation
# ---------------------------------------------------------------------------


class TestValidateColor:
    def test_valid_named_color(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_color("red")
        assert len(w) == 0

    def test_valid_hex_color(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_color("#FF0000")
        assert len(w) == 0

    def test_invalid_hex_color(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_color("#ZZZ")
        assert len(w) == 1
        assert "Invalid color" in str(w[0].message)

    def test_invalid_named_color_with_suggestion(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_color("bleu")
        assert len(w) == 1
        assert "blue" in str(w[0].message)

    def test_non_string_skipped(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_color((1.0, 0.0, 0.0))
        assert len(w) == 0


# ---------------------------------------------------------------------------
# Alpha / size validation
# ---------------------------------------------------------------------------


class TestValidateAlpha:
    def test_valid_alpha(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_alpha(0.5)
        assert len(w) == 0

    def test_alpha_too_high(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_alpha(2.0)
        assert len(w) == 1
        assert "outside the valid range" in str(w[0].message)

    def test_alpha_negative(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_alpha(-0.5)
        assert len(w) == 1


class TestValidateSize:
    def test_valid_size(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_size(50)
        assert len(w) == 0

    def test_negative_size(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_size(-5)
        assert len(w) == 1
        assert "negative" in str(w[0].message)


# ---------------------------------------------------------------------------
# Integration: geom factory validation
# ---------------------------------------------------------------------------


class TestGeomFactoryValidation:
    def test_geom_point_valid_call(self):
        from plotten.geoms import geom_point

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            geom_point(color="steelblue", size=50, alpha=0.8)
        plotten_warnings = [x for x in w if issubclass(x.category, PlottenWarning)]
        assert len(plotten_warnings) == 0

    def test_geom_point_unknown_param_warns(self):
        from plotten.geoms import geom_point

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            geom_point(siz=50)
        plotten_warnings = [x for x in w if issubclass(x.category, PlottenWarning)]
        assert len(plotten_warnings) == 1
        assert "siz" in str(plotten_warnings[0].message)

    def test_geom_point_alpha_out_of_range_warns(self):
        from plotten.geoms import geom_point

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            geom_point(alpha=2.0)
        plotten_warnings = [x for x in w if issubclass(x.category, PlottenWarning)]
        assert any("outside the valid range" in str(pw.message) for pw in plotten_warnings)

    def test_geom_point_negative_size_warns(self):
        from plotten.geoms import geom_point

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            geom_point(size=-5)
        plotten_warnings = [x for x in w if issubclass(x.category, PlottenWarning)]
        assert any("negative" in str(pw.message) for pw in plotten_warnings)


# ---------------------------------------------------------------------------
# Matplotlib draw error wrapping
# ---------------------------------------------------------------------------


class TestDrawErrorWrapping:
    def test_render_error_wrapped(self):
        """Matplotlib errors during geom.draw() should be wrapped with context."""
        from plotten import aes, geom_point, ggplot
        from plotten._render._mpl import render

        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = ggplot(df, aes(x="x", y="y")) + geom_point()

        original_draw = plot.layers[0].geom.draw

        def bad_draw(data, ax, params):
            msg = "test draw error"
            raise ValueError(msg)

        plot.layers[0].geom.draw = bad_draw  # type: ignore[attr-defined]

        with pytest.raises(RenderError, match="Error rendering geom_point"):
            render(plot)

        plot.layers[0].geom.draw = original_draw  # type: ignore[attr-defined]
