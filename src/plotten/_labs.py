from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Self


@dataclass(frozen=True, slots=True, kw_only=True)
class Labs:
    """Labels for plot title, subtitle, axes, and aesthetics."""

    title: str | None = None
    subtitle: str | None = None
    x: str | None = None
    y: str | None = None
    color: str | None = None
    fill: str | None = None
    size: str | None = None
    alpha: str | None = None
    shape: str | None = None
    linetype: str | None = None
    linewidth: str | None = None
    hatch: str | None = None
    caption: str | None = None
    tag: str | None = None

    def __add__(self, other: Labs) -> Self:
        """Merge labels — other's non-None values win."""
        if not isinstance(other, Labs):
            return NotImplemented
        kwargs: dict[str, Any] = {}
        for f in fields(self):
            other_val = getattr(other, f.name)
            if other_val is not None:
                kwargs[f.name] = other_val
            else:
                kwargs[f.name] = getattr(self, f.name)
        return type(self)(**kwargs)


def labs(**kwargs: str) -> Labs:
    """Set plot labels for title, axes, and legends.

    Parameters
    ----------
    title : str, optional
        Plot title.
    subtitle : str, optional
        Plot subtitle.
    x, y : str, optional
        Axis labels.
    color, fill, size, alpha, shape, linetype, linewidth, hatch : str, optional
        Legend titles for the corresponding aesthetic.
        ``colour`` is accepted as an alias for ``color``.
    caption : str, optional
        Caption text below the plot.
    tag : str, optional
        Tag label for multi-panel figures (e.g. "A", "B").

    Examples
    --------
    >>> from plotten import labs
    >>> labs(title="My Plot", x="Speed (mph)", y="Distance (ft)")
    Labs(title='My Plot', ...)
    """
    if "colour" in kwargs:
        kwargs["color"] = kwargs.pop("colour")
    return Labs(**kwargs)
