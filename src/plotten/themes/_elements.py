from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rel:
    """Relative size multiplier.

    When used as the ``size`` of an :class:`ElementText`, the final font
    size is ``factor * default_size`` where *default_size* comes from the
    theme hierarchy.
    """

    factor: float


def rel(factor: float) -> Rel:
    """Create a relative size multiplier.

    Parameters
    ----------
    factor : float
        Multiplicative factor applied to the parent element's default
        size.  For example, ``rel(0.8)`` means 80 % of the default.

    Examples
    --------
    >>> from plotten.themes import element_text, rel
    >>> element_text(size=rel(1.2))
    ElementText(size=Rel(factor=1.2), ...)
    """
    return Rel(factor)


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementText:
    """Theme element for text."""

    size: float | Rel | None = None
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
