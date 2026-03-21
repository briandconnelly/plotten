"""Tests for ggplot2-compatible shape resolution."""

from __future__ import annotations

import pytest

from plotten._shapes import _GGPLOT2_SHAPES, resolve_shape


class TestResolveShapeNumeric:
    """Numeric codes 0-25."""

    @pytest.mark.parametrize("code", range(26))
    def test_all_numeric_codes(self, code: int) -> None:
        result = resolve_shape(code)
        assert isinstance(result, str)
        assert result == _GGPLOT2_SHAPES[code]

    def test_numeric_string(self) -> None:
        assert resolve_shape("0") == "s"
        assert resolve_shape("1") == "o"
        assert resolve_shape("25") == "v"

    def test_out_of_range(self) -> None:
        assert resolve_shape(99) == "o"
        assert resolve_shape(-1) == "o"


class TestResolveShapeNames:
    """String name lookups."""

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("circle", "o"),
            ("square", "s"),
            ("triangle", "^"),
            ("diamond", "D"),
            ("plus", "+"),
            ("cross", "x"),
            ("asterisk", "*"),
            ("triangle down", "v"),
            ("circle filled", "o"),
            ("square open", "s"),
        ],
    )
    def test_named_shapes(self, name: str, expected: str) -> None:
        assert resolve_shape(name) == expected

    def test_case_insensitive(self) -> None:
        assert resolve_shape("Circle") == "o"
        assert resolve_shape("SQUARE") == "s"
        assert resolve_shape("Triangle Down") == "v"


class TestResolveShapePassthrough:
    """Matplotlib markers passed through."""

    @pytest.mark.parametrize("marker", ["o", "s", "^", "v", "D", "+", "x", "*", ".", "h", "p"])
    def test_mpl_markers(self, marker: str) -> None:
        assert resolve_shape(marker) == marker

    def test_unknown_string(self) -> None:
        assert resolve_shape("$\\bigstar$") == "$\\bigstar$"


class TestResolveShapeEdgeCases:
    """Edge cases and invalid inputs."""

    def test_none(self) -> None:
        assert resolve_shape(None) == "o"

    def test_empty_string(self) -> None:
        assert resolve_shape("") == "o"

    def test_whitespace(self) -> None:
        assert resolve_shape("  ") == "o"

    def test_non_string_non_int(self) -> None:
        assert resolve_shape(3.14) == "o"  # type: ignore[arg-type]
