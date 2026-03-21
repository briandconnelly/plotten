"""Helper to extract matplotlib text kwargs from ElementText + theme defaults."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plotten.themes._elements import ElementBlank, ElementText
    from plotten.themes._theme import Theme


def text_props(
    element: ElementText | ElementBlank | None,
    theme: Theme,
    *,
    default_size: float | None = None,
    default_color: str = "#000000",
    is_title: bool = False,
) -> dict[str, Any]:
    """Build matplotlib text kwargs from ElementText + theme fallbacks.

    Returns dict with keys like ``fontsize``, ``color``, ``fontfamily``,
    ``fontweight``, ``fontstyle``, ``rotation``, ``ha``, ``va`` — only
    including non-None values.  Falls back to *theme.font_family* for
    family and the provided *default_size* / *default_color* for size/color.

    When *is_title* is True, the element also inherits from ``theme.title``
    (which itself inherits from ``theme.text``).
    """
    from plotten.themes._elements import ElementText, merge_text

    # Build the inheritance chain: theme.text → theme.title (if title) → element
    base = theme.text if isinstance(theme.text, ElementText) else None
    if is_title and isinstance(theme.title, ElementText):
        base = merge_text(theme.title, base)
    if isinstance(element, ElementText):
        element = merge_text(element, base)
    elif base is not None:
        element = base

    props: dict[str, Any] = {}

    if default_size is not None:
        props["fontsize"] = default_size
    props["color"] = default_color
    props["fontfamily"] = theme.font_family

    if isinstance(element, ElementText):
        if element.size is not None:
            from plotten.themes._elements import Rel

            if isinstance(element.size, Rel):
                if default_size is not None:
                    props["fontsize"] = element.size.factor * default_size
            else:
                props["fontsize"] = element.size
        if element.color is not None:
            props["color"] = element.color
        if element.family is not None:
            props["fontfamily"] = element.family
        if element.weight is not None:
            props["fontweight"] = element.weight
        if element.style is not None:
            props["fontstyle"] = element.style
        if element.rotation is not None:
            props["rotation"] = element.rotation
        if element.ha is not None:
            props["ha"] = element.ha
        if element.va is not None:
            props["va"] = element.va

    return props
