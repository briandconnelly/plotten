"""Tests for geom_text_repel and geom_label_repel."""

from __future__ import annotations

import tempfile

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from plotten import Plot, aes, geom_label_repel, geom_point, geom_text_repel, ggplot, ggsave
from plotten.geoms._repel import GeomLabelRepel, GeomTextRepel, _box_overlap

matplotlib.use("Agg")

import numpy as np


class TestBoxOverlap:
    def test_no_overlap(self):
        pos1 = np.array([0.0, 0.0])
        size1 = np.array([10.0, 10.0])
        pos2 = np.array([20.0, 20.0])
        size2 = np.array([10.0, 10.0])
        assert _box_overlap(pos1, size1, pos2, size2) == 0.0

    def test_full_overlap(self):
        pos1 = np.array([5.0, 5.0])
        size1 = np.array([10.0, 10.0])
        pos2 = np.array([5.0, 5.0])
        size2 = np.array([10.0, 10.0])
        assert _box_overlap(pos1, size1, pos2, size2) == pytest.approx(100.0)

    def test_partial_overlap(self):
        pos1 = np.array([0.0, 0.0])
        size1 = np.array([10.0, 10.0])
        pos2 = np.array([5.0, 0.0])
        size2 = np.array([10.0, 10.0])
        overlap = _box_overlap(pos1, size1, pos2, size2)
        assert overlap > 0
        assert overlap < 100


class TestGeomClasses:
    def test_text_repel_required_aes(self):
        geom = GeomTextRepel()
        assert geom.required_aes == frozenset({"x", "y", "label"})

    def test_label_repel_required_aes(self):
        geom = GeomLabelRepel()
        assert geom.required_aes == frozenset({"x", "y", "label"})

    def test_text_repel_default_stat(self):
        from plotten.stats._identity import StatIdentity

        geom = GeomTextRepel()
        assert isinstance(geom.default_stat(), StatIdentity)

    def test_text_repel_seed_deterministic(self):
        geom1 = GeomTextRepel(seed=42)
        geom2 = GeomTextRepel(seed=42)
        assert geom1.seed == geom2.seed == 42


def _render_plot(p: Plot) -> None:
    """Helper to render a plot to a temp file."""
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        ggsave(p, f.name)
    plt.close("all")


class TestRepelIntegration:
    def test_text_repel_renders(self):
        """geom_text_repel should render without error."""
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5],
                "y": [1, 2, 3, 4, 5],
                "lab": ["a", "b", "c", "d", "e"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_text_repel()
        _render_plot(p)

    def test_label_repel_renders(self):
        """geom_label_repel should render with bbox."""
        df = pd.DataFrame(
            {
                "x": [1, 2, 3],
                "y": [1, 2, 3],
                "lab": ["alpha", "beta", "gamma"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_label_repel()
        _render_plot(p)

    def test_text_repel_with_point(self):
        """geom_text_repel combined with geom_point."""
        df = pd.DataFrame(
            {
                "x": [1, 1.1, 1.2],
                "y": [1, 1.05, 1.1],
                "lab": ["A", "B", "C"],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + geom_text_repel(label="lab")
        _render_plot(p)

    def test_text_repel_nudge(self):
        """nudge_x and nudge_y parameters should be accepted."""
        df = pd.DataFrame({"x": [1], "y": [1], "lab": ["test"]})
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_text_repel(nudge_x=0.5, nudge_y=0.5)
        _render_plot(p)

    def test_single_label_no_error(self):
        """Single label should not error."""
        df = pd.DataFrame({"x": [5], "y": [5], "lab": ["only"]})
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_text_repel()
        _render_plot(p)

    def test_overlapping_labels_renders(self):
        """Labels at the same point should render without error."""
        df = pd.DataFrame(
            {
                "x": [1.0, 1.0, 1.0],
                "y": [1.0, 1.0, 1.0],
                "lab": ["A", "B", "C"],
            }
        )
        p = ggplot(df, aes(x="x", y="y", label="lab")) + geom_text_repel(seed=42)
        _render_plot(p)

    def test_repel_factory_returns_layer(self):
        """Factory function should return a Layer."""
        from plotten._layer import Layer

        layer = geom_text_repel()
        assert isinstance(layer, Layer)

    def test_label_repel_factory_returns_layer(self):
        from plotten._layer import Layer

        layer = geom_label_repel(fill="#ffffcc", label_alpha=0.9)
        assert isinstance(layer, Layer)
        assert isinstance(layer.geom, GeomLabelRepel)
        assert layer.geom.fill == "#ffffcc"
        assert layer.geom.label_alpha == 0.9
