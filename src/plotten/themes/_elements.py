from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementText:
    """Theme element for text."""

    size: float | None = None
    color: str | None = None
    family: str | None = None
    weight: str | None = None
    style: str | None = None
    rotation: float | None = None
    ha: str | None = None
    va: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementLine:
    """Theme element for lines."""

    color: str | None = None
    size: float | None = None
    linetype: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementRect:
    """Theme element for rectangles."""

    fill: str | None = None
    color: str | None = None
    size: float | None = None


@dataclass(frozen=True, slots=True)
class ElementBlank:
    """Suppresses drawing of the element."""

    pass


def element_text(**kwargs) -> ElementText:
    """Create a text element."""
    return ElementText(**kwargs)


def element_line(**kwargs) -> ElementLine:
    """Create a line element."""
    return ElementLine(**kwargs)


def element_rect(**kwargs) -> ElementRect:
    """Create a rect element."""
    return ElementRect(**kwargs)


def element_blank() -> ElementBlank:
    """Create a blank element that suppresses drawing."""
    return ElementBlank()
