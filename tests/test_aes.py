import pytest

from plotten._aes import Aes, aes


def test_aes_defaults():
    a = Aes()
    assert a.x is None
    assert a.y is None


def test_aes_constructor():
    a = aes(x="col_x", y="col_y", color="grp")
    assert a.x == "col_x"
    assert a.y == "col_y"
    assert a.color == "grp"
    assert a.fill is None


def test_aes_merge():
    a = aes(x="a", y="b", color="c")
    b = aes(y="d", size="s")
    merged = a | b
    assert merged.x == "a"  # kept from a
    assert merged.y == "d"  # overridden by b
    assert merged.color == "c"  # kept from a
    assert merged.size == "s"  # new from b


def test_aes_frozen():
    a = aes(x="x")
    try:
        a.x = "y"  # type: ignore[misc]
        pytest.fail("Should have raised")
    except AttributeError:
        pass
