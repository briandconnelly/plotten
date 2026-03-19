"""Tests for theme() convenience function (1A)."""

import pytest

from plotten.themes import Theme, theme, theme_minimal


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
