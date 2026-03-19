"""Tests for v0.11.0 theme additions."""

import pandas as pd
import pytest

from plotten import (
    Aes,
    Theme,
    geom_point,
    ggplot,
    theme,
    theme_dark,
    theme_get,
    theme_gray,
    theme_grey,
    theme_set,
    theme_update,
)
from plotten._render._mpl import render


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
