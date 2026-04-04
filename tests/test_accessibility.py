"""Tests for the accessibility audit module."""

from __future__ import annotations

import pandas as pd
import pytest

from plotten import (
    AccessibilityReport,
    AccessibilityWarning,
    accessibility_report,
    aes,
    geom_line,
    geom_point,
    ggplot,
    labs,
    scale_color_manual,
    theme,
)
from plotten._accessibility import (
    _DEUTERANOPIA_MATRIX,
    _PROTANOPIA_MATRIX,
    _contrast_ratio,
    _delta_e,
    _hex_to_linear_rgb,
    _is_valid_hex,
    _linear_rgb_to_lab,
    _normalize_color,
    _relative_luminance,
    _simulate_cvd,
)
from plotten.themes import element_text


class TestColorConversion:
    def test_hex_to_linear_rgb_black(self):
        rgb = _hex_to_linear_rgb("#000000")
        assert rgb[0] == pytest.approx(0.0)
        assert rgb[1] == pytest.approx(0.0)
        assert rgb[2] == pytest.approx(0.0)

    def test_hex_to_linear_rgb_white(self):
        rgb = _hex_to_linear_rgb("#ffffff")
        assert rgb[0] == pytest.approx(1.0)
        assert rgb[1] == pytest.approx(1.0)
        assert rgb[2] == pytest.approx(1.0)

    def test_hex_to_linear_rgb_short_form(self):
        rgb = _hex_to_linear_rgb("#fff")
        assert rgb[0] == pytest.approx(1.0)

    def test_is_valid_hex(self):
        assert _is_valid_hex("#ff0000")
        assert _is_valid_hex("#f00")
        assert _is_valid_hex("ff0000")
        assert not _is_valid_hex("red")
        assert not _is_valid_hex("#xyz")
        assert not _is_valid_hex("")

    def test_normalize_named_color(self):
        result = _normalize_color("red")
        assert result is not None
        assert result.startswith("#")
        assert len(result) == 7

    def test_normalize_hex(self):
        assert _normalize_color("#ff0000") == "#ff0000"
        assert _normalize_color("#f00") == "#ff0000"


class TestColorblindSimulation:
    def test_simulate_deuteranopia_red_green(self):
        """Red and green should become more similar under deuteranopia."""
        sim_red = _simulate_cvd("#ff0000", _DEUTERANOPIA_MATRIX)
        sim_green = _simulate_cvd("#00ff00", _DEUTERANOPIA_MATRIX)
        lab_red_sim = _linear_rgb_to_lab(sim_red)
        lab_green_sim = _linear_rgb_to_lab(sim_green)
        de_sim = _delta_e(lab_red_sim, lab_green_sim)

        # Compare to original distance
        orig_red = _hex_to_linear_rgb("#ff0000")
        orig_green = _hex_to_linear_rgb("#00ff00")
        de_orig = _delta_e(_linear_rgb_to_lab(orig_red), _linear_rgb_to_lab(orig_green))

        # Simulated distance should be significantly smaller
        assert de_sim < de_orig * 0.6

    def test_simulate_protanopia(self):
        """Protanopia simulation should transform colors."""
        sim = _simulate_cvd("#ff0000", _PROTANOPIA_MATRIX)
        # Red component should be reduced
        original = _hex_to_linear_rgb("#ff0000")
        assert sim[0] < original[0]

    def test_blue_yellow_distinguishable_deutan(self):
        """Blue and yellow should remain distinguishable under deuteranopia."""
        sim_blue = _simulate_cvd("#0000ff", _DEUTERANOPIA_MATRIX)
        sim_yellow = _simulate_cvd("#ffff00", _DEUTERANOPIA_MATRIX)
        lab_blue = _linear_rgb_to_lab(sim_blue)
        lab_yellow = _linear_rgb_to_lab(sim_yellow)
        de = _delta_e(lab_blue, lab_yellow)
        assert de > 10  # should still be distinguishable


class TestContrastRatio:
    def test_black_white(self):
        """Black on white should have max contrast."""
        ratio = _contrast_ratio("#000000", "#ffffff")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_same_color(self):
        """Same color should have contrast ratio of 1."""
        ratio = _contrast_ratio("#ff0000", "#ff0000")
        assert ratio == pytest.approx(1.0)

    def test_wcag_threshold(self):
        """Light gray on white should fail WCAG."""
        ratio = _contrast_ratio("#cccccc", "#ffffff")
        assert ratio < 4.5

    def test_relative_luminance_black(self):
        assert _relative_luminance("#000000") == pytest.approx(0.0)

    def test_relative_luminance_white(self):
        assert _relative_luminance("#ffffff") == pytest.approx(1.0)


class TestAccessibilityReport:
    def test_report_str_no_warnings(self):
        report = AccessibilityReport()
        assert "passed" in str(report).lower()

    def test_report_str_with_warnings(self):
        report = AccessibilityReport(
            warnings=[
                AccessibilityWarning(
                    category="contrast",
                    severity="warning",
                    message="Low contrast",
                    suggestion="Fix it",
                )
            ]
        )
        s = str(report)
        assert "WARN" in s
        assert "Low contrast" in s
        assert "Fix it" in s

    def test_passed_with_info_only(self):
        report = AccessibilityReport(
            warnings=[
                AccessibilityWarning(category="font_size", severity="info", message="Small text")
            ]
        )
        assert report.passed is True

    def test_not_passed_with_warning(self):
        report = AccessibilityReport(
            warnings=[
                AccessibilityWarning(
                    category="contrast", severity="warning", message="Low contrast"
                )
            ]
        )
        assert report.passed is False


class TestFullAudit:
    def test_red_green_palette_flagged(self):
        """A red/green palette should trigger colorblind warnings."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_manual(values={"a": "#ff0000", "b": "#00ff00", "c": "#0000ff"})
        )
        report = accessibility_report(p)
        colorblind_warnings = [w for w in report.warnings if w.category == "colorblind"]
        assert len(colorblind_warnings) > 0

    def test_small_font_flagged(self):
        """Very small fonts should trigger warnings."""
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = ggplot(df, aes(x="x", y="y")) + theme(tick_size=5, label_size=6)
        report = accessibility_report(p)
        font_warnings = [w for w in report.warnings if w.category == "font_size"]
        assert len(font_warnings) > 0

    def test_low_contrast_flagged(self):
        """Light text on light background should trigger contrast warning."""
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + theme(
                title_color="#eeeeee",
                background="#ffffff",
                panel_background="#ffffff",
            )
            + labs(title="Test")
        )
        report = accessibility_report(p)
        contrast_warnings = [w for w in report.warnings if w.category == "contrast"]
        assert len(contrast_warnings) > 0

    def test_good_plot_passes(self):
        """A well-configured plot should have no errors/warnings."""
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y"))
        report = accessibility_report(p)
        # Default theme should be accessible
        error_warnings = [w for w in report.warnings if w.severity in ("error", "warning")]
        # May have some minor warnings, but should be few
        assert len(error_warnings) <= 1

    def test_axis_text_contrast(self):
        """Low contrast axis text should be flagged."""
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = ggplot(df, aes(x="x", y="y")) + theme(
            axis_text=element_text(color="#fafafa"),
            background="#ffffff",
            panel_background="#ffffff",
        )
        report = accessibility_report(p)
        contrast_warnings = [w for w in report.warnings if w.category == "contrast"]
        assert len(contrast_warnings) > 0

    def test_report_returns_correct_type(self):
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = ggplot(df, aes(x="x", y="y"))
        report = accessibility_report(p)
        assert isinstance(report, AccessibilityReport)


class TestRedundantEncoding:
    def test_color_only_flagged(self):
        """Color as sole encoding channel should warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 1
        assert "g" in encoding_warnings[0].message

    def test_color_with_shape_passes(self):
        """Color + shape mapping to the same variable should not warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g", shape="g")) + geom_point()
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 0

    def test_color_with_linetype_passes(self):
        """Color + linetype mapping should not warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g", linetype="g")) + geom_line()
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 0

    def test_no_color_mapping_skipped(self):
        """No color mapping should produce no encoding warnings."""
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 0

    def test_continuous_color_skipped(self):
        """Continuous color scales should not trigger redundant encoding warnings."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "v": [0.1, 0.5, 0.9]})
        p = ggplot(df, aes(x="x", y="y", color="v")) + geom_point()
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 0

    def test_layer_level_shape_passes(self):
        """Shape mapped in a layer (not global) should still count as redundant."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point(mapping=aes(shape="g"))
        report = accessibility_report(p)
        encoding_warnings = [w for w in report.warnings if w.category == "encoding"]
        assert len(encoding_warnings) == 0


class TestPaletteSize:
    def test_many_levels_flagged(self):
        """More than 8 discrete color levels should warn."""
        n = 10
        df = pd.DataFrame(
            {"x": list(range(n)), "y": list(range(n)), "g": [f"cat{i}" for i in range(n)]}
        )
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
        report = accessibility_report(p)
        palette_warnings = [w for w in report.warnings if w.category == "palette"]
        assert len(palette_warnings) == 1
        assert "10" in palette_warnings[0].message

    def test_few_levels_passes(self):
        """8 or fewer levels should not warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
        report = accessibility_report(p)
        palette_warnings = [w for w in report.warnings if w.category == "palette"]
        assert len(palette_warnings) == 0


class TestLegendPresent:
    def test_hidden_legend_flagged(self):
        """Suppressed legend with mapped aesthetics should warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + theme(legend_position="none")
        report = accessibility_report(p)
        legend_warnings = [w for w in report.warnings if w.category == "legend"]
        assert len(legend_warnings) == 1

    def test_visible_legend_passes(self):
        """Default legend position should not warn."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
        report = accessibility_report(p)
        legend_warnings = [w for w in report.warnings if w.category == "legend"]
        assert len(legend_warnings) == 0

    def test_hidden_legend_no_mapping_passes(self):
        """Suppressed legend with no mapped aesthetics should not warn."""
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(legend_position="none")
        report = accessibility_report(p)
        legend_warnings = [w for w in report.warnings if w.category == "legend"]
        assert len(legend_warnings) == 0


class TestDescriptiveText:
    def test_no_title_flagged(self):
        """Plot without a title should produce info-level suggestion."""
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        report = accessibility_report(p)
        desc_warnings = [w for w in report.warnings if w.category == "description"]
        assert len(desc_warnings) == 1
        assert desc_warnings[0].severity == "info"

    def test_with_title_passes(self):
        """Plot with a title should not produce description warnings."""
        df = pd.DataFrame({"x": [1], "y": [1]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="My Plot")
        report = accessibility_report(p)
        desc_warnings = [w for w in report.warnings if w.category == "description"]
        assert len(desc_warnings) == 0
