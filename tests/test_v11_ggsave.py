"""Tests for the ggsave() convenience function."""

from pathlib import Path

import pandas as pd

from plotten import Aes, geom_point, ggplot, ggsave


def _make_plot():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    return ggplot(df, Aes(x="x", y="y")) + geom_point()


def test_ggsave_basic(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_svg(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.svg"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_pdf(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.pdf"
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_width_height(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=8, height=6)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_width_only(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=10)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_height_only(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, height=5)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_cm_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=20, height=15, units="cm")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_mm_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=200, height=150, units="mm")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_px_units(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, width=800, height=600, units="px")
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_transparent(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, transparent=True)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_custom_dpi(tmp_path: Path) -> None:
    p = _make_plot()
    out = tmp_path / "plot.png"
    ggsave(p, out, dpi=72)
    assert out.exists()
    assert out.stat().st_size > 0


def test_ggsave_pathlib(tmp_path: Path) -> None:
    p = _make_plot()
    out = Path(tmp_path) / "subdir" / "plot.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    ggsave(p, out)
    assert out.exists()
    assert out.stat().st_size > 0
