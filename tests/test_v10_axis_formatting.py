"""Tests for smart axis number formatting (1C)."""

from plotten.scales._position import ScaleContinuous, _smart_format


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
    import pandas as pd

    s = ScaleContinuous(aesthetic="x")
    s.train(pd.Series([0, 10]))
    labels = s.get_labels()
    # All labels should be cleanly formatted
    for label in labels:
        assert "..." not in label
