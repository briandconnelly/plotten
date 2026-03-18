"""Tests for v0.5 annotate()."""

from __future__ import annotations

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import aes, annotate, geom_point, ggplot


class TestAnnotateText:
    def test_text_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("text", x=2, y=5, label="Hello")
        )
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_text_does_not_interfere(self):
        df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
        p1 = ggplot(df, aes(x="x", y="y")) + geom_point()
        p2 = p1 + annotate("text", x=1, y=3, label="Note")
        # Both should render without error
        assert len(p1._repr_png_()) > 0
        assert len(p2._repr_png_()) > 0


class TestAnnotateRect:
    def test_rect_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("rect", xmin=1.5, xmax=2.5, ymin=4.5, ymax=5.5, alpha=0.2)
        )
        fig = p._repr_png_()
        assert len(fig) > 0


class TestAnnotateSegment:
    def test_segment_renders(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + annotate("segment", x=1, y=4, xend=3, yend=6, color="red")
        )
        fig = p._repr_png_()
        assert len(fig) > 0


class TestAnnotateInvalid:
    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown annotation"):
            annotate("bogus", x=1, y=2)
