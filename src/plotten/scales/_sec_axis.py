from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class SecAxis:
    """Secondary axis specification with forward and inverse transforms."""

    def __init__(
        self,
        trans: Callable[[Any], Any],
        inverse: Callable[[Any], Any],
        name: str | None = None,
        breaks: list[float] | None = None,
        labels: list[str] | None = None,
    ) -> None:
        self.trans = trans
        self.inverse = inverse
        self.name = name
        self.breaks = breaks
        self.labels = labels


def sec_axis(
    trans: Callable[[Any], Any],
    inverse: Callable[[Any], Any],
    name: str | None = None,
    **kwargs: Any,
) -> SecAxis:
    """Create a secondary axis with a transformation."""
    return SecAxis(trans=trans, inverse=inverse, name=name, **kwargs)


def dup_axis(name: str | None = None) -> SecAxis:
    """Create a duplicate (identity) secondary axis."""
    return SecAxis(trans=lambda x: x, inverse=lambda x: x, name=name)
