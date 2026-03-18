import os
import tempfile

import polars as pl

from plotten import ggplot, aes, geom_bar, geom_point, coord_flip
from plotten.coords._cartesian import CoordCartesian


def _save_and_check(p):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_coord_flip_bar():
    df = pl.DataFrame({"x": ["a", "b", "a", "c", "b", "a"]})
    p = ggplot(df, aes(x="x")) + geom_bar() + coord_flip()
    _save_and_check(p)


def test_coord_flip_scatter():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + coord_flip()
    _save_and_check(p)


def test_coord_cartesian_xlim():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + CoordCartesian(xlim=(0, 10))
    _save_and_check(p)


def test_coord_cartesian_ylim():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + CoordCartesian(ylim=(-1, 8))
    _save_and_check(p)
