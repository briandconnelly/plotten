"""Tests for secondary axes (sec_axis, dup_axis)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import pandas as pd

from plotten import Aes, dup_axis, geom_line, ggplot, scale_y_continuous, sec_axis
from plotten._render._mpl import render
from plotten.scales._sec_axis import SecAxis


class TestSecAxis:
    def test_sec_axis_creation(self):
        sa = sec_axis(trans=lambda x: x * 1.8 + 32, inverse=lambda x: (x - 32) / 1.8)
        assert isinstance(sa, SecAxis)
        assert sa.name is None

    def test_sec_axis_with_name(self):
        sa = sec_axis(
            trans=lambda x: x * 1.8 + 32,
            inverse=lambda x: (x - 32) / 1.8,
            name="Fahrenheit",
        )
        assert sa.name == "Fahrenheit"

    def test_dup_axis(self):
        sa = dup_axis()
        assert isinstance(sa, SecAxis)
        # Identity transform
        assert sa.trans(5) == 5
        assert sa.inverse(5) == 5

    def test_dup_axis_with_name(self):
        sa = dup_axis(name="Also Y")
        assert sa.name == "Also Y"

    def test_sec_axis_transforms(self):
        sa = sec_axis(
            trans=lambda x: x * 2,
            inverse=lambda x: x / 2,
        )
        assert sa.trans(10) == 20
        assert sa.inverse(20) == 10

    def test_sec_axis_breaks_and_labels(self):
        sa = sec_axis(
            trans=lambda x: x,
            inverse=lambda x: x,
            breaks=[0, 50, 100],
            labels=["low", "mid", "high"],
        )
        assert sa.breaks == [0, 50, 100]
        assert sa.labels == ["low", "mid", "high"]

    def _find_sec_axis(self, ax):
        """Find SecondaryAxis child of an axes."""
        from matplotlib.axes._secondary_axes import SecondaryAxis

        for child in ax.get_children():
            if isinstance(child, SecondaryAxis):
                return child
        return None

    def test_sec_axis_rendering_y(self):
        df = pd.DataFrame({"x": range(10), "y": range(10)})
        sa = sec_axis(
            trans=lambda x: x * 1.8 + 32,
            inverse=lambda x: (x - 32) / 1.8,
            name="Fahrenheit",
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_line() + scale_y_continuous(sec_axis=sa)
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is not None
        assert sec.get_ylabel() == "Fahrenheit"

    def test_sec_axis_rendering_with_dup(self):
        df = pd.DataFrame({"x": range(5), "y": range(5)})
        p = (
            ggplot(df, Aes(x="x", y="y"))
            + geom_line()
            + scale_y_continuous(sec_axis=dup_axis(name="Copy"))
        )
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is not None
        assert sec.get_ylabel() == "Copy"

    def test_no_sec_axis_by_default(self):
        df = pd.DataFrame({"x": range(5), "y": range(5)})
        p = ggplot(df, Aes(x="x", y="y")) + geom_line()
        fig = render(p)
        ax = fig.axes[0]
        sec = self._find_sec_axis(ax)
        assert sec is None
