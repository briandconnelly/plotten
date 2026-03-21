"""Tests for text element helpers: hjust/vjust and element merging."""

from __future__ import annotations

import pytest

from plotten.themes._elements import (
    ElementBlank,
    ElementLine,
    ElementRect,
    ElementText,
    element_text,
    merge_line,
    merge_rect,
    merge_text,
)
from plotten.themes._text_props import _resolve_ha, _resolve_va


class TestHjustVjust:
    """Numeric 0-1 hjust/vjust to matplotlib ha/va."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, "left"),
            (0.1, "left"),
            (0.25, "left"),
            (0.5, "center"),
            (0.75, "right"),
            (0.9, "right"),
            (1.0, "right"),
        ],
    )
    def test_resolve_ha(self, value: float, expected: str) -> None:
        assert _resolve_ha(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, "bottom"),
            (0.1, "bottom"),
            (0.25, "bottom"),
            (0.5, "center"),
            (0.75, "top"),
            (0.9, "top"),
            (1.0, "top"),
        ],
    )
    def test_resolve_va(self, value: float, expected: str) -> None:
        assert _resolve_va(value) == expected

    def test_string_passthrough(self) -> None:
        assert _resolve_ha("left") == "left"
        assert _resolve_va("top") == "top"


class TestElementTextAliases:
    """hjust/vjust aliases in element_text()."""

    def test_hjust_alias(self) -> None:
        et = element_text(hjust=0.5)
        assert et.ha == 0.5

    def test_vjust_alias(self) -> None:
        et = element_text(vjust=1.0)
        assert et.va == 1.0

    def test_ha_takes_precedence(self) -> None:
        et = element_text(ha="left", hjust=0.5)
        assert et.ha == "left"


class TestMergeText:
    """merge_text with ElementBlank handling."""

    def test_element_blank_wins(self) -> None:
        base = ElementText(size=12)
        result = merge_text(ElementBlank(), base)
        assert isinstance(result, ElementBlank)

    def test_blank_base_ignored(self) -> None:
        element = ElementText(size=14)
        result = merge_text(element, ElementBlank())
        assert isinstance(result, ElementText)
        assert result.size == 14

    def test_none_element_returns_base(self) -> None:
        base = ElementText(size=12, color="red")
        assert merge_text(None, base) is base

    def test_merge_fills_none_from_base(self) -> None:
        element = ElementText(size=14)
        base = ElementText(size=12, color="red")
        result = merge_text(element, base)
        assert isinstance(result, ElementText)
        assert result.size == 14
        assert result.color == "red"


class TestMergeLine:
    """merge_line with ElementBlank handling."""

    def test_element_blank_wins(self) -> None:
        result = merge_line(ElementBlank(), ElementLine(size=1.0))
        assert isinstance(result, ElementBlank)

    def test_blank_base_ignored(self) -> None:
        element = ElementLine(size=2.0)
        result = merge_line(element, ElementBlank())
        assert isinstance(result, ElementLine)
        assert result.size == 2.0


class TestMergeRect:
    """merge_rect with ElementBlank handling."""

    def test_element_blank_wins(self) -> None:
        result = merge_rect(ElementBlank(), ElementRect(fill="white"))
        assert isinstance(result, ElementBlank)

    def test_blank_base_ignored(self) -> None:
        element = ElementRect(fill="blue")
        result = merge_rect(element, ElementBlank())
        assert isinstance(result, ElementRect)
        assert result.fill == "blue"
