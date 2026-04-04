"""Accessibility audit for plotten plots.

Checks data-visualization-specific accessibility concerns: colorblind safety,
redundant encoding, palette size, text contrast, font sizes, legend presence,
and descriptive text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class AccessibilityWarning:
    """A single accessibility issue found in a plot."""

    category: str  # "colorblind", "contrast", "font_size"
    severity: str  # "error", "warning", "info"
    message: str
    suggestion: str | None = None


@dataclass(slots=True)
class AccessibilityReport:
    """Result of an accessibility audit."""

    warnings: list[AccessibilityWarning] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True if no errors or warnings (info is OK)."""
        return all(w.severity == "info" for w in self.warnings)

    def __str__(self) -> str:
        if not self.warnings:
            return "Accessibility check passed — no issues found."
        lines = []
        for w in self.warnings:
            icon = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}[w.severity]
            lines.append(f"  {icon} [{w.category}] {w.message}")
            if w.suggestion:
                lines.append(f"         Suggestion: {w.suggestion}")
        status = "PASSED" if self.passed else "ISSUES FOUND"
        header = f"Accessibility Report — {status} ({len(self.warnings)} item(s))"
        return header + "\n" + "\n".join(lines)


# --- Color-blindness simulation ---

# Brettel et al. 1997 / Vienot et al. 1999 simulation matrices (linear RGB)
_DEUTERANOPIA_MATRIX = np.array(
    [
        [0.625, 0.375, 0.0],
        [0.700, 0.300, 0.0],
        [0.000, 0.300, 0.700],
    ]
)

_PROTANOPIA_MATRIX = np.array(
    [
        [0.567, 0.433, 0.0],
        [0.558, 0.442, 0.0],
        [0.000, 0.242, 0.758],
    ]
)

_TRITANOPIA_MATRIX = np.array(
    [
        [0.950, 0.050, 0.0],
        [0.000, 0.433, 0.567],
        [0.000, 0.475, 0.525],
    ]
)

_CVD_SIMULATIONS = {
    "deuteranopia": _DEUTERANOPIA_MATRIX,
    "protanopia": _PROTANOPIA_MATRIX,
    "tritanopia": _TRITANOPIA_MATRIX,
}


def _hex_to_linear_rgb(hex_color: str) -> np.ndarray:
    """Convert hex color to linear RGB (undo sRGB gamma)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    r, g, b = int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0
    # sRGB to linear
    return np.array([_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)])


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055


def _simulate_cvd(hex_color: str, matrix: np.ndarray) -> np.ndarray:
    """Simulate color vision deficiency, return linear RGB."""
    linear = _hex_to_linear_rgb(hex_color)
    simulated = matrix @ linear
    return np.clip(simulated, 0, 1)


def _linear_rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB to CIELAB for perceptual distance."""
    # Linear RGB -> XYZ (sRGB D65)
    m = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
    )
    xyz = m @ rgb
    # Normalize to D65 white point
    xyz /= np.array([0.95047, 1.0, 1.08883])

    def f(t: np.ndarray) -> np.ndarray:
        delta = 6.0 / 29.0
        return np.where(t > delta**3, np.cbrt(t), t / (3 * delta**2) + 4.0 / 29.0)

    fxyz = f(xyz)
    L = 116 * fxyz[1] - 16
    a = 500 * (fxyz[0] - fxyz[1])
    b = 200 * (fxyz[1] - fxyz[2])
    return np.array([L, a, b])


def _delta_e(lab1: np.ndarray, lab2: np.ndarray) -> float:
    """CIE76 color difference."""
    return float(np.sqrt(np.sum((lab1 - lab2) ** 2)))


def _is_valid_hex(color: str) -> bool:
    """Check if a string is a valid hex color."""
    if not isinstance(color, str):
        return False
    c = color.lstrip("#")
    if len(c) not in (3, 6):
        return False
    try:
        int(c, 16)
    except ValueError:
        return False
    return True


def _named_to_hex(color: str) -> str | None:
    """Convert a named matplotlib color to hex."""
    try:
        import matplotlib.colors as mcolors

        rgba = mcolors.to_rgba(color)
        if rgba[3] == 0.0:
            return None  # fully transparent (e.g. "none") is not a real color
        return f"#{int(rgba[0] * 255):02x}{int(rgba[1] * 255):02x}{int(rgba[2] * 255):02x}"
    except (ValueError, KeyError):
        return None


def _normalize_color(color: str) -> str | None:
    """Normalize a color string to hex, or None if not parseable."""
    if _is_valid_hex(color):
        h = color.lstrip("#")
        if len(h) == 3:
            h = h[0] * 2 + h[1] * 2 + h[2] * 2
        return f"#{h}"
    return _named_to_hex(color)


# --- Contrast ratio ---


def _relative_luminance(hex_color: str) -> float:
    """WCAG 2.1 relative luminance."""
    rgb = _hex_to_linear_rgb(hex_color)
    return float(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])


def _contrast_ratio(color1: str, color2: str) -> float:
    """WCAG 2.1 contrast ratio between two hex colors."""
    l1 = _relative_luminance(color1)
    l2 = _relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# --- Color extraction ---


def _extract_palette_colors(plot: Any) -> list[str]:
    """Extract palette colors from a plot's trained scales."""
    from plotten._render._resolve import resolve

    resolved = resolve(plot)
    colors: list[str] = []
    for scale in resolved.scales.values():
        entries = scale.legend_entries()
        if entries:
            for e in entries:
                if e.color:
                    c = _normalize_color(e.color)
                    if c:
                        colors.append(c)
                if e.fill:
                    c = _normalize_color(e.fill)
                    if c:
                        colors.append(c)
    return list(dict.fromkeys(colors))  # deduplicate preserving order


def _extract_theme_colors(plot: Any) -> dict[str, str]:
    """Extract key theme colors."""
    from plotten.themes._theme import Theme

    theme: Theme = plot.theme if plot.theme is not None else Theme()
    result: dict[str, str] = {}

    bg = _normalize_color(theme.background)
    if bg:
        result["background"] = bg

    from plotten.themes._elements import resolve_background

    panel_fill, _, _ = resolve_background(theme.panel_background)
    panel_bg = _normalize_color(panel_fill) if panel_fill else None
    if panel_bg:
        result["panel_background"] = panel_bg

    title_color = _normalize_color(theme.title_color)
    if title_color:
        result["title_color"] = title_color

    return result


# --- Main audit ---


def accessibility_report(plot: Any) -> AccessibilityReport:
    """Audit a plot for data-visualization accessibility issues.

    Checks:
    - Colorblind safety of the palette (deuteranopia, protanopia, tritanopia)
    - Redundant encoding (whether color is the only channel distinguishing groups)
    - Palette size (whether too many discrete colors are used)
    - Text contrast ratios against backgrounds
    - Minimum font sizes
    - Legend presence (whether a suppressed legend hides mapped aesthetics)
    - Descriptive text (whether the plot has a title for alt-text)
    """
    report = AccessibilityReport()

    _check_colorblind_safety(plot, report)
    _check_redundant_encoding(plot, report)
    _check_palette_size(plot, report)
    _check_contrast(plot, report)
    _check_font_sizes(plot, report)
    _check_legend_present(plot, report)
    _check_descriptive_text(plot, report)

    return report


def _check_colorblind_safety(plot: Any, report: AccessibilityReport) -> None:
    """Check if palette colors are distinguishable under color vision deficiencies."""
    try:
        colors = _extract_palette_colors(plot)
    except (ValueError, TypeError, KeyError, AttributeError):
        return

    if len(colors) < 2:
        return

    threshold = 20.0  # deltaE below this = hard to distinguish

    for cvd_name, matrix in _CVD_SIMULATIONS.items():
        simulated = [_simulate_cvd(c, matrix) for c in colors]
        labs = [_linear_rgb_to_lab(s) for s in simulated]

        for i in range(len(labs)):
            for j in range(i + 1, len(labs)):
                de = _delta_e(labs[i], labs[j])
                if de < threshold:
                    report.warnings.append(
                        AccessibilityWarning(
                            category="colorblind",
                            severity="warning",
                            message=(
                                f"Colors {colors[i]} and {colors[j]} may be "
                                f"indistinguishable under {cvd_name} "
                                f"(deltaE={de:.1f})"
                            ),
                            suggestion=(
                                "Use a colorblind-safe palette like viridis, "
                                "cividis, or ColorBrewer qualitative palettes."
                            ),
                        )
                    )


def _check_contrast(plot: Any, report: AccessibilityReport) -> None:
    """Check text-to-background contrast ratios."""
    from plotten.themes._theme import Theme

    theme: Theme = plot.theme if plot.theme is not None else Theme()
    theme_colors = _extract_theme_colors(plot)

    bg = theme_colors.get("panel_background") or theme_colors.get("background")
    if bg is None:
        return

    # Check title color
    title_color = theme_colors.get("title_color")
    if title_color:
        ratio = _contrast_ratio(title_color, bg)
        if ratio < 3.0:
            report.warnings.append(
                AccessibilityWarning(
                    category="contrast",
                    severity="error",
                    message=f"Title color {title_color} has very low contrast ({ratio:.1f}:1) against background {bg}",
                    suggestion="Increase contrast to at least 4.5:1 for normal text.",
                )
            )
        elif ratio < 4.5:
            report.warnings.append(
                AccessibilityWarning(
                    category="contrast",
                    severity="warning",
                    message=f"Title color {title_color} has low contrast ({ratio:.1f}:1) against background {bg}",
                    suggestion="WCAG AA requires at least 4.5:1 for normal text.",
                )
            )

    # Check axis text / label colors from ElementText if set
    from plotten.themes._elements import ElementText

    for attr_name, label in [
        ("axis_text", "Axis text"),
        ("axis_title", "Axis title"),
        ("strip_text", "Strip text"),
    ]:
        elem = getattr(theme, attr_name, None)
        if isinstance(elem, ElementText) and elem.color is not None:
            c = _normalize_color(elem.color)
            if c:
                ratio = _contrast_ratio(c, bg)
                if ratio < 3.0:
                    report.warnings.append(
                        AccessibilityWarning(
                            category="contrast",
                            severity="error",
                            message=f"{label} color {c} has very low contrast ({ratio:.1f}:1) against background {bg}",
                            suggestion="Increase contrast to at least 4.5:1.",
                        )
                    )


def _check_font_sizes(plot: Any, report: AccessibilityReport) -> None:
    """Check for excessively small font sizes."""
    from plotten.themes._theme import Theme

    theme: Theme = plot.theme if plot.theme is not None else Theme()

    size_checks = [
        ("tick_size", "Tick label", theme.tick_size),
        ("label_size", "Axis label", theme.label_size),
        ("title_size", "Title", theme.title_size),
    ]

    if theme.strip_text_size is not None:
        size_checks.append(("strip_text_size", "Strip text", theme.strip_text_size))

    for _field, label, size in size_checks:
        if size < 6:
            report.warnings.append(
                AccessibilityWarning(
                    category="font_size",
                    severity="error",
                    message=f"{label} font size ({size}pt) is extremely small.",
                    suggestion="Use at least 8pt for readability.",
                )
            )
        elif size < 8:
            report.warnings.append(
                AccessibilityWarning(
                    category="font_size",
                    severity="warning",
                    message=f"{label} font size ({size}pt) may be too small.",
                    suggestion="Use at least 8pt for readability.",
                )
            )


def _check_redundant_encoding(plot: Any, report: AccessibilityReport) -> None:
    """Check if color/fill is the only channel distinguishing groups."""
    from plotten.scales._base import MappedDiscreteScale

    # Collect all mappings (global + per-layer)
    all_mappings = [plot.mapping]
    for layer in plot.layers:
        if layer.mapping is not None:
            all_mappings.append(layer.mapping)

    # Find columns mapped to color/fill
    color_columns: set[str] = set()
    for m in all_mappings:
        for aes_name in ("color", "fill"):
            col = getattr(m, aes_name, None)
            if isinstance(col, str):
                color_columns.add(col)

    if not color_columns:
        return

    # Skip if the color/fill scale is continuous (shape can't encode continuous)
    try:
        from plotten._render._resolve import resolve

        resolved = resolve(plot)
    except (ValueError, TypeError, KeyError, AttributeError):
        return

    for aes_name in ("color", "fill"):
        scale = resolved.scales.get(aes_name)
        if scale is not None and not isinstance(scale, MappedDiscreteScale):
            return

    # Check if any redundant channel maps the same column
    redundant_channels = ("shape", "linetype", "hatch")
    redundant_columns: set[str] = set()
    for m in all_mappings:
        for ch in redundant_channels:
            col = getattr(m, ch, None)
            if isinstance(col, str):
                redundant_columns.add(col)

    unreinforced = color_columns - redundant_columns
    if unreinforced:
        cols = ", ".join(sorted(unreinforced))
        report.warnings.append(
            AccessibilityWarning(
                category="encoding",
                severity="warning",
                message=(
                    f"Color is the only channel encoding {cols}. "
                    f"Groups will be indistinguishable without color perception."
                ),
                suggestion=(
                    "Map shape or linetype to the same variable so groups "
                    "remain distinguishable without color."
                ),
            )
        )


def _check_palette_size(plot: Any, report: AccessibilityReport) -> None:
    """Check if a discrete palette has too many levels to distinguish."""
    from plotten.scales._base import MappedDiscreteScale

    try:
        from plotten._render._resolve import resolve

        resolved = resolve(plot)
    except (ValueError, TypeError, KeyError, AttributeError):
        return

    max_levels = 8
    for aes_name in ("color", "fill"):
        scale = resolved.scales.get(aes_name)
        if isinstance(scale, MappedDiscreteScale) and len(scale._levels) > max_levels:
            report.warnings.append(
                AccessibilityWarning(
                    category="palette",
                    severity="warning",
                    message=(
                        f"Discrete {aes_name} scale has {len(scale._levels)} levels. "
                        f"More than {max_levels} colors are difficult to distinguish."
                    ),
                    suggestion=(
                        "Consider grouping categories or using facets "
                        "to reduce the number of colors."
                    ),
                )
            )


def _check_legend_present(plot: Any, report: AccessibilityReport) -> None:
    """Check if a suppressed legend hides mapped aesthetics."""
    from plotten._enums import LegendPosition
    from plotten.themes._theme import Theme

    theme: Theme = plot.theme if plot.theme is not None else Theme()
    pos = theme.legend_position
    if not (isinstance(pos, str) and pos == LegendPosition.NONE):
        return

    try:
        from plotten._render._resolve import resolve

        resolved = resolve(plot)
    except (ValueError, TypeError, KeyError, AttributeError):
        return

    has_entries = any(
        scale.legend_entries()
        for scale in resolved.scales.values()
        if scale.legend_entries() is not None
    )
    if has_entries:
        report.warnings.append(
            AccessibilityWarning(
                category="legend",
                severity="warning",
                message=(
                    "Legend is hidden but mapped aesthetics are present. "
                    "Readers cannot decode the visual encoding without a legend."
                ),
                suggestion=(
                    "Remove legend_position='none' or add direct labels "
                    "to the plot (e.g. via annotate or geom_text)."
                ),
            )
        )


def _check_descriptive_text(plot: Any, report: AccessibilityReport) -> None:
    """Check if the plot has a title for use as alt-text."""
    title = getattr(plot.labs, "title", None) if plot.labs is not None else None
    if title is None:
        report.warnings.append(
            AccessibilityWarning(
                category="description",
                severity="info",
                message="Plot has no title.",
                suggestion=(
                    "Add a title with labs(title=...) to describe the plot's "
                    "main finding. Titles serve as alt-text when images are "
                    "embedded in documents or web pages."
                ),
            )
        )
