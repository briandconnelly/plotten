from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from plotten._aes import Aes

if TYPE_CHECKING:
    from plotten._protocols import Geom, Position, Stat


@dataclass(frozen=True, slots=True)
class Layer:
    """A single plot layer combining geom, stat, mapping, and data."""

    geom: Geom
    stat: Stat | None = None
    mapping: Aes = field(default_factory=Aes)
    params: dict = field(default_factory=dict)
    position: Position | None = None
    data: Any | None = None
