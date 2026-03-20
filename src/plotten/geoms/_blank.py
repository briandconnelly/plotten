"""Blank geom — trains scales from data without drawing anything."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomBlank:
    """A geom that draws nothing.

    Useful for expanding axis limits from data without rendering any marks.
    """

    required_aes: frozenset[str] = frozenset()
    supports_group_splitting: bool = False

    def default_stat(self):
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        pass
