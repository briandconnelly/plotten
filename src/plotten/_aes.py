from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from plotten._computed import AfterScale, AfterStat


@dataclass(frozen=True, slots=True, kw_only=True)
class Aes:
    """Aesthetic mapping specification."""

    x: str | AfterStat | AfterScale | None = None
    y: str | AfterStat | AfterScale | None = None
    color: str | AfterStat | AfterScale | None = None
    fill: str | AfterStat | AfterScale | None = None
    size: str | AfterStat | AfterScale | None = None
    alpha: str | AfterStat | AfterScale | None = None
    linetype: str | AfterStat | AfterScale | None = None
    shape: str | AfterStat | AfterScale | None = None
    label: str | AfterStat | AfterScale | None = None
    ymin: str | AfterStat | AfterScale | None = None
    ymax: str | AfterStat | AfterScale | None = None
    group: str | AfterStat | AfterScale | None = None
    xend: str | AfterStat | AfterScale | None = None
    yend: str | AfterStat | AfterScale | None = None
    xmin: str | AfterStat | AfterScale | None = None
    xmax: str | AfterStat | AfterScale | None = None
    z: str | AfterStat | AfterScale | None = None

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


def aes(**kwargs: str) -> Aes:
    """Convenience constructor for Aes."""
    return Aes(**kwargs)
