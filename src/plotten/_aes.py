from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Aes:
    """Aesthetic mapping specification."""
    x: str | None = None
    y: str | None = None
    color: str | None = None
    fill: str | None = None
    size: str | None = None
    alpha: str | None = None
    linetype: str | None = None
    shape: str | None = None
    label: str | None = None

    def __or__(self, other: Aes) -> Aes:
        """Merge aesthetics. other's non-None fields win."""
        return Aes(**{
            f.name: (getattr(other, f.name) if getattr(other, f.name) is not None else getattr(self, f.name))
            for f in self.__dataclass_fields__.values()
        })


def aes(**kwargs: str) -> Aes:
    """Convenience constructor for Aes."""
    return Aes(**kwargs)
