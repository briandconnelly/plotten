"""Tests for Phase 4: Annotations Overhaul (4A-4C)."""

import matplotlib.pyplot as plt
import polars as pl
import pytest

from plotten import aes, annotate, arrow, geom_point, geom_segment, ggplot
from plotten._arrow import _ARROW_STYLES, Arrow
from plotten._render._mpl import render

# --- 4A: Configurable arrow styles ---


class TestArrowStyles:
    def test_arrow_default(self):
        a = arrow()
        assert a.style == "open"
        assert a.size == 1.0

    def test_arrow_closed(self):
        a = arrow(style="closed")
        style_str = a.to_arrowstyle()
        assert "-|>" in style_str

    def test_arrow_invalid_style(self):
        with pytest.raises(ValueError, match="Unknown arrow style"):
            arrow(style="nonexistent")

    def test_all_styles_valid(self):
        for style in _ARROW_STYLES:
            a = Arrow(style=style)
            result = a.to_arrowstyle()
            assert isinstance(result, str)

    def test_arrow_true_backward_compat(self):
        """arrow=True should still work in geom_segment."""
        df = pl.DataFrame(
            {
                "x": [0.0],
                "y": [0.0],
                "xend": [1.0],
                "yend": [1.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment(arrow=True)
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_arrow_object_in_segment(self):
        """Arrow object should work in geom_segment."""
        df = pl.DataFrame(
            {
                "x": [0.0],
                "y": [0.0],
                "xend": [1.0],
                "yend": [1.0],
            }
        )
        plot = ggplot(df, aes(x="x", y="y", xend="xend", yend="yend")) + geom_segment(
            arrow=arrow(style="closed", size=1.5)
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_arrow_in_annotate_segment(self):
        """Arrow object should work in annotate("segment")."""
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("segment", x=1, y=1, xend=2, yend=2, arrow=arrow())
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 4B: Curved arrows and text boxes ---


class TestCurvedArrowsAndTextBoxes:
    def test_annotate_curve(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("curve", x=1, y=1, xend=3, yend=3, curvature=0.5, arrow=True)
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_annotate_curve_with_arrow_obj(self):
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("curve", x=1, y=1, xend=2, yend=2, arrow=arrow(style="closed"))
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_annotate_text_box(self):
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("text", x=1.5, y=1.5, label="Hello", box_fill="yellow", box_color="black")
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_annotate_text_box_with_pad(self):
        df = pl.DataFrame({"x": [1, 2], "y": [1, 2]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("text", x=1.5, y=1.5, label="Padded", box_fill="white", box_pad=0.5)
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)


# --- 4C: Bracket annotations ---


class TestBracketAnnotations:
    def test_annotate_bracket(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("bracket", xmin=1, xmax=3, y=3.5, label="Group A")
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_annotate_bracket_down(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("bracket", xmin=1, xmax=2, y=0.5, direction="down")
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_annotate_bracket_no_label(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
        plot = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("bracket", xmin=1, xmax=3, y=3.5)
        )
        fig = render(plot)
        assert fig is not None
        plt.close(fig)

    def test_invalid_annotation_type(self):
        with pytest.raises(ValueError, match="Unknown annotation geom_type"):
            annotate("unknown_type", x=1, y=1)
