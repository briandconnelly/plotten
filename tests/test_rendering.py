import os
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pytest

from plotten import Aes, aes, facet_wrap, geom_point, ggplot, guide_legend, guides, labs, watermark
from plotten._render._mpl import render
from plotten._watermark import Watermark
from plotten.facets import FacetWrap
from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
from plotten.scales._position import ScaleContinuous, _smart_format
from plotten.themes import Theme

# --- from test_v10_legend.py ---

# ── Tests for multi-column legend support (1D) ───────────────────


def test_legend_ncol_renders():
    """Multi-column legend should render without error."""
    df = pl.DataFrame(
        {
            "x": list(range(12)),
            "y": list(range(12)),
            "color": ["a", "b", "c", "d"] * 3,
        }
    )
    plot = (
        ggplot(df, aes(x="x", y="y", color="color"))
        + geom_point()
        + guides(color=guide_legend(n_cols=2))
    )
    fig = render(plot)
    assert fig is not None
    plt.close(fig)


def test_legend_n_cols_default():
    """Default n_cols=None should behave as single column."""
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "color": ["a", "b", "c"],
        }
    )
    plot = ggplot(df, aes(x="x", y="y", color="color")) + geom_point()
    fig = render(plot)
    assert fig is not None
    plt.close(fig)


# --- from test_v10_axis_formatting.py ---

"""Tests for smart axis number formatting (1C)."""


def test_smart_format_integer():
    assert _smart_format(2.0) == "2"
    assert _smart_format(100.0) == "100"
    assert _smart_format(0.0) == "0"


def test_smart_format_float():
    assert _smart_format(3.14159) == "3.14159"
    assert _smart_format(0.001) == "0.001"


def test_smart_format_large_float():
    # :.6g should avoid ugly trailing digits
    result = _smart_format(2443.915123456789)
    assert result == "2443.92"


def test_smart_format_int_type():
    # Actual int passes through
    assert _smart_format(5) == "5"


def test_scale_continuous_default_labels():

    s = ScaleContinuous(aesthetic="x")
    s.train(pd.Series([0, 10]))
    labels = s.get_labels()
    # All labels should be cleanly formatted
    for label in labels:
        assert "..." not in label


# --- from test_legends.py ---


def test_discrete_color_legend_entries():
    scale = ScaleColorDiscrete(aesthetic="color")
    s = pl.Series("color", ["a", "b", "c"])
    scale.train(s)
    entries = scale.legend_entries()
    assert len(entries) == 3
    assert all(isinstance(e, LegendEntry) for e in entries)
    assert [e.label for e in entries] == ["a", "b", "c"]
    # Each entry should have a hex color
    assert all(e.color is not None and e.color.startswith("#") for e in entries)


def test_continuous_color_legend_entries():
    scale = ScaleColorContinuous(aesthetic="color")
    s = pl.Series("color", [0.0, 5.0, 10.0])
    scale.train(s)
    entries = scale.legend_entries()
    assert len(entries) == 5  # 5 breaks by default
    assert all(isinstance(e, LegendEntry) for e in entries)
    assert all(e.color is not None and e.color.startswith("#") for e in entries)


def test_position_scale_returns_none():
    scale = ScaleContinuous(aesthetic="x")
    s = pl.Series("x", [1.0, 2.0, 3.0])
    scale.train(s)
    assert scale.legend_entries() is None


def test_render_with_color_legend():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_position_none():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "g": ["a", "b", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + Theme(legend_position="none")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_with_faceted_plot():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["a", "a", "b", "b", "c", "c"],
            "f": ["p", "p", "p", "q", "q", "q"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + FacetWrap(facets="f")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_title_from_labs():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "g": ["a", "b", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + labs(color="Species")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_position_left():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "g": ["a", "b", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + Theme(legend_position="left")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_position_top():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "g": ["a", "b", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + Theme(legend_position="top")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_legend_position_bottom():
    df = pl.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [3, 1, 2],
            "g": ["a", "b", "c"],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + Theme(legend_position="bottom")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_continuous_color_legend_positions():
    df = pl.DataFrame(
        {
            "x": [1.0, 2.0, 3.0],
            "y": [2.0, 4.0, 1.0],
            "val": [0.0, 5.0, 10.0],
        }
    )
    for pos in ("left", "top", "bottom"):
        p = ggplot(df, aes(x="x", y="y", color="val")) + geom_point() + Theme(legend_position=pos)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            p.save(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


def test_continuous_color_legend_render():
    df = pl.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 1.0, 5.0, 3.0],
            "val": [0.0, 2.5, 5.0, 7.5, 10.0],
        }
    )
    p = ggplot(df, aes(x="x", y="y", color="val")) + geom_point()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


# --- from test_v110_rendering.py ---

"""Tests for v1.1.0 Phase 4 rendering improvements: watermark and facet_wrap dir."""

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


# --- FacetWrap direction ---


class TestFacetWrapDir:
    def test_default_direction_is_h(self):
        fw = facet_wrap("group")
        assert fw.direction == "h"

    def test_direction_v(self):
        fw = facet_wrap("group", direction="v")
        assert fw.direction == "v"

    def test_panel_position_h(self):
        fw = FacetWrap(facets="g", n_cols=3, direction="h")
        nr, nc = fw.layout(5)
        # h: row-major => idx 0->(0,0), 1->(0,1), 2->(0,2), 3->(1,0), 4->(1,1)
        assert fw.panel_position(0, nr, nc) == (0, 0)
        assert fw.panel_position(1, nr, nc) == (0, 1)
        assert fw.panel_position(2, nr, nc) == (0, 2)
        assert fw.panel_position(3, nr, nc) == (1, 0)
        assert fw.panel_position(4, nr, nc) == (1, 1)

    def test_panel_position_v(self):
        fw = FacetWrap(facets="g", n_cols=3, n_rows=2, direction="v")
        nr, nc = fw.layout(5)
        # v: column-major => idx 0->(0,0), 1->(1,0), 2->(0,1), 3->(1,1), 4->(0,2)
        assert fw.panel_position(0, nr, nc) == (0, 0)
        assert fw.panel_position(1, nr, nc) == (1, 0)
        assert fw.panel_position(2, nr, nc) == (0, 1)
        assert fw.panel_position(3, nr, nc) == (1, 1)
        assert fw.panel_position(4, nr, nc) == (0, 2)

    def test_facet_wrap_direction_v_renders(self, tmp_path: Path):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6],
                "y": [1, 4, 9, 2, 5, 8],
                "g": ["A", "A", "B", "B", "C", "C"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + facet_wrap("g", n_cols=2, direction="v")
        out = tmp_path / "facet_dir_v.png"
        p.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_facet_wrap_direction_h_renders(self, tmp_path: Path):
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6],
                "y": [1, 4, 9, 2, 5, 8],
                "g": ["A", "A", "B", "B", "C", "C"],
            }
        )
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + facet_wrap("g", n_cols=2, direction="h")
        out = tmp_path / "facet_dir_h.png"
        p.save(str(out))
        assert out.exists()
        assert out.stat().st_size > 0


# ---------------------------------------------------------------------------
# Scale resolution internals
# ---------------------------------------------------------------------------


class TestScaleResolutionHelpers:
    """Unit tests for _render/_scale_resolution.py internals."""

    def test_opt_min_both_none(self):
        from plotten._render._scale_resolution import _opt_min

        assert _opt_min(None, None) is None

    def test_opt_min_a_none(self):
        from plotten._render._scale_resolution import _opt_min

        assert _opt_min(None, 5.0) == 5.0

    def test_opt_min_b_none(self):
        from plotten._render._scale_resolution import _opt_min

        assert _opt_min(3.0, None) == 3.0

    def test_opt_min_both_values(self):
        from plotten._render._scale_resolution import _opt_min

        assert _opt_min(3.0, 5.0) == 3.0

    def test_opt_max_a_none(self):
        from plotten._render._scale_resolution import _opt_max

        assert _opt_max(None, 5.0) == 5.0

    def test_opt_max_both_values(self):
        from plotten._render._scale_resolution import _opt_max

        assert _opt_max(3.0, 5.0) == 5.0


class TestTrainScalesNanHandling:
    """Test that scale training handles NaN/Inf values gracefully."""

    def test_train_with_nan_warns(self):
        import warnings

        import narwhals as nw

        from plotten._render._scale_resolution import _train_scales

        data = {"x": [1.0, float("nan"), 3.0]}
        frame = nw.from_native(pl.DataFrame(data))
        scales: dict = {}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _train_scales(frame, data, scales)
        nan_warnings = [x for x in w if "non-finite" in str(x.message)]
        assert len(nan_warnings) >= 1

    def test_train_with_all_nan_skips(self):
        import warnings

        import narwhals as nw

        from plotten._render._scale_resolution import _train_scales

        data = {"x": [float("nan"), float("inf")]}
        frame = nw.from_native(pl.DataFrame(data))
        scales: dict = {}
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _train_scales(frame, data, scales)
        skip_warnings = [x for x in w if "all values are non-finite" in str(x.message)]
        assert len(skip_warnings) >= 1

    def test_render_with_nan_in_data(self):
        """Full render should survive NaN values in data."""
        import warnings

        df = pl.DataFrame({"x": [1.0, float("nan"), 3.0], "y": [1.0, 2.0, 3.0]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig = render(p)
        assert fig is not None
