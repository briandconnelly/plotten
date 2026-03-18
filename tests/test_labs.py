import os
import tempfile

import polars as pl

from plotten import Labs, ggplot, aes, geom_point, labs


def test_labs_creation():
    lb = Labs(title="My Title", x="X Axis")
    assert lb.title == "My Title"
    assert lb.x == "X Axis"
    assert lb.y is None


def test_labs_convenience():
    lb = labs(title="Hello", y="Y Axis")
    assert isinstance(lb, Labs)
    assert lb.title == "Hello"
    assert lb.y == "Y Axis"


def test_labs_merge():
    a = Labs(title="A", x="X1")
    b = Labs(title="B", caption="Cap")
    merged = a + b
    assert merged.title == "B"  # other wins
    assert merged.x == "X1"  # kept from self
    assert merged.caption == "Cap"


def test_labs_immutable():
    lb = Labs(title="T")
    assert lb.title == "T"


def test_plot_with_labs():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + labs(title="Test", x="X Label", y="Y Label")
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_subtitle_only():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(subtitle="Just subtitle")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_title_and_subtitle():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + labs(title="Main Title", subtitle="A subtitle")
    )
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_caption_rendering():
    df = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
    p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(caption="Source: test data")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        p.save(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
