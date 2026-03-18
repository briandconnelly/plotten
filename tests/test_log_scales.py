import os
import tempfile

import polars as pl

from plotten import aes, geom_point, ggplot, scale_x_log10, scale_y_log10
from plotten.scales._log import ScaleLog


def test_scale_log_breaks():
    s = ScaleLog(aesthetic="x", base=10)
    import pandas as pd

    s.train(pd.Series([1, 100, 10000]))
    breaks = s.get_breaks()
    assert 1 in breaks
    assert 100 in breaks
    assert 10000 in breaks


def test_scale_log_limits():
    s = ScaleLog(aesthetic="y", base=10)
    import pandas as pd

    s.train(pd.Series([10, 1000]))
    lo, hi = s.get_limits()
    assert lo == 10
    assert hi == 1000


def test_scale_y_log10_render():
    df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 100, 1000, 10000, 100000]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_log10()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_scale_x_log10_render():
    df = pl.DataFrame({"x": [1, 10, 100, 1000], "y": [1, 2, 3, 4]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_log10()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
