"""Tests for v1.1.0 Phase 4 rendering improvements: watermark and facet_wrap dir."""

from pathlib import Path

import pandas as pd
import pytest

from plotten import Aes, facet_wrap, geom_point, ggplot, watermark
from plotten._watermark import Watermark
from plotten.facets._wrap import FacetWrap

# --- Watermark ---


class TestWatermark:
    def test_factory_defaults(self):
        wm = watermark("DRAFT")
        assert isinstance(wm, Watermark)
        assert wm.text == "DRAFT"
        assert wm.alpha == 0.1
        assert wm.fontsize == 50
        assert wm.rotation == 30
        assert wm.color == "#cccccc"

    def test_factory_custom(self):
        wm = watermark("CONFIDENTIAL", alpha=0.2, fontsize=80, rotation=45, color="red")
        assert wm.text == "CONFIDENTIAL"
        assert wm.alpha == 0.2
        assert wm.fontsize == 80
        assert wm.rotation == 45
        assert wm.color == "red"

    def test_frozen(self):
        wm = watermark("DRAFT")
        with pytest.raises(AttributeError):
            wm.text = "OTHER"  # type: ignore[misc]

    def test_add_to_plot(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + watermark("DRAFT")
        assert p._watermark is not None
        assert p._watermark.text == "DRAFT"

    def test_watermark_renders(self, tmp_path: Path):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + watermark("DRAFT")
        out = tmp_path / "watermark.png"
        p.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_no_watermark_by_default(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point()
        assert p._watermark is None


# --- FacetWrap dir ---


class TestFacetWrapDir:
    def test_default_dir_is_h(self):
        fw = facet_wrap("group")
        assert fw.dir == "h"

    def test_dir_v(self):
        fw = facet_wrap("group", dir="v")
        assert fw.dir == "v"

    def test_panel_position_h(self):
        fw = FacetWrap(facets="g", ncol=3, dir="h")
        nrow, ncol = fw.layout(5)
        # h: row-major => idx 0->(0,0), 1->(0,1), 2->(0,2), 3->(1,0), 4->(1,1)
        assert fw.panel_position(0, nrow, ncol) == (0, 0)
        assert fw.panel_position(1, nrow, ncol) == (0, 1)
        assert fw.panel_position(2, nrow, ncol) == (0, 2)
        assert fw.panel_position(3, nrow, ncol) == (1, 0)
        assert fw.panel_position(4, nrow, ncol) == (1, 1)

    def test_panel_position_v(self):
        fw = FacetWrap(facets="g", ncol=3, nrow=2, dir="v")
        nrow, ncol = fw.layout(5)
        # v: column-major => idx 0->(0,0), 1->(1,0), 2->(0,1), 3->(1,1), 4->(0,2)
        assert fw.panel_position(0, nrow, ncol) == (0, 0)
        assert fw.panel_position(1, nrow, ncol) == (1, 0)
        assert fw.panel_position(2, nrow, ncol) == (0, 1)
        assert fw.panel_position(3, nrow, ncol) == (1, 1)
        assert fw.panel_position(4, nrow, ncol) == (0, 2)

    def test_facet_wrap_dir_v_renders(self, tmp_path: Path):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6],
                "y": [1, 4, 9, 2, 5, 8],
                "g": ["A", "A", "B", "B", "C", "C"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + facet_wrap("g", ncol=2, dir="v")
        out = tmp_path / "facet_dir_v.png"
        p.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_facet_wrap_dir_h_renders(self, tmp_path: Path):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6],
                "y": [1, 4, 9, 2, 5, 8],
                "g": ["A", "A", "B", "B", "C", "C"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + facet_wrap("g", ncol=2, dir="h")
        out = tmp_path / "facet_dir_h.png"
        p.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0
