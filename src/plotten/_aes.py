from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from plotten._computed import AfterScale, AfterStat
    from plotten._interaction import Interaction

type AesValue = str | AfterStat | AfterScale | Interaction | None


@dataclass(frozen=True, slots=True, kw_only=True)
class Aes:
    """Aesthetic mapping specification."""

    x: str | AfterStat | AfterScale | Interaction | None = None
    y: str | AfterStat | AfterScale | Interaction | None = None
    color: str | AfterStat | AfterScale | Interaction | None = None
    fill: str | AfterStat | AfterScale | Interaction | None = None
    size: str | AfterStat | AfterScale | Interaction | None = None
    alpha: str | AfterStat | AfterScale | Interaction | None = None
    linetype: str | AfterStat | AfterScale | Interaction | None = None
    shape: str | AfterStat | AfterScale | Interaction | None = None
    label: str | AfterStat | AfterScale | Interaction | None = None
    ymin: str | AfterStat | AfterScale | Interaction | None = None
    ymax: str | AfterStat | AfterScale | Interaction | None = None
    group: str | AfterStat | AfterScale | Interaction | None = None
    xend: str | AfterStat | AfterScale | Interaction | None = None
    yend: str | AfterStat | AfterScale | Interaction | None = None
    xmin: str | AfterStat | AfterScale | Interaction | None = None
    xmax: str | AfterStat | AfterScale | Interaction | None = None
    z: str | AfterStat | AfterScale | Interaction | None = None
    angle: str | AfterStat | AfterScale | Interaction | None = None
    radius: str | AfterStat | AfterScale | Interaction | None = None

    def __or__(self, other: Aes) -> Self:
        """Merge aesthetics. other's non-None fields win."""
        return type(self)(
            **{
                f.name: (
                    getattr(other, f.name)
                    if getattr(other, f.name) is not None
                    else getattr(self, f.name)
                )
                for f in self.__dataclass_fields__.values()
            }
        )


def aes(**kwargs: str | AfterStat | AfterScale | Interaction) -> Aes:
    """Map data columns to visual properties.

    Accepts ``colour`` as an alias for ``color`` (ggplot2 convention).

    Parameters
    ----------
    x, y : str, optional
        Column names for position aesthetics.
    color, fill : str, optional
        Column names for color or fill mapping.
    size, alpha, shape, linetype : str, optional
        Column names for other visual properties.
    label : str, optional
        Column name for text labels.
    group : str, optional
        Column name for grouping.

    Examples
    --------
    >>> from plotten import aes
    >>> aes(x="speed", y="distance", color="category")
    Aes(x='speed', y='distance', color='category', ...)
    """
    # Support British spelling alias
    if "colour" in kwargs:
        if "color" in kwargs:
            msg = "Cannot specify both 'color' and 'colour' in aes()"
            raise TypeError(msg)
        kwargs["color"] = kwargs.pop("colour")
    return Aes(**kwargs)
