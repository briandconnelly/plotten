from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

from typing import TYPE_CHECKING

from plotten import (
    Aes,
    Theme,
    aes,
    element_blank,
    element_line,
    element_rect,
    element_text,
    geom_point,
    ggplot,
    ggsave,
    labs,
    theme,
    theme_bw,
    theme_classic,
    theme_dark,
    theme_get,
    theme_gray,
    theme_grey,
    theme_set,
    theme_update,
    theme_void,
)
from plotten._render._mpl import render
from plotten.themes import (
    theme_538,
    theme_default,
    theme_economist,
    theme_minimal,
    theme_seaborn,
    theme_tufte,
)
from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, ElementText

if TYPE_CHECKING:
    from pathlib import Path

# --- from test_themes.py ---


def test_theme_defaults():
    t = theme_default()
    assert t.title_size == 14
    assert t.panel_background == "#ebebeb"


def test_theme_minimal():
    t = theme_minimal()
    assert t.panel_background == "none"
    assert t.axis_line_width == 0.0


def test_theme_dark():
    t = theme_dark()
    assert t.background == "#2d2d2d"
    assert t.panel_background == "#3d3d3d"


def test_theme_add():
    base = theme_default()
    overlay = Theme(title_size=20)
    combined = base + overlay
    assert combined.title_size == 20
    # Non-overridden fields stay from base
    assert combined.panel_background == "#ebebeb"


def test_theme_frozen():
    t = Theme()
    try:
        t.title_size = 99  # type: ignore[misc]
        pytest.fail("Should have raised")
    except AttributeError:
        pass


# --- from test_v06_themes.py ---

"""Tests for v0.6.0 theme granularity and new predefined themes."""

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


# --- from test_v08_themes.py ---

"""Tests for v0.8.0 theme element system."""


class TestElementClasses:
    def test_element_text_defaults(self):
        et = ElementText()
        assert et.size is None
        assert et.color is None
        assert et.family is None

    def test_element_text_with_values(self):
        et = ElementText(size=14, color="red", weight="bold")
        assert et.size == 14
        assert et.color == "red"
        assert et.weight == "bold"

    def test_element_line_defaults(self):
        el = ElementLine()
        assert el.color is None
        assert el.size is None

    def test_element_line_with_values(self):
        el = ElementLine(color="blue", size=2.0, linetype="--")
        assert el.color == "blue"
        assert el.size == 2.0
        assert el.linetype == "--"

    def test_element_rect_defaults(self):
        er = ElementRect()
        assert er.fill is None
        assert er.color is None

    def test_element_rect_with_values(self):
        er = ElementRect(fill="gray", color="black", size=1.0)
        assert er.fill == "gray"

    def test_element_blank(self):
        eb = ElementBlank()
        assert isinstance(eb, ElementBlank)

    def test_elements_are_frozen(self):

        et = ElementText(size=12)
        with pytest.raises(AttributeError):
            et.size = 14  # type: ignore


class TestElementFactories:
    def test_element_text_factory(self):
        et = element_text(size=12, color="blue")
        assert isinstance(et, ElementText)
        assert et.size == 12

    def test_element_line_factory(self):
        el = element_line(color="red")
        assert isinstance(el, ElementLine)

    def test_element_rect_factory(self):
        er = element_rect(fill="gray")
        assert isinstance(er, ElementRect)

    def test_element_blank_factory(self):
        eb = element_blank()
        assert isinstance(eb, ElementBlank)


class TestThemeWithElements:
    def test_theme_default_elements_none(self):
        t = Theme()
        assert t.panel_grid_major is None
        assert t.panel_grid_minor is None
        assert t.plot_title is None

    def test_theme_with_element_blank_grid(self):
        t = Theme(panel_grid_minor=element_blank())
        assert isinstance(t.panel_grid_minor, ElementBlank)

    def test_theme_with_element_line_grid(self):
        t = Theme(panel_grid_major=element_line(color="red", size=2.0))
        assert isinstance(t.panel_grid_major, ElementLine)
        assert t.panel_grid_major.color == "red"

    def test_theme_with_element_text_title(self):
        t = Theme(plot_title=element_text(size=20, color="navy"))
        assert isinstance(t.plot_title, ElementText)
        assert t.plot_title.size == 20

    def test_theme_addition_preserves_elements(self):
        t1 = Theme(panel_grid_minor=element_blank())
        t2 = Theme(title_size=18)
        combined = t1 + t2
        assert isinstance(combined.panel_grid_minor, ElementBlank)
        assert combined.title_size == 18

    def test_theme_addition_element_override(self):
        t1 = Theme(panel_grid_major=element_line(color="red"))
        t2 = Theme(panel_grid_major=element_blank())
        combined = t1 + t2
        assert isinstance(combined.panel_grid_major, ElementBlank)


class TestElementRendering:
    def test_render_blank_minor_grid(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(grid_minor_x=True, grid_minor_y=True, panel_grid_minor=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_blank_major_grid(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(panel_grid_major=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_custom_grid_color(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(panel_grid_major=element_line(color="#cccccc", size=1.5))
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_element_text_title(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_title=element_text(size=24, color="darkblue"))
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Big Title") + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_blank_title(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_title=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Hidden") + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_blank_caption(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_caption=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(caption="Hidden") + theme
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_render_blank_subtitle(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_subtitle=element_blank())
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(title="Title", subtitle="Hidden")
            + theme
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)


# --- from test_v10_theme_function.py ---

"""Tests for theme() convenience function (1A)."""


def test_theme_basic():
    t = theme(title_size=20)
    assert t.title_size == 20
    assert isinstance(t, Theme)


def test_theme_multiple_kwargs():
    t = theme(title_size=20, axis_text_x_rotation=45, background="#000000")
    assert t.title_size == 20
    assert t.axis_text_x_rotation == 45
    assert t.background == "#000000"


def test_theme_invalid_kwarg():
    with pytest.raises(TypeError, match="Unknown theme properties"):
        theme(nonexistent_field=42)


def test_theme_composition():
    combined = theme_minimal() + theme(title_size=20)
    assert combined.title_size == 20
    # theme_minimal sets panel_background to "none"
    assert combined.panel_background == "none"


def test_theme_empty():
    t = theme()
    assert t == Theme()


# --- from test_v11_theme.py ---

"""Tests for v0.11.0 theme additions."""


@pytest.fixture(autouse=True)
def _reset_global_theme():
    """Reset global theme before and after each test."""
    theme_set(Theme())
    yield
    theme_set(Theme())


class TestThemeSetGet:
    def test_default_is_base_theme(self):
        assert theme_get() == Theme()

    def test_set_returns_old(self):
        old = theme_set(theme_dark())
        assert old == Theme()

    def test_get_after_set(self):
        theme_set(theme_dark())
        current = theme_get()
        assert current.background == theme_dark().background

    def test_set_affects_render(self):
        """Global theme should affect rendered plot."""
        theme_set(theme_dark())
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        fig = render(p)
        # dark theme has dark background
        assert fig.get_facecolor() != (1.0, 1.0, 1.0, 1.0)

    def test_plot_theme_overrides_global(self):
        """Plot-level theme should override global theme."""
        theme_set(theme_dark())
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + theme(background="#ff0000")
        fig = render(p)
        # The plot-level red background should win
        fc = fig.get_facecolor()
        assert fc[0] == 1.0  # red channel


class TestThemeUpdate:
    def test_update_changes_global(self):
        theme_update(title_size=24)
        assert theme_get().title_size == 24

    def test_update_returns_theme(self):
        result = theme_update(label_size=16)
        assert isinstance(result, Theme)
        assert result.label_size == 16

    def test_update_preserves_previous(self):
        theme_update(title_size=24)
        theme_update(label_size=16)
        current = theme_get()
        assert current.title_size == 24
        assert current.label_size == 16


class TestThemeGrey:
    def test_theme_grey_exists(self):
        t = theme_grey()
        assert isinstance(t, Theme)

    def test_grey_has_grey_background(self):
        t = theme_grey()
        assert t.panel_background == "#ebebeb"

    def test_grey_white_gridlines(self):
        t = theme_grey()
        assert t.grid_color == "#ffffff"

    def test_grey_no_axis_lines(self):
        t = theme_grey()
        assert t.axis_line_width == 0

    def test_gray_alias(self):
        assert theme_gray is theme_grey

    def test_grey_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + theme_grey()
        fig = render(p)
        assert fig is not None


# --- from test_v110_themes.py ---

"""Tests for v1.1.0 Phase 1 theme gallery: theme_538, theme_economist, theme_tufte, theme_seaborn."""


def _make_plot():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    return ggplot(df, Aes(x="x", y="y")) + geom_point()


# --- theme_538 ---


class TestTheme538:
    def test_returns_theme(self):
        t = theme_538()
        assert isinstance(t, Theme)

    def test_background(self):
        t = theme_538()
        assert t.background == "#f0f0f0"
        assert t.panel_background == "#f0f0f0"

    def test_no_axis_lines(self):
        t = theme_538()
        assert t.axis_line_x is False
        assert t.axis_line_y is False

    def test_white_grid_major_only(self):
        t = theme_538()
        assert t.grid_color == "#ffffff"
        assert t.grid_minor_x is False
        assert t.grid_minor_y is False

    def test_bold_large_title(self):
        t = theme_538()
        assert t.title_size >= 16

    def test_sans_serif(self):
        t = theme_538()
        assert t.font_family == "sans-serif"

    def test_compose(self):
        combined = theme_538() + Theme(title_size=24)
        assert combined.title_size == 24
        assert combined.background == "#f0f0f0"

    def test_render(self, tmp_path: Path):
        p = _make_plot() + theme_538()
        out = tmp_path / "plot_538.png"
        ggsave(p, out)
        assert out.exists()
        assert out.stat().st_size > 0


# --- theme_economist ---


class TestThemeEconomist:
    def test_returns_theme(self):
        t = theme_economist()
        assert isinstance(t, Theme)

    def test_background(self):
        t = theme_economist()
        assert t.background == "#d5e4eb"
        assert t.panel_background == "#d5e4eb"

    def test_y_grid_only(self):
        t = theme_economist()
        assert t.grid_major_x is False
        assert t.grid_major_y is True

    def test_no_minor_grid(self):
        t = theme_economist()
        assert t.grid_minor_x is False
        assert t.grid_minor_y is False

    def test_larger_title(self):
        t = theme_economist()
        assert t.title_size > Theme().title_size

    def test_compose(self):
        combined = theme_economist() + Theme(grid_color="#000000")
        assert combined.grid_color == "#000000"
        assert combined.background == "#d5e4eb"

    def test_render(self, tmp_path: Path):
        p = _make_plot() + theme_economist()
        out = tmp_path / "plot_economist.png"
        ggsave(p, out)
        assert out.exists()
        assert out.stat().st_size > 0


# --- theme_tufte ---


class TestThemeTufte:
    def test_returns_theme(self):
        t = theme_tufte()
        assert isinstance(t, Theme)

    def test_white_background_no_panel(self):
        t = theme_tufte()
        assert t.background == "#ffffff"
        assert t.panel_background == "none"

    def test_no_grid(self):
        t = theme_tufte()
        assert t.grid_major_x is False
        assert t.grid_major_y is False
        assert t.grid_minor_x is False
        assert t.grid_minor_y is False

    def test_thin_axis_lines(self):
        t = theme_tufte()
        assert t.axis_line_width <= 0.5

    def test_serif_font(self):
        t = theme_tufte()
        assert t.font_family == "serif"

    def test_compose(self):
        combined = theme_tufte() + Theme(title_size=20)
        assert combined.title_size == 20
        assert combined.panel_background == "none"

    def test_render(self, tmp_path: Path):
        p = _make_plot() + theme_tufte()
        out = tmp_path / "plot_tufte.png"
        ggsave(p, out)
        assert out.exists()
        assert out.stat().st_size > 0


# --- theme_seaborn ---


class TestThemeSeaborn:
    def test_returns_theme(self):
        t = theme_seaborn()
        assert isinstance(t, Theme)

    def test_white_background(self):
        t = theme_seaborn()
        assert t.background == "#ffffff"
        assert t.panel_background == "#ffffff"

    def test_light_grey_grid(self):
        t = theme_seaborn()
        assert t.grid_color == "#eaeaf2"

    def test_no_axis_lines(self):
        t = theme_seaborn()
        assert t.axis_line_x is False
        assert t.axis_line_y is False

    def test_panel_border(self):
        t = theme_seaborn()
        assert t.panel_border_color == "#cccccc"

    def test_compose(self):
        combined = theme_seaborn() + Theme(grid_color="#aaaaaa")
        assert combined.grid_color == "#aaaaaa"
        assert combined.panel_border_color == "#cccccc"

    def test_render(self, tmp_path: Path):
        p = _make_plot() + theme_seaborn()
        out = tmp_path / "plot_seaborn.png"
        ggsave(p, out)
        assert out.exists()
        assert out.stat().st_size > 0


# --- Cross-theme tests ---


@pytest.mark.parametrize("theme_fn", [theme_538, theme_economist, theme_tufte, theme_seaborn])
def test_all_new_themes_return_theme(theme_fn):
    assert isinstance(theme_fn(), Theme)


@pytest.mark.parametrize("theme_fn", [theme_538, theme_economist, theme_tufte, theme_seaborn])
def test_all_new_themes_composable(theme_fn):
    combined = theme_fn() + Theme(title_size=99)
    assert combined.title_size == 99


def test_top_level_imports():
    """Verify all four themes are importable from the top-level package."""
    import plotten

    assert callable(plotten.theme_538)
    assert callable(plotten.theme_economist)
    assert callable(plotten.theme_tufte)
    assert callable(plotten.theme_seaborn)
