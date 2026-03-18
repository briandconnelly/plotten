import os
import tempfile

import polars as pl

from plotten import aes, geom_point, ggplot, labs
from plotten.facets import FacetWrap
from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
from plotten.scales._position import ScaleContinuous
from plotten.themes import Theme


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
