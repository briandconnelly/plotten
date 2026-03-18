"""Tests for v0.8.0 theme element system."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import polars as pl

from plotten import (
    Theme,
    aes,
    element_blank,
    element_line,
    element_rect,
    element_text,
    geom_point,
    ggplot,
    labs,
)
from plotten._render._mpl import render
from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, ElementText

matplotlib.use("Agg")


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
        import pytest

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
