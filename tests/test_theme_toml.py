"""Tests for TOML theme serialization and deserialization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from plotten import ConfigError
from plotten.themes import (
    ElementBlank,
    ElementLine,
    ElementRect,
    ElementText,
    Margin,
    Rel,
    Theme,
    theme_from_toml,
    theme_to_toml,
)


@pytest.fixture
def tmp_toml(tmp_path: Path):
    """Helper to write a TOML string and return the path."""

    def _write(content: str) -> Path:
        p = tmp_path / "theme.toml"
        p.write_text(content)
        return p

    return _write


# ---------------------------------------------------------------------------
# theme_from_toml — scalar fields
# ---------------------------------------------------------------------------


class TestFromTomlScalars:
    def test_basic_scalars(self, tmp_toml):
        p = tmp_toml('base_size = 14\nfont_family = "serif"\nbackground = "#fafafa"')
        t = theme_from_toml(p)
        assert t.base_size == 14
        assert t.font_family == "serif"
        assert t.background == "#fafafa"

    def test_boolean_fields(self, tmp_toml):
        p = tmp_toml("grid_major_x = false\naxis_line_y = true")
        t = theme_from_toml(p)
        assert t.grid_major_x is False
        assert t.axis_line_y is True

    def test_tuple_from_array(self, tmp_toml):
        p = tmp_toml("legend_position = [0.8, 0.2]")
        t = theme_from_toml(p)
        assert t.legend_position == (0.8, 0.2)

    def test_string_legend_position(self, tmp_toml):
        p = tmp_toml('legend_position = "bottom"')
        t = theme_from_toml(p)
        assert t.legend_position == "bottom"

    def test_panel_widths_tuple(self, tmp_toml):
        p = tmp_toml("panel_widths = [1.0, 2.0, 1.0]")
        t = theme_from_toml(p)
        assert t.panel_widths == (1.0, 2.0, 1.0)


# ---------------------------------------------------------------------------
# theme_from_toml — element fields
# ---------------------------------------------------------------------------


class TestFromTomlElements:
    def test_element_text(self, tmp_toml):
        p = tmp_toml('[axis_title]\nsize = 14\ncolor = "#333"')
        t = theme_from_toml(p)
        assert isinstance(t.axis_title, ElementText)
        assert t.axis_title.size == 14
        assert t.axis_title.color == "#333"

    def test_element_line(self, tmp_toml):
        p = tmp_toml('[panel_grid]\ncolor = "#ddd"\nsize = 0.5')
        t = theme_from_toml(p)
        assert isinstance(t.panel_grid, ElementLine)
        assert t.panel_grid.color == "#ddd"
        assert t.panel_grid.size == 0.5

    def test_element_rect(self, tmp_toml):
        p = tmp_toml('[panel_border]\nfill = "#fff"\ncolor = "#000"\nsize = 1.0')
        t = theme_from_toml(p)
        assert isinstance(t.panel_border, ElementRect)
        assert t.panel_border.fill == "#fff"
        assert t.panel_border.color == "#000"

    def test_element_blank(self, tmp_toml):
        p = tmp_toml("[axis_ticks]\nblank = true")
        t = theme_from_toml(p)
        assert isinstance(t.axis_ticks, ElementBlank)

    def test_blank_false_is_not_blank(self, tmp_toml):
        p = tmp_toml('[axis_title]\nblank = false\nsize = 14\ncolor = "#333"')
        t = theme_from_toml(p)
        assert isinstance(t.axis_title, ElementText)
        assert t.axis_title.size == 14

    def test_rel_size(self, tmp_toml):
        p = tmp_toml("[plot_caption]\nsize = { rel = 0.8 }")
        t = theme_from_toml(p)
        assert isinstance(t.plot_caption, ElementText)
        assert isinstance(t.plot_caption.size, Rel)
        assert t.plot_caption.size.factor == 0.8

    def test_str_or_element_rect_as_string(self, tmp_toml):
        p = tmp_toml('panel_background = "#f0f0f0"')
        t = theme_from_toml(p)
        assert t.panel_background == "#f0f0f0"

    def test_str_or_element_rect_as_table(self, tmp_toml):
        p = tmp_toml('[panel_background]\nfill = "#eee"\ncolor = "#999"\nsize = 0.5')
        t = theme_from_toml(p)
        assert isinstance(t.panel_background, ElementRect)
        assert t.panel_background.fill == "#eee"


# ---------------------------------------------------------------------------
# theme_from_toml — margin fields
# ---------------------------------------------------------------------------


class TestFromTomlMargin:
    def test_margin_as_number(self, tmp_toml):
        p = tmp_toml("legend_margin = 12.0")
        t = theme_from_toml(p)
        assert t.legend_margin == 12.0

    def test_margin_as_array(self, tmp_toml):
        p = tmp_toml("plot_margin = [10.0, 5.0, 10.0, 5.0]")
        t = theme_from_toml(p)
        assert t.plot_margin == (10.0, 5.0, 10.0, 5.0)

    def test_margin_as_table(self, tmp_toml):
        p = tmp_toml("[plot_margin]\ntop = 10\nright = 5\nbottom = 10\nleft = 5")
        t = theme_from_toml(p)
        assert isinstance(t.plot_margin, Margin)
        assert t.plot_margin.top == 10
        assert t.plot_margin.right == 5

    def test_margin_with_unit(self, tmp_toml):
        p = tmp_toml(
            '[plot_margin]\ntop = 1.0\nright = 0.5\nbottom = 1.0\nleft = 0.5\nunit = "cm"'
        )
        t = theme_from_toml(p)
        assert isinstance(t.plot_margin, Margin)
        assert t.plot_margin.unit == "cm"


# ---------------------------------------------------------------------------
# theme_from_toml — base theme inheritance
# ---------------------------------------------------------------------------


class TestFromTomlBase:
    def test_base_minimal(self, tmp_toml):
        p = tmp_toml('base = "minimal"\nbase_size = 14')
        t = theme_from_toml(p)
        assert t.base_size == 14
        assert t.panel_background == "none"  # from theme_minimal
        assert t.complete is True  # complete themes stay complete

    def test_base_dark(self, tmp_toml):
        p = tmp_toml('base = "dark"\nfont_family = "monospace"')
        t = theme_from_toml(p)
        assert t.font_family == "monospace"
        assert t.background == "#2d2d2d"  # from theme_dark

    def test_unknown_base_raises(self, tmp_toml):
        p = tmp_toml('base = "nonexistent"')
        with pytest.raises(ConfigError, match="Unknown base theme"):
            theme_from_toml(p)


# ---------------------------------------------------------------------------
# theme_from_toml — error handling
# ---------------------------------------------------------------------------


class TestFromTomlErrors:
    def test_unknown_property(self, tmp_toml):
        p = tmp_toml("not_a_field = 42")
        with pytest.raises(ConfigError, match="Unknown theme properties"):
            theme_from_toml(p)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            theme_from_toml("/nonexistent/path/theme.toml")


# ---------------------------------------------------------------------------
# theme_to_toml
# ---------------------------------------------------------------------------


class TestToToml:
    def test_round_trip_scalars(self, tmp_path):
        original = Theme(base_size=14, font_family="serif", background="#fafafa")
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert loaded.base_size == 14
        assert loaded.font_family == "serif"
        assert loaded.background == "#fafafa"

    def test_round_trip_element_text(self, tmp_path):
        original = Theme(axis_title=ElementText(size=14, color="#333"))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.axis_title, ElementText)
        assert loaded.axis_title.size == 14
        assert loaded.axis_title.color == "#333"

    def test_round_trip_element_blank(self, tmp_path):
        original = Theme(axis_ticks=ElementBlank())
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.axis_ticks, ElementBlank)

    def test_round_trip_rel(self, tmp_path):
        original = Theme(plot_caption=ElementText(size=Rel(1.2)))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.plot_caption, ElementText)
        assert isinstance(loaded.plot_caption.size, Rel)
        assert loaded.plot_caption.size.factor == 1.2

    def test_round_trip_margin(self, tmp_path):
        m = Margin(top=10, right=5, bottom=10, left=5, unit="cm")
        original = Theme(plot_margin=m)
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.plot_margin, Margin)
        assert loaded.plot_margin.top == 10
        assert loaded.plot_margin.unit == "cm"

    def test_round_trip_tuple(self, tmp_path):
        original = Theme(legend_position=(0.8, 0.2))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert loaded.legend_position == (0.8, 0.2)

    def test_skips_defaults(self, tmp_path):
        original = Theme()  # all defaults
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        content = p.read_text()
        # Should be minimal — only the non-default plot_caption
        assert "base_size" not in content
        assert "font_family" not in content

    def test_complete_emits_all_fields(self, tmp_path):
        original = Theme()
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        content = p.read_text()
        # Complete mode should include default scalar fields
        assert "font_family" in content
        assert "background" in content
        assert "grid_color" in content
        assert "grid_major_x" in content

    def test_complete_shows_none_scalars_commented(self, tmp_path):
        original = Theme()
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        content = p.read_text()
        # None scalar fields should appear as commented-out lines
        assert "# base_size =" in content
        assert "# axis_title_x_size =" in content

    def test_complete_shows_none_elements_commented(self, tmp_path):
        original = Theme()
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        content = p.read_text()
        # None element fields should appear as commented-out tables
        assert "# [axis_title]" in content
        assert "# size =" in content
        assert "# color =" in content
        assert "# blank = false" in content

    def test_complete_shows_none_margin_commented(self, tmp_path):
        original = Theme()
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        content = p.read_text()
        assert "# [plot_margin]" in content
        assert "# top =" in content

    def test_complete_is_valid_toml(self, tmp_path):
        """Complete output with comments should still parse as valid TOML."""
        import tomllib

        original = Theme(base_size=14, axis_title=ElementText(size=14, color="#333"))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        with p.open("rb") as f:
            data = tomllib.load(f)
        assert data["base_size"] == 14
        assert data["axis_title"]["size"] == 14

    def test_complete_round_trips(self, tmp_path):
        from plotten.themes import theme_dark

        original = theme_dark()
        p = tmp_path / "out.toml"
        theme_to_toml(original, p, complete=True)
        loaded = theme_from_toml(p)
        assert loaded.background == original.background
        assert loaded.title_color == original.title_color
        assert loaded.font_family == original.font_family

    def test_round_trip_element_line(self, tmp_path):
        original = Theme(panel_grid=ElementLine(color="#ddd", size=0.5))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.panel_grid, ElementLine)
        assert loaded.panel_grid.color == "#ddd"
        assert loaded.panel_grid.size == 0.5

    def test_round_trip_element_rect(self, tmp_path):
        original = Theme(legend_key=ElementRect(fill="#fff", color="#ccc", size=0.5))
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        loaded = theme_from_toml(p)
        assert isinstance(loaded.legend_key, ElementRect)
        assert loaded.legend_key.fill == "#fff"

    def test_output_is_valid_toml(self, tmp_path):
        """The output should parse without errors."""
        original = Theme(
            base_size=14,
            font_family="serif",
            axis_title=ElementText(size=14, color="#333"),
            axis_ticks=ElementBlank(),
            plot_caption=ElementText(size=Rel(0.8)),
            plot_margin=Margin(top=10, right=5, bottom=10, left=5, unit="cm"),
            legend_position=(0.8, 0.2),
            grid_major_x=False,
        )
        p = tmp_path / "out.toml"
        theme_to_toml(original, p)
        # Should parse without error
        import tomllib

        with p.open("rb") as f:
            data = tomllib.load(f)
        assert isinstance(data, dict)
