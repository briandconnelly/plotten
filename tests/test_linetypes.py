"""Tests for ggplot2-compatible linetype resolution."""

from __future__ import annotations

import pytest

from plotten._linetypes import _GGPLOT2_LINETYPES, resolve_linetype


class TestResolveLinetypeNumeric:
    """Numeric codes 0-6."""

    @pytest.mark.parametrize("code", range(7))
    def test_all_numeric_codes(self, code: int) -> None:
        result = resolve_linetype(code)
        assert result == _GGPLOT2_LINETYPES[code]

    def test_numeric_string(self) -> None:
        assert resolve_linetype("0") == "none"
        assert resolve_linetype("1") == "solid"
        assert resolve_linetype("2") == "dashed"

    def test_out_of_range(self) -> None:
        assert resolve_linetype(99) == "solid"
        assert resolve_linetype(-1) == "solid"


class TestResolveLinetypeNames:
    """String name lookups."""

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("blank", "none"),
            ("solid", "solid"),
            ("dashed", "dashed"),
            ("dotted", "dotted"),
            ("dotdash", "dashdot"),
            ("longdash", (0, (10, 3))),
            ("twodash", (0, (8, 3, 2, 3))),
        ],
    )
    def test_named_linetypes(self, name: str, expected: object) -> None:
        assert resolve_linetype(name) == expected

    def test_case_insensitive(self) -> None:
        assert resolve_linetype("Solid") == "solid"
        assert resolve_linetype("DASHED") == "dashed"
        assert resolve_linetype("LongDash") == (0, (10, 3))


class TestResolveLinetypeShortAliases:
    """Short alias strings."""

    @pytest.mark.parametrize(
        ("alias", "expected"),
        [
            ("--", "dashed"),
            ("..", "dotted"),
            ("-.", "dashdot"),
            ("-", "solid"),
        ],
    )
    def test_aliases(self, alias: str, expected: str) -> None:
        assert resolve_linetype(alias) == expected


class TestResolveLinetypeHexPattern:
    """Hex dash pattern strings."""

    def test_simple_hex(self) -> None:
        result = resolve_linetype("33")
        assert result == (0, (3.0, 3.0))

    def test_complex_hex(self) -> None:
        result = resolve_linetype("3313")
        assert result == (0, (3.0, 3.0, 1.0, 3.0))

    def test_hex_with_letters(self) -> None:
        result = resolve_linetype("af")
        assert result == (0, (10.0, 15.0))


class TestResolveLinetypeEdgeCases:
    """Edge cases and invalid inputs."""

    def test_none(self) -> None:
        assert resolve_linetype(None) == "solid"

    def test_empty_string(self) -> None:
        assert resolve_linetype("") == "solid"

    def test_whitespace(self) -> None:
        assert resolve_linetype("  ") == "solid"

    def test_passthrough(self) -> None:
        assert resolve_linetype("solid") == "solid"

    def test_non_string_non_int(self) -> None:
        # Tuples pass through as-is (matplotlib dash spec)
        dash = (0, (5, 2))
        assert resolve_linetype(dash) == dash  # type: ignore[arg-type]
