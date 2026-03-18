"""Tests for v0.5 save improvements."""

from __future__ import annotations

import os

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import aes, geom_point, ggplot


class TestSave:
    @pytest.fixture
    def simple_plot(self):
        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        return ggplot(df, aes(x="x", y="y")) + geom_point()

    def test_save_default(self, simple_plot, tmp_path):
        path = str(tmp_path / "test.png")
        simple_plot.save(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_width_height_inches(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_wh.png")
        simple_plot.save(path, width=10, height=6, units="in")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_cm(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_cm.png")
        simple_plot.save(path, width=25, height=15, units="cm")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_mm(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_mm.png")
        simple_plot.save(path, width=250, height=150, units="mm")
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_with_px(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_px.png")
        simple_plot.save(path, width=800, height=600, units="px", dpi=100)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_backward_compat(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_compat.png")
        simple_plot.save(path, dpi=72)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_save_width_only(self, simple_plot, tmp_path):
        path = str(tmp_path / "test_w.png")
        simple_plot.save(path, width=12)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
