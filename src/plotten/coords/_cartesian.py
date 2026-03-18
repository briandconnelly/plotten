from __future__ import annotations

from typing import Any


class CoordCartesian:
    """Cartesian coordinate system with optional axis limits."""

    def __init__(
        self,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
    ) -> None:
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, data: Any, ax: Any) -> Any:
        """Apply coordinate limits to the axes."""
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        return data
