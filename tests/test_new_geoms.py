import os
import tempfile

import polars as pl

from plotten import ggplot, aes, geom_histogram, geom_boxplot, geom_smooth, geom_text, geom_label


def test_histogram_render():
    df = pl.DataFrame({"val": [1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 5.5, 6.0, 7.0]})
    p = ggplot(df, aes(x="val")) + geom_histogram(bins=5)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_boxplot_render():
    df = pl.DataFrame({
        "group": ["a"] * 10 + ["b"] * 10,
        "value": list(range(10)) + list(range(5, 15)),
    })
    p = ggplot(df, aes(x="group", y="value")) + geom_boxplot()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_smooth_ols_render():
    df = pl.DataFrame({
        "x": list(range(20)),
        "y": [float(i) + (i % 3) for i in range(20)],
    })
    p = ggplot(df, aes(x="x", y="y")) + geom_smooth(method="ols")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_smooth_moving_average_render():
    df = pl.DataFrame({
        "x": list(range(20)),
        "y": [float(i) * 0.5 for i in range(20)],
    })
    p = ggplot(df, aes(x="x", y="y")) + geom_smooth(method="moving_average")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_text_render():
    df = pl.DataFrame({
        "x": [1, 2, 3],
        "y": [3, 1, 2],
        "lbl": ["A", "B", "C"],
    })
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_text()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_label_render():
    df = pl.DataFrame({
        "x": [1, 2, 3],
        "y": [3, 1, 2],
        "lbl": ["A", "B", "C"],
    })
    p = ggplot(df, aes(x="x", y="y", label="lbl")) + geom_label()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
