"""Tests for v1.1.0 Phase 1 theme gallery: theme_538, theme_economist, theme_tufte, theme_seaborn."""

from pathlib import Path

import pandas as pd
import pytest

from plotten import Aes, Theme, geom_point, ggplot, ggsave
from plotten.themes import theme_538, theme_economist, theme_seaborn, theme_tufte


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
