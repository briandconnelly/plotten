"""Tests for Pythonic API improvements: enums, ggsave deprecation, options()."""

from __future__ import annotations

import inspect
import warnings

import pandas as pd
import pytest

import plotten
from plotten import (
    Direction,
    FacetScales,
    SizeUnit,
    SmoothMethod,
    StripPosition,
    aes,
    facet_grid,
    facet_wrap,
    geom_point,
    geom_smooth,
    ggplot,
    ggsave,
    options,
    set_strict,
    theme_dark,
    theme_get,
    theme_minimal,
)


@pytest.fixture
def simple_plot():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    return ggplot(df, aes(x="x", y="y")) + geom_point()


# --- Enum type annotations ---


class TestEnumParameters:
    """Enums are accepted and bare strings still work."""

    def test_facet_wrap_scales_enum(self):
        f = facet_wrap("g", scales=FacetScales.FREE)
        assert f.scales == "free"

    def test_facet_wrap_scales_string(self):
        f = facet_wrap("g", scales="free_x")
        assert f.scales == "free_x"

    def test_facet_wrap_strip_position_enum(self):
        f = facet_wrap("g", strip_position=StripPosition.BOTTOM)
        assert f.strip_position == "bottom"

    def test_facet_wrap_strip_position_string(self):
        f = facet_wrap("g", strip_position="bottom")
        assert f.strip_position == "bottom"

    def test_facet_wrap_direction_enum(self):
        f = facet_wrap("g", dir=Direction.VERTICAL)
        assert f.dir == "v"

    def test_facet_wrap_direction_string(self):
        f = facet_wrap("g", dir="v")
        assert f.dir == "v"

    def test_facet_grid_scales_enum(self):
        f = facet_grid(rows="r", scales=FacetScales.FREE_Y)
        assert f.scales == "free_y"

    def test_facet_grid_scales_string(self):
        f = facet_grid(rows="r", scales="free_y")
        assert f.scales == "free_y"

    def test_geom_smooth_method_enum(self):
        layer = geom_smooth(method=SmoothMethod.OLS)
        assert layer.geom._method == "ols"  # type: ignore[attr-defined]

    def test_geom_smooth_method_string(self):
        layer = geom_smooth(method="loess")
        assert layer.geom._method == "loess"  # type: ignore[attr-defined]

    def test_save_units_enum(self, simple_plot, tmp_path):
        path = str(tmp_path / "test.png")
        simple_plot.save(path, units=SizeUnit.CM, width=10, height=8)
        assert (tmp_path / "test.png").exists()

    def test_save_units_string(self, simple_plot, tmp_path):
        path = str(tmp_path / "test.png")
        simple_plot.save(path, units="cm", width=10, height=8)
        assert (tmp_path / "test.png").exists()

    def test_enums_exported(self):
        """All new enums are accessible from the top-level package."""
        assert hasattr(plotten, "Direction")
        assert hasattr(plotten, "StripPosition")

    def test_enum_defaults_match_string_values(self):
        """Default enum values produce the same strings as the old defaults."""
        assert FacetScales.FIXED == "fixed"
        assert StripPosition.TOP == "top"
        assert Direction.HORIZONTAL == "h"
        assert SmoothMethod.LOESS == "loess"
        assert SizeUnit.INCHES == "in"


# --- ggsave deprecation ---


class TestGgsaveDeprecation:
    def test_ggsave_emits_deprecation_warning(self, simple_plot, tmp_path):
        out = tmp_path / "plot.png"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ggsave(simple_plot, out)
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) == 1
            assert "plot.save()" in str(deprecation_warnings[0].message)

    def test_ggsave_still_produces_output(self, simple_plot, tmp_path):
        out = tmp_path / "plot.png"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ggsave(simple_plot, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_plot_save_transparent(self, simple_plot, tmp_path):
        path = str(tmp_path / "transparent.png")
        simple_plot.save(path, transparent=True)
        assert (tmp_path / "transparent.png").exists()

    def test_plot_save_default_dpi(self):
        sig = inspect.signature(plotten.Plot.save)
        assert sig.parameters["dpi"].default == 300


# --- options() context manager ---


class TestOptions:
    def test_theme_override_and_restore(self):
        original = theme_get()
        dark = theme_dark()
        with options(theme=dark):
            assert theme_get() is dark
        assert theme_get() is original

    def test_theme_restore_on_exception(self):
        original = theme_get()
        with pytest.raises(RuntimeError), options(theme=theme_minimal()):
            raise RuntimeError("boom")
        assert theme_get() is original

    def test_strict_override_and_restore(self):
        set_strict(False)
        with options(strict=True), pytest.raises(plotten.ValidationError):
            plotten._validation.plotten_warn("test warning")
        # Should be back to non-strict
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            plotten._validation.plotten_warn("test warning")
            assert len(w) == 1

    def test_strict_restore_on_exception(self):
        set_strict(False)
        with pytest.raises(RuntimeError), options(strict=True):
            raise RuntimeError("boom")
        # Should be back to non-strict
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            plotten._validation.plotten_warn("test warning")
            assert len(w) == 1

    def test_options_no_args_is_noop(self):
        original_theme = theme_get()
        with options():
            assert theme_get() is original_theme
        assert theme_get() is original_theme

    def test_options_exported(self):
        assert hasattr(plotten, "options")

    def test_theme_and_strict_together(self):
        original_theme = theme_get()
        set_strict(False)
        dark = theme_dark()
        with options(theme=dark, strict=True):
            assert theme_get() is dark
            with pytest.raises(plotten.ValidationError):
                plotten._validation.plotten_warn("test")
        assert theme_get() is original_theme

    def test_nested_options(self):
        original = theme_get()
        dark = theme_dark()
        minimal = theme_minimal()
        with options(theme=dark):
            assert theme_get() is dark
            with options(theme=minimal):
                assert theme_get() is minimal
            assert theme_get() is dark
        assert theme_get() is original
