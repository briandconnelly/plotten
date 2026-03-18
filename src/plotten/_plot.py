from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any

from plotten._aes import Aes
from plotten._labs import Labs
from plotten._layer import Layer
from plotten.coords._cartesian import CoordCartesian
from plotten.coords._flip import CoordFlip
from plotten.facets import FacetGrid, FacetWrap
from plotten.scales._base import ScaleBase
from plotten.themes._theme import Theme


@dataclass(frozen=True)
class Plot:
    """Immutable plot specification built up via ``+`` operator."""

    data: Any = None
    mapping: Aes = field(default_factory=Aes)
    layers: tuple[Layer, ...] = ()
    scales: tuple[ScaleBase, ...] = ()
    coord: Any = field(default_factory=CoordCartesian)
    theme: Theme = field(default_factory=Theme)
    labs: Labs = field(default_factory=Labs)
    facet: Any = None

    def _replace(self, **kwargs: Any) -> Plot:
        """Return a copy with given fields replaced."""
        from dataclasses import fields as dc_fields

        vals = {f.name: getattr(self, f.name) for f in dc_fields(self)}
        vals.update(kwargs)
        return Plot(**vals)

    def __add__(self, other: Any) -> Plot:
        if isinstance(other, Layer):
            return self._replace(layers=(*self.layers, other))
        if isinstance(other, ScaleBase):
            return self._replace(scales=(*self.scales, other))
        if isinstance(other, Theme):
            return self._replace(theme=self.theme + other)
        if isinstance(other, Labs):
            return self._replace(labs=self.labs + other)
        if isinstance(other, (CoordCartesian, CoordFlip)):
            return self._replace(coord=other)
        # Support new coord types
        from plotten.coords._equal import CoordEqual, CoordFixed

        if isinstance(other, (CoordEqual, CoordFixed)):
            return self._replace(coord=other)
        if isinstance(other, (FacetWrap, FacetGrid)):
            return self._replace(facet=other)
        return NotImplemented

    def show(self) -> None:
        """Render and display the plot."""
        from plotten._render._mpl import render

        fig = render(self)
        fig.show()

    def save(
        self,
        path: str,
        dpi: int = 150,
        width: float | None = None,
        height: float | None = None,
        units: str = "in",
    ) -> None:
        """Render and save the plot to a file."""
        from plotten._render._mpl import render

        fig = render(self)
        if width is not None or height is not None:
            unit_factors = {"in": 1.0, "cm": 1 / 2.54, "mm": 1 / 25.4, "px": 1 / dpi}
            factor = unit_factors.get(units, 1.0)
            cur_w, cur_h = fig.get_size_inches()
            new_w = width * factor if width is not None else cur_w
            new_h = height * factor if height is not None else cur_h
            fig.set_size_inches(new_w, new_h)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        import matplotlib.pyplot as plt

        plt.close(fig)

    def _repr_png_(self) -> bytes:
        """Jupyter integration — display as PNG."""
        from plotten._render._mpl import render

        fig = render(self)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        import matplotlib.pyplot as plt

        plt.close(fig)
        return buf.getvalue()


def ggplot(data: Any = None, mapping: Aes | None = None) -> Plot:
    """Create a new plot."""
    return Plot(data=data, mapping=mapping or Aes())
