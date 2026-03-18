"""Tests for v0.6.0 theme granularity and new predefined themes."""

from __future__ import annotations

import matplotlib
import polars as pl

from plotten import (
    Aes,
    Theme,
    geom_point,
    ggplot,
    labs,
    theme_bw,
    theme_classic,
    theme_void,
)

matplotlib.use("Agg")


# ── New Theme fields ────────────────────────────────────────────────


class TestThemeNewFields:
    def test_default_values(self):
        t = Theme()
        assert t.axis_title_x_size is None
        assert t.axis_title_y_size is None
        assert t.axis_text_x_size is None
        assert t.axis_text_y_size is None
        assert t.axis_text_x_rotation == 0
        assert t.axis_text_y_rotation == 0
        assert t.panel_border_color is None
        assert t.panel_border_width == 1.0
        assert t.strip_background == "#d9d9d9"
        assert t.strip_text_size is None
        assert t.strip_text_color == "#000000"
        assert t.title_color == "#000000"
        assert t.subtitle_size is None
        assert t.subtitle_color == "#555555"
        assert t.legend_background is None
        assert t.legend_title_size is None
        assert t.legend_text_size is None
        assert t.grid_major_x is True
        assert t.grid_major_y is True
        assert t.grid_minor_x is False
        assert t.grid_minor_y is False
        assert t.axis_line_x is True
        assert t.axis_line_y is True

    def test_custom_values(self):
        t = Theme(
            axis_title_x_size=16,
            axis_text_x_rotation=45,
            panel_border_color="#333333",
            grid_minor_x=True,
            axis_line_y=False,
        )
        assert t.axis_title_x_size == 16
        assert t.axis_text_x_rotation == 45
        assert t.panel_border_color == "#333333"
        assert t.grid_minor_x is True
        assert t.axis_line_y is False

    def test_theme_add_preserves_new_fields(self):
        base = Theme(axis_title_x_size=16, panel_border_color="#000000")
        overlay = Theme(axis_text_x_rotation=45)
        combined = base + overlay
        assert combined.axis_title_x_size == 16
        assert combined.axis_text_x_rotation == 45

    def test_theme_add_overlay_overrides(self):
        base = Theme(panel_border_color="#000000")
        overlay = Theme(panel_border_color="#ff0000")
        combined = base + overlay
        assert combined.panel_border_color == "#ff0000"


# ── Per-axis rendering ──────────────────────────────────────────────


class TestPerAxisRendering:
    def test_rotated_x_ticks(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + Theme(axis_text_x_rotation=45)
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_per_axis_title_sizes(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + Theme(axis_title_x_size=18, axis_title_y_size=8)
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_panel_border(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + Theme(panel_border_color="#000000", panel_border_width=2.0)
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_grid_per_axis(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + Theme(grid_major_x=False, grid_major_y=True, grid_minor_y=True)
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_axis_line_visibility(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + Theme(axis_line_x=False, axis_line_y=False)
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_title_subtitle_colors(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_point()
            + labs(title="Title", subtitle="Subtitle")
            + Theme(title_color="#ff0000", subtitle_color="#00ff00", subtitle_size=10)
        )
        fig = p._repr_png_()
        assert len(fig) > 0


# ── Predefined themes ──────────────────────────────────────────────


class TestThemeBw:
    def test_white_panel(self):
        t = theme_bw()
        assert t.panel_background == "#ffffff"

    def test_black_border(self):
        t = theme_bw()
        assert t.panel_border_color == "#000000"

    def test_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + theme_bw()
        fig = p._repr_png_()
        assert len(fig) > 0


class TestThemeClassic:
    def test_no_grid(self):
        t = theme_classic()
        assert t.grid_major_x is False
        assert t.grid_major_y is False

    def test_white_panel(self):
        t = theme_classic()
        assert t.panel_background == "#ffffff"

    def test_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + theme_classic()
        fig = p._repr_png_()
        assert len(fig) > 0


class TestThemeVoid:
    def test_transparent_backgrounds(self):
        t = theme_void()
        assert t.background == "none"
        assert t.panel_background == "none"

    def test_no_axes(self):
        t = theme_void()
        assert t.axis_line_x is False
        assert t.axis_line_y is False

    def test_no_grid(self):
        t = theme_void()
        assert t.grid_major_x is False
        assert t.grid_major_y is False

    def test_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + theme_void()
        fig = p._repr_png_()
        assert len(fig) > 0


# ── Import smoke test ───────────────────────────────────────────────


class TestImports:
    def test_all_new_exports(self):
        pass
