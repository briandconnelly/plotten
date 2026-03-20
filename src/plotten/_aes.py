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

    x: AesValue = None
    y: AesValue = None
    color: AesValue = None
    fill: AesValue = None
    size: AesValue = None
    alpha: AesValue = None
    linetype: AesValue = None
    shape: AesValue = None
    label: AesValue = None
    ymin: AesValue = None
    ymax: AesValue = None
    group: AesValue = None
    xend: AesValue = None
    yend: AesValue = None
    xmin: AesValue = None
    xmax: AesValue = None
    z: AesValue = None
    angle: AesValue = None
    radius: AesValue = None
    linewidth: AesValue = None
    hatch: AesValue = None

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


def aes(**kwargs: AesValue) -> Aes:
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
