import os
import tempfile

import polars as pl

from plotten import ggplot, aes, geom_bar, coord_flip


def test_coord_flip_bar():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    p = ggplot(df, aes(x="x")) + geom_bar() + coord_flip()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_coord_flip_scatter():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + coord_flip()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        # Just test that it doesn't crash — no geom, no output
        # Add a point geom for valid render
        from plotten import geom_point
        p2 = p + geom_point()
        p2.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
