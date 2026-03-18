from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from plotten._aes import Aes


@dataclass(frozen=True)
class Layer:
    """A single plot layer combining geom, stat, mapping, and data."""
    geom: Any
    stat: Any | None = None
    mapping: Aes = field(default_factory=Aes)
    params: dict = field(default_factory=dict)
    data: Any | None = None
    position: Any | None = None
