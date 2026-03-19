"""Dataclasses for the resolution pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plotten._labs import Labs
    from plotten._protocols import Coord, Geom, Position
    from plotten.scales._base import ScaleBase
    from plotten.themes._theme import Theme


@dataclass(slots=True)
class ResolvedLayer:
    """A layer with stat applied and data resolved to plain dicts."""

    geom: Geom
    data: dict[str, Any]
    params: dict
    position: Position | None = None


@dataclass(slots=True)
class ResolvedPanel:
    """A single panel (facet) of layers and scales."""

    label: str
    layers: list[ResolvedLayer] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)


@dataclass(slots=True)
class ResolvedPlot:
    """Fully resolved plot ready for rendering."""

    panels: list[ResolvedPanel] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)
    coord: Coord | None = None
    theme: Theme | None = None
    labs: Labs | None = None
    facet: Any = None
    guides: dict | None = None
