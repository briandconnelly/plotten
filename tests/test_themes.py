from __future__ import annotations

import matplotlib
import pandas as pd
import polars as pl
import pytest

matplotlib.use("Agg")

from typing import TYPE_CHECKING

from plotten import (
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
from plotten._validation import ConfigError
from plotten.themes import (
    theme_538,
    theme_default,
    theme_economist,
    theme_light,
    theme_linedraw,
    theme_minimal,
    theme_seaborn,
    theme_test,
    theme_tufte,
)
from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, ElementText

if TYPE_CHECKING:
    from pathlib import Path


def test_theme_defaults():
    t = theme_default()
    assert t.title_size == 16
    assert t.panel_background == "#ffffff"


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
    assert combined.panel_background == "#ffffff"


def test_theme_frozen():
    t = Theme()
    try:
        t.title_size = 99  # type: ignore[misc]
        pytest.fail("Should have raised")
    except AttributeError:
        pass


# ── Tests for v0.6.0 theme granularity and new predefined themes ───

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
        assert t.strip_background == "none"
        assert t.strip_text_size is None
        assert t.strip_text_color == "#000000"
        assert t.title_color == "#1a1a1a"
        assert t.subtitle_size == 12
        assert t.subtitle_color == "#666666"
        assert t.legend_background is None
        assert t.legend_title_size is None
        assert t.legend_text_size is None
        assert t.grid_major_x is True
        assert t.grid_major_y is True
        assert t.grid_minor_x is False
        assert t.grid_minor_y is False
        assert t.axis_line_x is False
        assert t.axis_line_y is False

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
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + Theme(axis_text_x_rotation=45)
        fig = render(p)
        ax = fig.axes[0]
        for label in ax.get_xticklabels():
            if label.get_text():
                assert label.get_rotation() == pytest.approx(45)

    def test_per_axis_title_sizes(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + Theme(axis_title_x_size=18, axis_title_y_size=8)
        )
        fig = render(p)
        ax = fig.axes[0]
        assert ax.xaxis.label.get_fontsize() == pytest.approx(18)
        assert ax.yaxis.label.get_fontsize() == pytest.approx(8)

    def test_panel_border(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + Theme(panel_border_color="#000000", panel_border_width=2.0)
        )
        fig = render(p)
        ax = fig.axes[0]
        for spine in ax.spines.values():
            assert spine.get_linewidth() == pytest.approx(2.0)

    def test_grid_per_axis(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + Theme(grid_major_x=False, grid_major_y=True, grid_minor_y=True)
        )
        fig = render(p)
        ax = fig.axes[0]
        # y-axis major gridlines should be visible
        y_gridlines = ax.yaxis.get_gridlines()
        assert any(gl.get_visible() for gl in y_gridlines)

    def test_axis_line_visibility(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + Theme(axis_line_x=False, axis_line_y=False)
        )
        fig = render(p)
        ax = fig.axes[0]
        assert not ax.spines["bottom"].get_visible()
        assert not ax.spines["left"].get_visible()

    def test_title_subtitle_colors(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(title="Title", subtitle="Subtitle")
            + Theme(title_color="#ff0000", subtitle_color="#00ff00", subtitle_size=10)
        )
        fig = render(p)
        # Title and subtitle should appear somewhere in the figure's text artists
        all_texts = [t.get_text() for sf in fig.subfigs for t in sf.texts]
        assert "Title" in all_texts


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
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_bw()
        fig = render(p)
        assert fig is not None


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
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_classic()
        fig = render(p)
        assert fig is not None


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
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_void()
        fig = render(p)
        assert fig is not None


# ── Import smoke test ───────────────────────────────────────────────


# ── Tests for v0.8.0 theme element system ─────────────────────────


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

    def test_render_blank_major_grid(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(panel_grid_major=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme
        fig = render(p)
        assert fig is not None

    def test_render_custom_grid_color(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(panel_grid_major=element_line(color="#cccccc", size=1.5))
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme
        fig = render(p)
        assert fig is not None

    def test_render_element_text_title(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_title=element_text(size=24, color="darkblue"))
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Big Title") + theme
        fig = render(p)
        assert fig is not None

    def test_render_blank_title(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_title=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Hidden") + theme
        fig = render(p)
        assert fig is not None

    def test_render_blank_caption(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        theme = Theme(plot_caption=element_blank())
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(caption="Hidden") + theme
        fig = render(p)
        assert fig is not None

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


# ── Tests for theme() convenience function (1A) ──────────────────


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
    with pytest.raises(ConfigError, match="Unknown theme properties"):
        theme(nonexistent_field=42)


def test_theme_composition():
    combined = theme_minimal() + theme(title_size=20)
    assert combined.title_size == 20
    # theme_minimal sets panel_background to "none"
    assert combined.panel_background == "none"


def test_theme_empty():
    t = theme()
    assert t == Theme()


# ── Tests for v0.11.0 theme additions ─────────────────────────────


class TestThemeSetGet:
    @pytest.fixture(autouse=True)
    def _reset_global_theme(self):
        theme_set(Theme())
        yield
        theme_set(Theme())

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
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = render(p)
        # dark theme has dark background
        assert fig.get_facecolor() != (1.0, 1.0, 1.0, 1.0)

    def test_plot_theme_overrides_global(self):
        """Plot-level theme should override global theme."""
        theme_set(theme_dark())
        df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(background="#ff0000")
        fig = render(p)
        # The plot-level red background should win
        fc = fig.get_facecolor()
        assert fc[0] == 1.0  # red channel


class TestThemeUpdate:
    @pytest.fixture(autouse=True)
    def _reset_global_theme(self):
        theme_set(Theme())
        yield
        theme_set(Theme())

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


class TestThemeUse:
    @pytest.fixture(autouse=True)
    def _reset_global_theme(self):
        theme_set(Theme())
        yield
        theme_set(Theme())

    def test_sets_theme_inside_block(self):
        from plotten import theme_use

        with theme_use(theme_dark()):
            assert theme_get().background == "#2d2d2d"

    def test_restores_theme_after_block(self):
        from plotten import theme_use

        original = theme_get()
        with theme_use(theme_dark()):
            pass
        assert theme_get() == original

    def test_restores_on_exception(self):
        from plotten import theme_use

        original = theme_get()
        with pytest.raises(RuntimeError), theme_use(theme_dark()):
            raise RuntimeError("boom")
        assert theme_get() == original

    def test_yields_the_theme(self):
        from plotten import theme_use

        dark = theme_dark()
        with theme_use(dark) as t:
            assert t is dark

    def test_nesting(self):
        from plotten import theme_use

        original = theme_get()
        with theme_use(theme_dark()):
            with theme_use(theme_minimal()):
                assert theme_get().panel_background == "none"
            assert theme_get().background == "#2d2d2d"
        assert theme_get() == original


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
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_grey()
        fig = render(p)
        assert fig is not None


# ── Tests for v1.1.0 Phase 1 theme gallery ────────────────────────


def _make_plot():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    return ggplot(df, aes(x="x", y="y")) + geom_point()


def _make_legend_plot():
    """Standard colored scatter plot for legend tests."""
    from plotten import scale_color_discrete

    df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0], "g": ["a", "b", "c"]})
    return ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + scale_color_discrete()


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
    assert callable(plotten.theme_light)
    assert callable(plotten.theme_test)


# ---------------------------------------------------------------------------
# New theme fields — ggplot2 gap closure
# ---------------------------------------------------------------------------


class TestNewThemeFields:
    """Tests for per-axis elements, ticks, spacing, legend key, etc."""

    def test_per_axis_title_elements(self):
        from plotten.themes._elements import ElementBlank, ElementText

        t = Theme(
            axis_title_x=element_text(size=16, color="red"),
            axis_title_y=element_blank(),
        )
        assert isinstance(t.axis_title_x, ElementText)
        assert t.axis_title_x.size == 16
        assert t.axis_title_x.color == "red"
        assert isinstance(t.axis_title_y, ElementBlank)

    def test_per_axis_text_elements(self):
        from plotten.themes._elements import ElementText

        t = Theme(
            axis_text_x=element_text(size=8, rotation=45),
            axis_text_y=element_text(size=10),
        )
        assert isinstance(t.axis_text_x, ElementText)
        assert t.axis_text_x.size == 8
        assert t.axis_text_x.rotation == 45
        assert isinstance(t.axis_text_y, ElementText)
        assert t.axis_text_y.size == 10

    def test_axis_ticks_elements(self):
        from plotten.themes._elements import ElementBlank, ElementLine

        t = Theme(
            axis_ticks=element_line(color="gray", size=0.5),
            axis_ticks_x=element_blank(),
        )
        assert isinstance(t.axis_ticks, ElementLine)
        assert t.axis_ticks.color == "gray"
        assert isinstance(t.axis_ticks_x, ElementBlank)

    def test_axis_ticks_length_per_axis(self):
        t = Theme(axis_ticks_length_x=6.0, axis_ticks_length_y=3.0)
        assert t.axis_ticks_length_x == 6.0
        assert t.axis_ticks_length_y == 3.0

    def test_axis_line_element(self):
        from plotten.themes._elements import ElementLine

        t = Theme(axis_line_element=element_line(color="black", size=1.0))
        assert isinstance(t.axis_line_element, ElementLine)
        assert t.axis_line_element.color == "black"
        assert t.axis_line_element.size == 1.0

    def test_per_axis_grid_elements(self):
        from plotten.themes._elements import ElementBlank, ElementLine

        t = Theme(
            panel_grid_major_x=element_line(color="red"),
            panel_grid_major_y=element_blank(),
        )
        assert isinstance(t.panel_grid_major_x, ElementLine)
        assert t.panel_grid_major_x.color == "red"
        assert isinstance(t.panel_grid_major_y, ElementBlank)

    def test_panel_spacing(self):
        t = Theme(panel_spacing=0.12, panel_spacing_x=0.1, panel_spacing_y=0.15)
        assert t.panel_spacing == 0.12
        assert t.panel_spacing_x == 0.1
        assert t.panel_spacing_y == 0.15

    def test_strip_per_axis(self):
        from plotten.themes._elements import ElementText

        t = Theme(
            strip_text_x=element_text(size=12, color="blue"),
            strip_text_y=element_text(size=10),
            strip_background_x="#eeeeee",
            strip_background_y="#dddddd",
            strip_placement="inside",
        )
        assert isinstance(t.strip_text_x, ElementText)
        assert t.strip_text_x.size == 12
        assert isinstance(t.strip_text_y, ElementText)
        assert t.strip_text_y.size == 10
        assert t.strip_background_x == "#eeeeee"
        assert t.strip_placement == "inside"

    def test_legend_key(self):
        from plotten.themes._elements import ElementRect

        t = Theme(
            legend_key=element_rect(fill="white", color="gray"),
            legend_key_size=25.0,
            legend_key_width=30.0,
            legend_key_height=15.0,
        )
        assert isinstance(t.legend_key, ElementRect)
        assert t.legend_key.fill == "white"
        assert t.legend_key_size == 25.0
        assert t.legend_key_width == 30.0
        assert t.legend_key_height == 15.0

    def test_legend_spacing_and_margin(self):
        t = Theme(legend_spacing=6.0, legend_margin=10.0)
        assert t.legend_spacing == 6.0
        assert t.legend_margin == 10.0

    def test_plot_background(self):
        from plotten.themes._elements import ElementRect

        t = Theme(plot_background=element_rect(fill="#fafafa"))
        assert isinstance(t.plot_background, ElementRect)
        assert t.plot_background.fill == "#fafafa"

    def test_plot_margin(self):
        t = Theme(plot_margin=(0.05, 0.05, 0.05, 0.05))
        assert t.plot_margin == (0.05, 0.05, 0.05, 0.05)

    def test_aspect_ratio(self):
        t = Theme(aspect_ratio=0.75)
        assert t.aspect_ratio == 0.75

    def test_composition_preserves_new_fields(self):
        from plotten.themes._elements import ElementText

        t1 = Theme(axis_title_x=element_text(size=16))
        t2 = Theme(axis_title_y=element_text(size=14))
        combined = t1 + t2
        assert isinstance(combined.axis_title_x, ElementText)
        assert combined.axis_title_x.size == 16
        assert isinstance(combined.axis_title_y, ElementText)
        assert combined.axis_title_y.size == 14

    def test_theme_function_validates_new_fields(self):
        t = theme(axis_ticks_length_x=5.0, panel_spacing=0.1, aspect_ratio=1.0)
        assert t.axis_ticks_length_x == 5.0
        assert t.panel_spacing == 0.1
        assert t.aspect_ratio == 1.0

    def test_theme_function_rejects_invalid_new_field(self):
        with pytest.raises(ConfigError, match="Unknown theme"):
            theme(axis_ticks_length_z=5.0)

    def test_render_with_per_axis_elements(self):
        """Smoke test: rendering with per-axis element overrides doesn't crash."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                axis_text_x=element_text(size=8, rotation=45, color="red"),
                axis_title_y=element_blank(),
                axis_ticks=element_line(color="gray"),
                axis_ticks_x=element_blank(),
                axis_line_element=element_line(color="black", size=1.0),
                panel_grid_major_x=element_blank(),
                panel_grid_major_y=element_line(color="#cccccc", size=0.5),
            )
        )
        render(p)

    def test_render_with_aspect_ratio(self):
        """Smoke test: aspect_ratio affects figure size."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(aspect_ratio=0.5)
        fig = render(p)
        w, h = fig.get_size_inches()
        # aspect_ratio=0.5 means h = w * 0.5
        assert abs(h - w * 0.5) < 0.1

    def test_render_with_plot_margin(self):
        """Smoke test: plot_margin doesn't crash rendering."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(plot_margin=(0.05, 0.05, 0.05, 0.05))
        )
        render(p)

    def test_render_with_panel_spacing(self):
        """Smoke test: panel_spacing doesn't crash faceted rendering."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "a"]})
        from plotten import facet_wrap

        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g")
            + theme(panel_spacing=0.15)
        )
        render(p)


class TestDarkThemeTextColors:
    """Fix 1: Dark theme should have light text on dark backgrounds."""

    def test_dark_theme_has_light_title(self):
        from plotten import theme_dark

        t = theme_dark()
        assert t.title_color == "#ffffff"

    def test_dark_theme_has_light_subtitle(self):
        from plotten import theme_dark

        t = theme_dark()
        assert t.subtitle_color == "#e0e0e0"

    def test_dark_theme_has_light_axis_text(self):
        from plotten import theme_dark
        from plotten.themes._elements import ElementText

        t = theme_dark()
        assert isinstance(t.axis_text, ElementText)
        assert t.axis_text.color == "#cccccc"

    def test_dark_theme_has_light_axis_title(self):
        from plotten import theme_dark
        from plotten.themes._elements import ElementText

        t = theme_dark()
        assert isinstance(t.axis_title, ElementText)
        assert t.axis_title.color == "#e0e0e0"

    def test_dark_theme_has_light_strip_text(self):
        from plotten import theme_dark

        t = theme_dark()
        assert t.strip_text_color == "#e0e0e0"

    def test_dark_theme_renders(self):
        """Smoke test: dark theme renders without errors."""
        from plotten import theme_dark

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_dark()
        render(p)


class TestGeomFontInheritance:
    """Fix 2: geom_text/geom_label should inherit theme font_family."""

    def test_geom_text_inherits_font(self):
        from plotten import geom_text

        df = pl.DataFrame({"x": [1.0], "y": [1.0], "lab": ["hello"]})
        p = (
            ggplot(df, aes(x="x", y="y", label="lab"))
            + geom_text()
            + theme(font_family="monospace")
        )
        fig = render(p)
        ax = fig.axes[0]
        texts = [t for t in ax.texts if t.get_text() == "hello"]
        assert len(texts) == 1
        assert "monospace" in str(texts[0].get_fontfamily())

    def test_geom_text_explicit_family_overrides(self):
        from plotten import geom_text

        df = pl.DataFrame({"x": [1.0], "y": [1.0], "lab": ["hello"]})
        p = (
            ggplot(df, aes(x="x", y="y", label="lab"))
            + geom_text(family="serif")
            + theme(font_family="monospace")
        )
        fig = render(p)
        ax = fig.axes[0]
        texts = [t for t in ax.texts if t.get_text() == "hello"]
        assert len(texts) == 1
        assert "serif" in str(texts[0].get_fontfamily())


class TestThemeLinedraw:
    """Fix 3: theme_linedraw() should exist."""

    def test_linedraw_exists(self):

        t = theme_linedraw()
        assert isinstance(t, Theme)

    def test_linedraw_has_white_background(self):

        t = theme_linedraw()
        assert t.panel_background == "#ffffff"

    def test_linedraw_has_border(self):

        t = theme_linedraw()
        assert t.panel_border_color == "#000000"

    def test_linedraw_composable(self):

        combined = theme_linedraw() + Theme(title_size=20)
        assert combined.title_size == 20
        assert combined.panel_border_color == "#000000"

    def test_linedraw_renders(self):

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_linedraw()
        render(p)


class TestThemeLight:
    """theme_light() — light grey axes directing attention to data."""

    def test_light_exists(self):

        t = theme_light()
        assert isinstance(t, Theme)

    def test_light_has_white_panel(self):

        t = theme_light()
        assert t.panel_background == "#ffffff"

    def test_light_has_grey_border(self):

        t = theme_light()
        assert t.panel_border_color == "#999999"

    def test_light_composable(self):

        combined = theme_light() + Theme(title_size=20)
        assert combined.title_size == 20
        assert combined.panel_border_color == "#999999"

    def test_light_renders(self):

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_light()
        render(p)


class TestThemeTest:
    """theme_test() — stable theme for visual unit tests."""

    def test_test_exists(self):

        t = theme_test()
        assert isinstance(t, Theme)

    def test_test_has_white_background(self):

        t = theme_test()
        assert t.panel_background == "#ffffff"
        assert t.background == "#ffffff"

    def test_test_no_grid(self):

        t = theme_test()
        assert t.grid_major_x is False
        assert t.grid_major_y is False

    def test_test_has_border(self):

        t = theme_test()
        assert t.panel_border_color == "#000000"

    def test_test_composable(self):

        combined = theme_test() + Theme(title_size=20)
        assert combined.title_size == 20
        assert combined.panel_border_color == "#000000"

    def test_test_renders(self):

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme_test()
        render(p)


class TestSecAxisThemeStyling:
    """Fix 5: Secondary axes should respect theme styling."""

    @staticmethod
    def _find_sec_axis(fig):
        from matplotlib.axes._secondary_axes import SecondaryAxis

        ax = fig.axes[0]
        for child in ax.get_children():
            if isinstance(child, SecondaryAxis):
                return child
        return None

    def test_sec_axis_with_theme(self):
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(
                sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2, name="Secondary")
            )
            + theme(font_family="monospace", tick_size=8)
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None
        assert sec.get_ylabel() == "Secondary"

    def test_sec_axis_text_y_right(self):
        """axis_text_y_right should style secondary y-axis tick labels."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_text_y_right=element_text(color="red", size=14))
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_text_y_right_blank(self):
        """axis_text_y_right=element_blank() should hide secondary tick labels."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_text_y_right=element_blank())
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_title_y_right(self):
        """axis_title_y_right should style secondary y-axis title."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(
                sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2, name="Right")
            )
            + theme(axis_title_y_right=element_text(color="blue", size=16))
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_title_y_right_blank(self):
        """axis_title_y_right=element_blank() should suppress secondary title."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(
                sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2, name="Right")
            )
            + theme(axis_title_y_right=element_blank())
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None
        # Title should be suppressed
        assert sec.get_ylabel() == ""

    def test_sec_axis_ticks_y_right(self):
        """axis_ticks_y_right should style secondary tick marks."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_ticks_y_right=element_line(color="green", size=2.0))
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_ticks_y_right_blank(self):
        """axis_ticks_y_right=element_blank() should suppress secondary tick marks."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_ticks_y_right=element_blank())
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_line_y_right(self):
        """axis_line_y_right should style secondary spine."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_line_y_right=element_line(color="purple", size=2.0))
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None

    def test_sec_axis_x_top(self):
        """Secondary x-axis (top) should respect per-position theme fields."""
        from plotten import scale_x_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_x_continuous(
                sec_axis=sec_axis(
                    trans=lambda x: x * 100, inverse=lambda x: x / 100, name="Percent"
                )
            )
            + theme(
                axis_text_x_top=element_text(color="red"),
                axis_title_x_top=element_text(size=14),
                axis_ticks_x_top=element_line(color="blue"),
                axis_ticks_length_x_top=5.0,
            )
        )
        fig = render(p)
        assert fig is not None

    def test_sec_axis_ticks_length_y_right(self):
        """axis_ticks_length_y_right should control tick length on secondary axis."""
        from plotten import scale_y_continuous, sec_axis

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [4.0, 5.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 2, inverse=lambda x: x / 2))
            + theme(axis_ticks_length_y_right=8.0)
        )
        fig = render(p)
        sec = self._find_sec_axis(fig)
        assert sec is not None


class TestPerPositionPrimaryAxis:
    """Per-position theme fields for primary axes (bottom, left)."""

    def test_axis_text_x_bottom(self):
        """axis_text_x_bottom should override primary x tick labels."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(axis_text_x_bottom=element_text(color="red", size=14))
        )
        fig = render(p)
        assert fig is not None

    def test_axis_text_y_left(self):
        """axis_text_y_left should override primary y tick labels."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(axis_text_y_left=element_text(color="blue", size=12))
        )
        fig = render(p)
        assert fig is not None

    def test_axis_title_x_bottom_blank(self):
        """axis_title_x_bottom=element_blank() should suppress primary x title."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(x="X Label")
            + theme(axis_title_x_bottom=element_blank())
        )
        fig = render(p)
        assert fig is not None

    def test_axis_title_y_left(self):
        """axis_title_y_left should style primary y-axis title."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(y="Y Label")
            + theme(axis_title_y_left=element_text(color="green", size=16))
        )
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_x_bottom(self):
        """axis_ticks_x_bottom should style primary x tick marks."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(axis_ticks_x_bottom=element_line(color="orange", size=2.0))
        )
        fig = render(p)
        assert fig is not None

    def test_axis_line_x_bottom_blank(self):
        """axis_line_x_bottom=element_blank() should hide bottom spine."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                axis_line_x=True,
                axis_line_x_bottom=element_blank(),
            )
        )
        fig = render(p)
        ax = fig.axes[0]
        assert not ax.spines["bottom"].get_visible()

    def test_axis_line_y_left_styled(self):
        """axis_line_y_left=element_line() should show and style left spine."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                axis_line_y_left=element_line(color="red", size=2.0),
            )
        )
        fig = render(p)
        ax = fig.axes[0]
        assert ax.spines["left"].get_visible()

    def test_axis_ticks_length_x_bottom(self):
        """axis_ticks_length_x_bottom should override primary x tick length."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(axis_ticks_length_x_bottom=8.0)
        fig = render(p)
        assert fig is not None


class TestLegendInside:
    """Fix 6: Tuple legend position should be axes-relative."""

    def test_legend_inside_rendering(self):
        from plotten import scale_color_discrete

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_position=(0.8, 0.8))
        )
        render(p)


class TestLegendKeySize:
    """Fix 4 (partial): legend_key_size is wired into rendering."""

    def test_legend_key_size_rendering(self):
        from plotten import scale_color_discrete

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_key_size=30.0, legend_spacing=8.0, legend_margin=12.0)
        )
        render(p)


class TestGeomLabelThemeAware:
    """Fix 7: geom_label should adapt to dark themes."""

    def test_label_on_dark_theme(self):
        from plotten import geom_label, theme_dark

        df = pl.DataFrame({"x": [1.0], "y": [1.0], "lab": ["hello"]})
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_label() + theme_dark()
        render(p)

    def test_label_on_light_theme(self):
        from plotten import geom_label

        df = pl.DataFrame({"x": [1.0], "y": [1.0], "lab": ["hello"]})
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_label()
        render(p)


class TestCompleteThemeFields:
    """Tests for new ggplot2 gap-closure fields."""

    _NONE_DEFAULT_FIELDS = (
        # Per-position axis variants
        "axis_title_x_top",
        "axis_title_x_bottom",
        "axis_title_y_left",
        "axis_title_y_right",
        "axis_text_x_top",
        "axis_text_x_bottom",
        "axis_text_y_left",
        "axis_text_y_right",
        "axis_ticks_x_top",
        "axis_ticks_x_bottom",
        "axis_ticks_y_left",
        "axis_ticks_y_right",
        "axis_ticks_length",
        "axis_ticks_length_x_top",
        "axis_ticks_length_x_bottom",
        "axis_ticks_length_y_left",
        "axis_ticks_length_y_right",
        "axis_line_x_element",
        "axis_line_y_element",
        "axis_line_x_top",
        "axis_line_x_bottom",
        "axis_line_y_left",
        "axis_line_y_right",
        # Polar
        "axis_text_theta",
        "axis_text_r",
        "axis_ticks_theta",
        "axis_ticks_r",
        "axis_line_theta",
        "axis_line_r",
        # Minor ticks
        "axis_minor_ticks",
        "axis_minor_ticks_x",
        "axis_minor_ticks_y",
        "axis_minor_ticks_length",
        "axis_minor_ticks_length_x",
        "axis_minor_ticks_length_y",
        # Legend layout
        "legend_direction",
        "legend_justification",
        "legend_position_inside",
        "legend_box",
        "legend_box_just",
        "legend_box_margin",
        "legend_box_background",
        "legend_box_spacing",
        "legend_text_position",
        "legend_title_position",
        "legend_frame",
        "legend_ticks",
        "legend_ticks_length",
        "legend_axis_line",
        "legend_key_spacing",
        "legend_key_spacing_x",
        "legend_key_spacing_y",
        # Plot tags
        "plot_tag",
        "plot_tag_position",
        "plot_tag_location",
        # Panel control
        "panel_widths",
        "panel_heights",
        # Strip refinements
        "strip_text_x_top",
        "strip_text_x_bottom",
        "strip_text_y_left",
        "strip_text_y_right",
        "strip_switch_pad_grid",
        "strip_switch_pad_wrap",
        # Base element inheritance
        "line",
        "rect",
        "text",
        "title",
        "spacing",
        "margins",
    )

    @pytest.mark.parametrize("field", _NONE_DEFAULT_FIELDS)
    def test_field_defaults_to_none(self, field: str):
        assert getattr(Theme(), field) is None

    def test_non_none_defaults(self):
        t = Theme()
        assert t.legend_row_major is False
        assert t.plot_title_position == "plot"
        assert t.plot_caption_position == "plot"
        assert t.panel_ontop is False
        assert t.strip_clip == "inherit"
        assert t.complete is False
        assert t.validate is True

    def test_new_fields_preserved_through_add(self):
        t1 = Theme(panel_ontop=True, legend_direction="horizontal")
        t2 = Theme(plot_title_position="plot")
        combined = t1 + t2
        assert combined.panel_ontop is True
        assert combined.legend_direction == "horizontal"
        assert combined.plot_title_position == "plot"

    def test_theme_function_accepts_new_fields(self):
        t = theme(
            panel_ontop=True,
            legend_direction="horizontal",
            plot_title_position="plot",
            plot_caption_position="plot",
            strip_clip="on",
        )
        assert t.panel_ontop is True
        assert t.legend_direction == "horizontal"

    def test_theme_function_rejects_typos_in_new_fields(self):
        with pytest.raises(ConfigError, match="Unknown theme"):
            theme(panel_on_top=True)


class TestCompleteFlag:
    """complete=True theme replaces rather than merges."""

    def test_complete_theme_replaces(self):
        base = Theme(title_size=20, panel_ontop=True)
        complete = Theme(title_size=16, complete=True)
        result = base + complete
        assert result.title_size == 16
        assert result.panel_ontop is False  # default, not from base
        assert result.complete is True

    def test_incomplete_theme_merges(self):
        base = Theme(title_size=20)
        overlay = Theme(label_size=16)
        result = base + overlay
        assert result.title_size == 20
        assert result.label_size == 16

    def test_predefined_themes_are_complete(self):
        assert theme_default().complete is True
        assert theme_bw().complete is True
        assert theme_classic().complete is True
        assert theme_dark().complete is True
        assert theme_void().complete is True
        assert theme_grey().complete is True
        assert theme_538().complete is True
        assert theme_economist().complete is True
        assert theme_tufte().complete is True
        assert theme_seaborn().complete is True
        assert theme_minimal().complete is True

    def test_complete_theme_overrides_custom(self):
        custom = Theme(title_size=30, background="#ff0000")
        result = custom + theme_bw()
        assert result.title_size == theme_bw().title_size
        assert result.background == theme_bw().background


class TestBaseSize:
    """base_size derives all text sizes from a single parameter."""

    def test_basic_derivation(self):
        t = Theme(base_size=11)
        assert t.title_size == pytest.approx(13.2)  # 11 * 1.2
        assert t.subtitle_size == pytest.approx(9.9)  # 11 * 0.9
        assert t.label_size == pytest.approx(11.0)  # 11 * 1.0
        assert t.tick_size == pytest.approx(8.8)  # 11 * 0.8

    def test_explicit_override_wins(self):
        t = Theme(base_size=11, title_size=20)
        assert t.title_size == 20
        assert t.label_size == pytest.approx(11.0)
        assert t.tick_size == pytest.approx(8.8)

    def test_none_preserves_backward_compat(self):
        t = Theme()
        assert t.base_size is None
        assert t.title_size == 16
        assert t.label_size == 11
        assert t.tick_size == 10
        assert t.subtitle_size == 12

    def test_complete_theme_with_base_size(self):
        t = theme_grey(base_size=14)
        assert t.title_size == pytest.approx(16.8)
        assert t.label_size == pytest.approx(14.0)
        assert t.tick_size == pytest.approx(11.2)
        assert t.subtitle_size == pytest.approx(12.6)
        assert t.base_size == 14

    def test_merge_with_base_size(self):
        result = theme_grey() + theme(base_size=14)
        assert result.title_size == pytest.approx(16.8)
        assert result.tick_size == pytest.approx(11.2)

    def test_theme_void_preserves_tick_size_zero(self):
        t = theme_void()
        assert t.tick_size == 0

    def test_theme_538_with_base_size(self):
        t = theme_538(base_size=14)
        assert t.title_size == pytest.approx(16.8)  # derived, not hardcoded 18

    def test_theme_538_without_base_size(self):
        t = theme_538()
        assert t.title_size == 18  # original hardcoded value

    def test_theme_economist_with_base_size(self):
        t = theme_economist(base_size=14)
        assert t.title_size == pytest.approx(16.8)

    def test_theme_economist_without_base_size(self):
        t = theme_economist()
        assert t.title_size == 18

    def test_caption_sizing_with_base_size(self):
        """Caption Rel(0.8) multiplies against base_size, not tick_size."""
        t = Theme(base_size=10)
        from plotten.themes._text_props import text_props

        kw = text_props(
            t.plot_caption,
            t,
            default_size=t.base_size if t.base_size is not None else t.tick_size,
        )
        assert kw["fontsize"] == pytest.approx(8.0)  # 10 * 0.8

    def test_base_size_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(title="Big text", caption="Small caption")
            + theme(base_size=16)
        )
        render(p)


class TestBackgroundTypeUpgrades:
    """panel_background, legend_background, strip_background accept ElementRect."""

    def test_panel_background_str(self):
        """String value still works as fill color."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(panel_background="#f0f0f0")
        render(p)

    def test_panel_background_element_rect(self):
        from plotten import element_rect

        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(panel_background=element_rect(fill="#f0f0f0", color="#000000", size=1.0))
        )
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_facecolor()[:3] != (1.0, 1.0, 1.0)  # not default white

    def test_legend_background_element_rect(self):
        from plotten import element_rect

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3], "c": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="c"))
            + geom_point()
            + theme(legend_background=element_rect(fill="#eeeeee", color="#999999"))
        )
        render(p)

    def test_strip_background_element_rect(self):
        from plotten import element_rect, facet_wrap

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g")
            + theme(strip_background=element_rect(fill="#d9d9d9", color="#333333", size=0.5))
        )
        render(p)

    def test_resolve_background_str(self):
        from plotten.themes._elements import resolve_background

        fill, color, size = resolve_background("#ff0000")
        assert fill == "#ff0000"
        assert color is None
        assert size is None

    def test_resolve_background_element_rect(self):
        from plotten import element_rect
        from plotten.themes._elements import resolve_background

        fill, color, size = resolve_background(element_rect(fill="white", color="black", size=2.0))
        assert fill == "white"
        assert color == "black"
        assert size == 2.0

    def test_resolve_background_none(self):
        from plotten.themes._elements import resolve_background

        assert resolve_background(None) == (None, None, None)


class TestRemainingGapFields:
    """Fields added to close remaining ggplot2 gaps."""

    def test_legend_justification_positional_defaults(self):
        t = Theme()
        assert t.legend_justification_top is None
        assert t.legend_justification_bottom is None
        assert t.legend_justification_left is None
        assert t.legend_justification_right is None
        assert t.legend_justification_inside is None

    def test_legend_key_justification_default(self):
        t = Theme()
        assert t.legend_key_justification is None

    def test_legend_margin_accepts_margin(self):
        from plotten.themes._elements import Margin

        t = Theme(legend_margin=Margin(top=5, right=10, bottom=5, left=10))
        assert isinstance(t.legend_margin, Margin)

    def test_legend_margin_accepts_tuple(self):
        t = Theme(legend_margin=(5, 10, 5, 10))
        assert t.legend_margin == (5, 10, 5, 10)

    def test_legend_margin_accepts_float(self):
        t = Theme(legend_margin=12.0)
        assert t.legend_margin == 12.0

    def test_polar_tick_length_fields(self):
        t = Theme()
        assert t.axis_ticks_length_theta is None
        assert t.axis_ticks_length_r is None

    def test_minor_ticks_positional_fields(self):
        t = Theme()
        assert t.axis_minor_ticks_x_top is None
        assert t.axis_minor_ticks_x_bottom is None
        assert t.axis_minor_ticks_y_left is None
        assert t.axis_minor_ticks_y_right is None
        assert t.axis_minor_ticks_theta is None
        assert t.axis_minor_ticks_r is None

    def test_minor_ticks_length_positional_fields(self):
        t = Theme()
        assert t.axis_minor_ticks_length_x_top is None
        assert t.axis_minor_ticks_length_x_bottom is None
        assert t.axis_minor_ticks_length_y_left is None
        assert t.axis_minor_ticks_length_y_right is None
        assert t.axis_minor_ticks_length_theta is None
        assert t.axis_minor_ticks_length_r is None

    def test_new_fields_accepted_by_theme_function(self):
        t = theme(
            legend_justification_top="left",
            legend_key_justification="center",
            axis_ticks_length_theta=5.0,
            axis_minor_ticks_x_top=element_blank(),
            axis_minor_ticks_length_theta=2.0,
        )
        assert t.legend_justification_top == "left"
        assert t.legend_key_justification == "center"
        assert t.axis_ticks_length_theta == 5.0

    def test_new_fields_preserved_through_add(self):
        t1 = Theme(legend_justification_top="left", axis_ticks_length_r=3.0)
        t2 = Theme(title_size=20)
        combined = t1 + t2
        assert combined.legend_justification_top == "left"
        assert combined.axis_ticks_length_r == 3.0


class TestLegendLocationAndSpacing:
    """legend_location and legend_spacing_x/y fields."""

    def test_legend_location_default_is_none(self):
        t = Theme()
        assert t.legend_location is None

    def test_legend_spacing_xy_default_is_none(self):
        t = Theme()
        assert t.legend_spacing_x is None
        assert t.legend_spacing_y is None

    def test_legend_location_panel_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3], "c": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="c"))
            + geom_point()
            + theme(legend_location="panel")
        )
        render(p)

    def test_legend_location_plot_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3], "c": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", color="c")) + geom_point() + theme(legend_location="plot")
        render(p)

    def test_legend_spacing_y_renders(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3], "c": ["a", "b", "a"]})
        p = ggplot(df, aes(x="x", y="y", color="c")) + geom_point() + theme(legend_spacing_y=10.0)
        render(p)

    def test_legend_location_preserved_through_add(self):
        t1 = Theme(legend_location="panel")
        t2 = Theme(title_size=20)
        combined = t1 + t2
        assert combined.legend_location == "panel"

    def test_legend_spacing_y_preserved_through_add(self):
        t1 = Theme(legend_spacing_y=10.0)
        t2 = Theme(title_size=20)
        combined = t1 + t2
        assert combined.legend_spacing_y == 10.0


class TestPanelGrid:
    """panel_grid parent element suppresses or styles all grid lines."""

    def test_panel_grid_blank_suppresses_all(self):
        """theme(panel_grid=element_blank()) removes all grid lines."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(panel_grid=element_blank())
        fig = render(p)
        ax = fig.axes[0]
        # All grid lines should be hidden
        x_lines = ax.xaxis.get_gridlines()
        assert len(x_lines) == 0 or not x_lines[0].get_visible()
        y_lines = ax.yaxis.get_gridlines()
        assert len(y_lines) == 0 or not y_lines[0].get_visible()

    def test_panel_grid_blank_with_major_override(self):
        """panel_grid=blank still wins even when grid_major_x=True."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(panel_grid=element_blank(), grid_major_x=True, grid_major_y=True)
        )
        fig = render(p)
        ax = fig.axes[0]
        x_lines = ax.xaxis.get_gridlines()
        assert len(x_lines) == 0 or not x_lines[0].get_visible()
        y_lines = ax.yaxis.get_gridlines()
        assert len(y_lines) == 0 or not y_lines[0].get_visible()

    def test_panel_grid_element_line_sets_color(self):
        """panel_grid=element_line(color=...) propagates to all grid lines."""
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(panel_grid=element_line(color="#ff0000"))
        )
        fig = render(p)
        ax = fig.axes[0]
        x_lines = ax.xaxis.get_gridlines()
        y_lines = ax.yaxis.get_gridlines()
        assert x_lines[0].get_color() == "#ff0000"
        assert y_lines[0].get_color() == "#ff0000"

    def test_panel_grid_default_is_none(self):
        t = Theme()
        assert t.panel_grid is None

    def test_panel_grid_preserved_through_add(self):
        t1 = Theme(panel_grid=element_blank())
        t2 = Theme(title_size=20)
        combined = t1 + t2
        assert isinstance(combined.panel_grid, ElementBlank)


class TestPanelOntop:
    """panel_ontop wiring into rendering."""

    def test_panel_ontop_false_default(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_axisbelow() is True

    def test_panel_ontop_true(self):
        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1, 2, 3]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(panel_ontop=True)
        fig = render(p)
        ax = fig.axes[0]
        assert ax.get_axisbelow() is not True


class TestLegendDirection:
    """legend_direction wiring into rendering."""

    def test_horizontal_legend_renders(self):
        from plotten import scale_color_discrete

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_direction="horizontal")
        )
        render(p)

    def test_vertical_legend_renders(self):
        from plotten import scale_color_discrete

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_direction="vertical")
        )
        render(p)


class TestPlotTitlePosition:
    """plot_title_position wiring into rendering."""

    def test_title_position_panel(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(title="Centered")
            + theme(plot_title_position="panel")
        )
        render(p)

    def test_title_position_plot(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(title="Left-aligned")
            + theme(plot_title_position="plot")
        )
        render(p)

    def test_caption_position_plot(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(caption="Right caption")
            + theme(plot_caption_position="plot")
        )
        render(p)

    def test_caption_position_panel(self):
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(caption="Panel caption")
            + theme(plot_caption_position="panel")
        )
        render(p)

    def test_default_title_left_aligned(self):
        """Default theme left-aligns title (plot_title_position='plot')."""
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [1, 2]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title="Left by default")
        render(p)


class TestStripPlacement:
    """Fix 4 (partial): strip_placement is wired into rendering."""

    def test_strip_inside(self):
        from plotten import facet_wrap

        df = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [4.0, 5.0, 6.0], "g": ["a", "b", "a"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g")
            + theme(strip_placement="inside")
        )
        render(p)


class TestIsDarkColor:
    """Unit tests for _is_dark_color helper."""

    def test_dark_colors(self):
        from plotten._render._mpl_theme import _is_dark_color

        assert _is_dark_color("#000000") is True
        assert _is_dark_color("#2d2d2d") is True
        assert _is_dark_color("#3d3d3d") is True

    def test_light_colors(self):
        from plotten._render._mpl_theme import _is_dark_color

        assert _is_dark_color("#ffffff") is False
        assert _is_dark_color("#ebebeb") is False
        assert _is_dark_color("#f0f0f0") is False

    def test_none_color(self):
        from plotten._render._mpl_theme import _is_dark_color

        assert _is_dark_color("none") is False

    def test_named_colors(self):
        from plotten._render._mpl_theme import _is_dark_color

        # Named dark colors are now correctly detected
        assert _is_dark_color("red") is True
        assert _is_dark_color("darkblue") is True
        # Named light colors
        assert _is_dark_color("white") is False
        assert _is_dark_color("yellow") is False
        # Invalid color strings
        assert _is_dark_color("notacolor") is False


# --- Margin tests ---


class TestMargin:
    def test_margin_construction(self):
        from plotten import Margin, margin

        m = margin(0.05, 0.1, 0.05, 0.1)
        assert isinstance(m, Margin)
        assert m.top == 0.05
        assert m.right == 0.1
        assert m.bottom == 0.05
        assert m.left == 0.1
        assert m.unit == "npc"

    def test_margin_defaults(self):
        from plotten import margin

        m = margin()
        assert m.top == 0
        assert m.right == 0
        assert m.bottom == 0
        assert m.left == 0

    def test_margin_npc_conversion(self):
        from plotten import margin

        m = margin(0.1, 0.2, 0.3, 0.4, unit="npc")
        result = m.to_npc(10, 8)
        assert result == (0.1, 0.2, 0.3, 0.4)

    def test_margin_inches_conversion(self):
        from plotten import margin

        m = margin(1, 1, 1, 1, unit="in")
        top, right, bottom, left = m.to_npc(fig_width=10, fig_height=8)
        assert top == pytest.approx(1.0 / 8.0)
        assert right == pytest.approx(1.0 / 10.0)
        assert bottom == pytest.approx(1.0 / 8.0)
        assert left == pytest.approx(1.0 / 10.0)

    def test_margin_cm_conversion(self):
        from plotten import margin

        m = margin(2.54, 2.54, 2.54, 2.54, unit="cm")
        top, right, bottom, left = m.to_npc(fig_width=10, fig_height=8)
        assert top == pytest.approx(1.0 / 8.0)
        assert right == pytest.approx(1.0 / 10.0)
        assert bottom == pytest.approx(1.0 / 8.0)
        assert left == pytest.approx(1.0 / 10.0)

    def test_margin_mm_conversion(self):
        from plotten import margin

        m = margin(25.4, 25.4, 25.4, 25.4, unit="mm")
        top, right, bottom, left = m.to_npc(fig_width=10, fig_height=8)
        assert top == pytest.approx(1.0 / 8.0)
        assert right == pytest.approx(1.0 / 10.0)
        assert bottom == pytest.approx(1.0 / 8.0)
        assert left == pytest.approx(1.0 / 10.0)

    def test_margin_unknown_unit(self):
        from plotten import margin

        with pytest.raises(ConfigError, match="Unknown margin unit"):
            margin(1, 1, 1, 1, unit="px")

    def test_margin_in_theme(self):
        from plotten import margin

        t = theme(plot_margin=margin(0.05, 0.05, 0.05, 0.05))
        assert t.plot_margin is not None

    def test_margin_render(self):
        from plotten import margin

        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(plot_margin=margin(0.05, 0.05, 0.05, 0.05))
        )
        fig = render(p)
        assert fig is not None

    def test_margin_with_inch_unit_render(self):
        from plotten import margin

        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(plot_margin=margin(0.5, 0.5, 0.5, 0.5, unit="in"))
        )
        fig = render(p)
        assert fig is not None


class TestLegendKey:
    """Tests for legend_key background wiring."""

    def test_legend_key_element_rect(self):
        """legend_key=element_rect() should render without error."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_key=element_rect(fill="#f0f0f0", color="#cccccc"))
        )
        fig = render(p)
        assert fig is not None

    def test_legend_key_blank(self):
        """legend_key=element_blank() should suppress key background."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_key=element_blank())
        )
        fig = render(p)
        assert fig is not None

    def test_legend_key_none_default(self):
        """Default legend_key=None renders without error."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
        p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
        fig = render(p)
        assert fig is not None


class TestLegendSpacingX:
    """Tests for legend_spacing_x wiring."""

    def test_spacing_x_horizontal(self):
        """legend_spacing_x with horizontal direction should render."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_direction="horizontal", legend_spacing_x=8.0)
        )
        fig = render(p)
        assert fig is not None

    def test_spacing_x_multicol(self):
        """legend_spacing_x with multi-column layout should render."""
        from plotten import guide_legend, guides

        df = pd.DataFrame({"x": range(6), "y": range(6), "g": ["a", "b", "c", "d", "e", "f"]})
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + theme(legend_spacing_x=8.0)
            + guides(color=guide_legend(n_cols=2))
        )
        fig = render(p)
        assert fig is not None


class TestPlotTag:
    """Tests for plot_tag rendering."""

    def test_tag_renders(self):
        """labs(tag='A') should render the tag on the figure."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(tag="A")
        fig = render(p)
        assert fig is not None
        # Check that a text artist with "A" exists on the figure
        texts = [t.get_text() for t in fig.texts]
        assert "A" in texts

    def test_tag_position_topright(self):
        """plot_tag_position='topright' should render without error."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(tag="B")
            + theme(plot_tag_position="topright")
        )
        fig = render(p)
        assert fig is not None

    def test_tag_position_tuple(self):
        """plot_tag_position=(x, y) tuple should render."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(tag="C")
            + theme(plot_tag_position=(0.1, 0.9))
        )
        fig = render(p)
        assert fig is not None

    def test_tag_element_blank_suppresses(self):
        """plot_tag=element_blank() should suppress the tag."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(tag="D")
            + theme(plot_tag=element_blank())
        )
        fig = render(p)
        assert fig is not None
        texts = [t.get_text() for t in fig.texts]
        assert "D" not in texts

    def test_tag_custom_styling(self):
        """plot_tag=element_text() should style the tag."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + labs(tag="E")
            + theme(plot_tag=element_text(size=24, color="red"))
        )
        fig = render(p)
        assert fig is not None

    def test_tag_none_no_render(self):
        """No tag should render when labs has no tag."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = render(p)
        assert fig is not None
        # No tag text on the figure
        texts = [t.get_text() for t in fig.texts]
        assert all(t != "A" for t in texts)

    def test_labs_tag_field(self):
        """Labs dataclass should have tag field."""
        from plotten._labs import Labs

        lab = Labs(tag="X")
        assert lab.tag == "X"

    def test_labs_merge_tag(self):
        """Labs merge should preserve tag from override."""
        from plotten._labs import Labs

        base = Labs(title="T", tag="A")
        override = Labs(tag="B")
        merged = base + override
        assert merged.tag == "B"
        assert merged.title == "T"


class TestMinorTicks:
    """Tests for minor tick rendering."""

    def test_minor_ticks_with_minor_grid(self):
        """Minor ticks should render when minor grid is enabled."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + theme(grid_minor_x=True)
        fig = render(p)
        assert fig is not None

    def test_minor_ticks_element_styling(self):
        """axis_minor_ticks element should style minor ticks."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                grid_minor_x=True,
                grid_minor_y=True,
                axis_minor_ticks=element_line(color="red", size=2.0),
            )
        )
        fig = render(p)
        assert fig is not None

    def test_minor_ticks_per_axis(self):
        """Per-axis minor tick elements should work."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                grid_minor_x=True,
                axis_minor_ticks_x=element_line(color="blue"),
            )
        )
        fig = render(p)
        assert fig is not None

    def test_minor_ticks_blank_suppresses(self):
        """element_blank() on axis_minor_ticks should suppress minor ticks."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                grid_minor_x=True,
                axis_minor_ticks=element_blank(),
            )
        )
        fig = render(p)
        assert fig is not None

    def test_minor_ticks_length(self):
        """axis_minor_ticks_length should control minor tick length."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(grid_minor_x=True, axis_minor_ticks_length=3.0)
        )
        fig = render(p)
        assert fig is not None

    def test_minor_ticks_length_per_axis(self):
        """Per-axis minor tick length should work."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(
                grid_minor_x=True,
                grid_minor_y=True,
                axis_minor_ticks_length_x=4.0,
                axis_minor_ticks_length_y=2.0,
            )
        )
        fig = render(p)
        assert fig is not None


class TestRowStrips:
    """Tests for facet_grid row strip (y-strip) rendering."""

    def test_facet_grid_rows_only(self):
        """facet_grid(rows=...) should render row strips."""
        from plotten.facets import facet_grid

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "r": ["a", "a", "b", "b"]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(rows="r")
        fig = render(p)
        assert fig is not None

    def test_facet_grid_rows_and_cols(self):
        """facet_grid(rows=..., cols=...) should render both strips."""
        from plotten.facets import facet_grid

        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [2, 4, 1, 3],
                "r": ["a", "a", "b", "b"],
                "c": ["x", "y", "x", "y"],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_grid(rows="r", cols="c")
        fig = render(p)
        assert fig is not None

    def test_row_strip_col_label_separation(self):
        """Row and col labels should be separated in facet_grid."""
        from plotten._render._resolve import _split_facet_label
        from plotten.facets._grid import FacetGrid

        facet = FacetGrid(rows="r", cols="c")
        row, col = _split_facet_label("a ~ x", facet)
        assert row == "a"
        assert col == "x"

    def test_row_strip_rows_only_split(self):
        """Rows-only facet should set row_label, col_label=None."""
        from plotten._render._resolve import _split_facet_label
        from plotten.facets._grid import FacetGrid

        facet = FacetGrid(rows="r")
        row, col = _split_facet_label("a", facet)
        assert row == "a"
        assert col is None

    def test_row_strip_cols_only_split(self):
        """Cols-only facet should set col_label, row_label=None."""
        from plotten._render._resolve import _split_facet_label
        from plotten.facets._grid import FacetGrid

        facet = FacetGrid(cols="c")
        row, col = _split_facet_label("x", facet)
        assert row is None
        assert col == "x"

    def test_strip_text_y_styling(self):
        """strip_text_y should style row strip labels."""
        from plotten.facets import facet_grid

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "r": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_grid(rows="r")
            + theme(strip_text_y=element_text(color="red", size=14))
        )
        fig = render(p)
        assert fig is not None

    def test_strip_background_y_styling(self):
        """strip_background_y should style row strip background."""
        from plotten.facets import facet_grid

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "r": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_grid(rows="r")
            + theme(strip_background_y=element_rect(fill="#f0f0f0", color="#cccccc"))
        )
        fig = render(p)
        assert fig is not None

    def test_resolved_panel_row_col_labels(self):
        """ResolvedPanel should have row_label and col_label fields."""
        from plotten._render._structures import ResolvedPanel

        p = ResolvedPanel(label="a ~ x", row_label="a", col_label="x")
        assert p.row_label == "a"
        assert p.col_label == "x"


class TestPanelWidthsHeights:
    """Tests for panel_widths and panel_heights facet sizing."""

    def test_panel_widths(self):
        """panel_widths should set column width ratios."""
        from plotten.facets import facet_wrap

        df = pd.DataFrame(
            {"x": [1, 2, 3, 4, 5, 6], "y": [1, 4, 9, 2, 5, 8], "g": ["a", "a", "b", "b", "c", "c"]}
        )
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g", n_cols=3)
            + theme(panel_widths=(2.0, 1.0, 1.0))
        )
        fig = render(p)
        assert fig is not None

    def test_panel_heights(self):
        """panel_heights should set row height ratios."""
        from plotten.facets import facet_grid

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "r": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_grid(rows="r")
            + theme(panel_heights=(2.0, 1.0))
        )
        fig = render(p)
        assert fig is not None

    def test_panel_widths_and_heights(self):
        """Both panel_widths and panel_heights together."""
        from plotten.facets import facet_grid

        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4],
                "y": [2, 4, 1, 3],
                "r": ["a", "a", "b", "b"],
                "c": ["x", "y", "x", "y"],
            }
        )
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_grid(rows="r", cols="c")
            + theme(panel_widths=(2.0, 1.0), panel_heights=(1.0, 2.0))
        )
        fig = render(p)
        assert fig is not None

    def test_panel_widths_none_default(self):
        """Default panel_widths=None should produce equal columns."""
        from plotten.facets import facet_wrap

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g")
        fig = render(p)
        assert fig is not None


class TestLegendColorbarRefinements:
    """Tests for legend_frame, legend_ticks, legend_ticks_length, legend_axis_line."""

    def _make_continuous_plot(self):
        from plotten import scale_color_gradient

        df = pd.DataFrame(
            {"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25], "v": [1.0, 2.0, 3.0, 4.0, 5.0]}
        )
        return (
            ggplot(df, aes(x="x", y="y", color="v"))
            + geom_point()
            + scale_color_gradient(low="blue", high="red")
        )

    def test_legend_frame(self):
        """legend_frame=element_rect() should add a border around the colorbar."""
        p = self._make_continuous_plot() + theme(
            legend_frame=element_rect(color="black", size=1.0)
        )
        fig = render(p)
        assert fig is not None

    def test_legend_ticks_styling(self):
        """legend_ticks=element_line() should style tick marks."""
        p = self._make_continuous_plot() + theme(legend_ticks=element_line(color="red", size=2.0))
        fig = render(p)
        assert fig is not None

    def test_legend_ticks_blank(self):
        """legend_ticks=element_blank() should suppress tick marks."""
        p = self._make_continuous_plot() + theme(legend_ticks=element_blank())
        fig = render(p)
        assert fig is not None

    def test_legend_ticks_length(self):
        """legend_ticks_length should control tick mark length."""
        p = self._make_continuous_plot() + theme(legend_ticks_length=8.0)
        fig = render(p)
        assert fig is not None

    def test_legend_axis_line(self):
        """legend_axis_line=element_line() should show the value axis spine."""
        p = self._make_continuous_plot() + theme(
            legend_axis_line=element_line(color="black", size=0.5)
        )
        fig = render(p)
        assert fig is not None

    def test_legend_frame_and_ticks_combined(self):
        """Frame, ticks, and ticks_length should all work together."""
        p = self._make_continuous_plot() + theme(
            legend_frame=element_rect(color="grey", size=0.5),
            legend_ticks=element_line(color="black"),
            legend_ticks_length=5.0,
            legend_axis_line=element_line(color="black", size=0.5),
        )
        fig = render(p)
        assert fig is not None


class TestPolarThemeFields:
    """Tests for polar axis theme field wiring."""

    def _make_polar_plot(self):
        from plotten.coords import coord_polar

        df = pd.DataFrame({"cat": ["a", "b", "c", "d"], "val": [3, 1, 2, 4]})
        return ggplot(df, aes(x="cat", y="val")) + geom_point() + coord_polar()

    def test_axis_text_theta_styling(self):
        """axis_text_theta should style theta tick labels."""
        p = self._make_polar_plot() + theme(axis_text_theta=element_text(color="red", size=14))
        fig = render(p)
        assert fig is not None

    def test_axis_text_theta_blank(self):
        """axis_text_theta=element_blank() should suppress theta labels."""
        p = self._make_polar_plot() + theme(axis_text_theta=element_blank())
        fig = render(p)
        assert fig is not None

    def test_axis_text_r_styling(self):
        """axis_text_r should style radial tick labels."""
        p = self._make_polar_plot() + theme(axis_text_r=element_text(color="blue", size=10))
        fig = render(p)
        assert fig is not None

    def test_axis_text_r_blank(self):
        """axis_text_r=element_blank() should suppress radial labels."""
        p = self._make_polar_plot() + theme(axis_text_r=element_blank())
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_theta_styling(self):
        """axis_ticks_theta should style theta tick marks."""
        p = self._make_polar_plot() + theme(axis_ticks_theta=element_line(color="red", size=2.0))
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_theta_blank(self):
        """axis_ticks_theta=element_blank() should suppress theta ticks."""
        p = self._make_polar_plot() + theme(axis_ticks_theta=element_blank())
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_r_styling(self):
        """axis_ticks_r should style radial tick marks."""
        p = self._make_polar_plot() + theme(axis_ticks_r=element_line(color="blue", size=1.5))
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_length_theta(self):
        """axis_ticks_length_theta should control theta tick length."""
        p = self._make_polar_plot() + theme(axis_ticks_length_theta=8.0)
        fig = render(p)
        assert fig is not None

    def test_axis_ticks_length_r(self):
        """axis_ticks_length_r should control radial tick length."""
        p = self._make_polar_plot() + theme(axis_ticks_length_r=6.0)
        fig = render(p)
        assert fig is not None

    def test_axis_line_theta_styling(self):
        """axis_line_theta should style the outer circle spine."""
        p = self._make_polar_plot() + theme(axis_line_theta=element_line(color="black", size=2.0))
        fig = render(p)
        assert fig is not None

    def test_axis_line_theta_blank(self):
        """axis_line_theta=element_blank() should hide the outer circle."""
        p = self._make_polar_plot() + theme(axis_line_theta=element_blank())
        fig = render(p)
        assert fig is not None

    def test_axis_line_r_styling(self):
        """axis_line_r should style the radial spines."""
        p = self._make_polar_plot() + theme(axis_line_r=element_line(color="grey", size=1.0))
        fig = render(p)
        assert fig is not None

    def test_axis_line_r_blank(self):
        """axis_line_r=element_blank() should hide radial spines."""
        p = self._make_polar_plot() + theme(axis_line_r=element_blank())
        fig = render(p)
        assert fig is not None

    def test_combined_polar_styling(self):
        """Multiple polar theme fields should work together."""
        p = self._make_polar_plot() + theme(
            axis_text_theta=element_text(color="white", size=12),
            axis_text_r=element_blank(),
            axis_ticks_theta=element_line(color="grey"),
            axis_ticks_r=element_blank(),
            axis_line_theta=element_line(color="white", size=1.5),
            axis_line_r=element_blank(),
            axis_ticks_length_theta=4.0,
        )
        fig = render(p)
        assert fig is not None


class TestLegendBoxLayout:
    """legend_box, legend_box_spacing, legend_box_background, legend_row_major, legend_position_inside."""

    @staticmethod
    def _make_multi_legend_plot():
        from plotten import geom_line, scale_color_discrete, scale_linetype_discrete

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
                "y": [1.0, 3.0, 2.0, 2.0, 1.0, 3.0],
                "g": ["a", "a", "a", "b", "b", "b"],
                "lt": ["solid", "solid", "solid", "dashed", "dashed", "dashed"],
            }
        )
        return (
            ggplot(df, aes(x="x", y="y", color="g", linetype="lt"))
            + geom_line()
            + scale_color_discrete()
            + scale_linetype_discrete()
        )

    def test_legend_box_vertical_default(self):
        """Default legend_box is vertical (None) — should render normally."""
        p = self._make_multi_legend_plot()
        fig = render(p)
        assert fig is not None

    def test_legend_box_horizontal(self):
        """legend_box='horizontal' should stack legend groups side by side."""
        p = self._make_multi_legend_plot() + theme(legend_box="horizontal")
        fig = render(p)
        assert fig is not None

    def test_legend_box_spacing(self):
        """legend_box_spacing should control gap between legend groups."""
        p = self._make_multi_legend_plot() + theme(legend_box_spacing=0.05)
        fig = render(p)
        assert fig is not None

    def test_legend_box_background(self):
        """legend_box_background should draw a background behind all legends."""
        p = self._make_multi_legend_plot() + theme(
            legend_box_background=element_rect(fill="lightyellow", color="grey")
        )
        fig = render(p)
        # Check that a patch was added to the figure
        assert len(fig.patches) > 0

    def test_legend_box_horizontal_with_spacing(self):
        """Horizontal box with custom spacing."""
        p = self._make_multi_legend_plot() + theme(
            legend_box="horizontal",
            legend_box_spacing=0.08,
        )
        fig = render(p)
        assert fig is not None

    def test_legend_row_major(self):
        """legend_row_major should reorder entries in row-first order."""
        from plotten import guide_legend, guides, scale_color_discrete

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0],
                "y": [1.0, 2.0, 3.0, 4.0],
                "g": ["a", "b", "c", "d"],
            }
        )
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + guides(color=guide_legend(n_cols=2))
            + theme(legend_row_major=True)
        )
        fig = render(p)
        assert fig is not None

    def test_legend_position_inside(self):
        """legend_position_inside should override position to axes-relative coords."""
        from plotten import scale_color_discrete

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
                "g": ["a", "b", "c"],
            }
        )
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_position_inside=(0.8, 0.8))
        )
        fig = render(p)
        assert fig is not None

    def test_legend_position_inside_overrides_position(self):
        """legend_position_inside takes precedence over legend_position."""
        from plotten import scale_color_discrete

        df = pl.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
                "g": ["a", "b", "c"],
            }
        )
        p = (
            ggplot(df, aes(x="x", y="y", color="g"))
            + geom_point()
            + scale_color_discrete()
            + theme(legend_position="left", legend_position_inside=(0.5, 0.5))
        )
        fig = render(p)
        assert fig is not None


class TestLegendTextPosition:
    """legend_text_position controls text placement relative to swatch."""

    @pytest.mark.parametrize("pos", ["right", "left", "top", "bottom"])
    def test_text_position(self, pos):
        p = _make_legend_plot() + theme(legend_text_position=pos)
        fig = render(p)
        assert fig is not None


class TestLegendTitlePosition:
    """legend_title_position controls title placement in legend."""

    @pytest.mark.parametrize("pos", ["top", "bottom", "left", "right"])
    def test_title_position(self, pos):
        p = _make_legend_plot() + theme(legend_title_position=pos)
        fig = render(p)
        assert fig is not None


class TestLegendBoxJustAndMargin:
    """legend_box_just and legend_box_margin positioning."""

    @pytest.mark.parametrize("just", ["left", "right", "top", "bottom"])
    def test_box_just(self, just):
        p = _make_legend_plot() + theme(legend_box_just=just)
        fig = render(p)
        assert fig is not None

    def test_box_margin(self):
        p = _make_legend_plot() + theme(legend_box_margin=(10, 5, 10, 5))
        fig = render(p)
        assert fig is not None


class TestStripMiscFields:
    """strip_clip, strip_switch_pad_grid, strip_switch_pad_wrap, spacing."""

    def test_strip_clip_off(self):
        from plotten.facets import facet_wrap

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g")
            + theme(strip_clip="off")
        )
        fig = render(p)
        assert fig is not None

    def test_strip_switch_pad_wrap(self):
        from plotten.facets import facet_wrap

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_wrap("g", strip_position="bottom")
            + theme(strip_switch_pad_wrap=10.0)
        )
        fig = render(p)
        assert fig is not None

    def test_strip_switch_pad_grid(self):
        from plotten.facets import facet_grid

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + facet_grid(cols="g")
            + theme(strip_switch_pad_grid=12.0)
        )
        fig = render(p)
        assert fig is not None

    def test_global_spacing(self):
        from plotten.facets import facet_wrap

        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 1, 3], "g": ["a", "a", "b", "b"]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + facet_wrap("g") + theme(spacing=2.0)
        fig = render(p)
        assert fig is not None

    def test_global_spacing_affects_panel_gap(self):
        """spacing=0.5 should halve the effective panel spacing."""
        t = Theme(panel_spacing=0.1, spacing=0.5)
        # spacing is a multiplier applied at render time, not stored as derived
        assert t.spacing == 0.5
        assert t.panel_spacing == 0.1


class TestThemeDiff:
    def test_identical_themes_empty(self):
        from plotten.themes import theme_diff

        assert theme_diff(Theme(), Theme()) == []

    def test_detects_scalar_difference(self):
        from plotten.themes import theme_diff

        a = Theme(base_size=12)
        b = Theme(base_size=16)
        diffs = theme_diff(a, b)
        field_names = [d.field for d in diffs]
        assert "base_size" in field_names
        entry = next(d for d in diffs if d.field == "base_size")
        assert entry.a == 12
        assert entry.b == 16

    def test_detects_element_difference(self):
        from plotten.themes import theme_diff

        a = Theme(axis_title=ElementText(size=14))
        b = Theme(axis_title=ElementText(size=18))
        diffs = theme_diff(a, b)
        assert any(d.field == "axis_title" for d in diffs)

    def test_builtin_themes_differ(self):
        from plotten.themes import theme_diff

        diffs = theme_diff(theme_minimal(), theme_dark())
        assert len(diffs) > 0
        field_names = [d.field for d in diffs]
        assert "background" in field_names

    def test_entry_repr(self):
        from plotten.themes import ThemeDiffEntry

        e = ThemeDiffEntry(field="background", a="#fff", b="#000")
        r = repr(e)
        assert "background" in r
        assert "#fff" in r
        assert "#000" in r

    def test_declaration_order(self):
        from plotten.themes import theme_diff

        a = Theme(background="#fff", font_family="serif")
        b = Theme(background="#000", font_family="monospace")
        diffs = theme_diff(a, b)
        field_names = [d.field for d in diffs]
        # font_family is declared before background in Theme? No — let's just
        # verify order matches dataclass field order
        from dataclasses import fields as dc_fields

        all_fields = [f.name for f in dc_fields(Theme)]
        indices = [all_fields.index(n) for n in field_names]
        assert indices == sorted(indices)


class TestThemePreview:
    def test_returns_plot(self):
        from plotten import Plot
        from plotten.themes import theme_preview

        p = theme_preview(Theme())
        assert isinstance(p, Plot)

    def test_renders_default(self):
        from plotten.themes import theme_preview

        fig = render(theme_preview(Theme()))
        assert fig is not None

    def test_renders_builtin_themes(self):
        from plotten.themes import theme_preview

        for factory in [theme_dark, theme_minimal, theme_classic, theme_bw]:
            fig = render(theme_preview(factory()))
            assert fig is not None

    def test_has_facets(self):
        from plotten.themes import theme_preview

        fig = render(theme_preview(Theme()))
        # 2 facet panels + 1 for the legend
        assert len(fig.axes) >= 2
