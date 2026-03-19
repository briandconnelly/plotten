from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any, Self

from plotten._aes import Aes
from plotten._enums import SizeUnit
from plotten._labs import Labs
from plotten._layer import Layer
from plotten.coords._cartesian import CoordCartesian
from plotten.coords._flip import CoordFlip
from plotten.facets import FacetGrid, FacetWrap
from plotten.scales._base import ScaleBase
from plotten.themes._theme import Theme


@dataclass(frozen=True, slots=True)
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
    guides: dict | None = None
    _expand_limits: tuple = ()

    def _replace(self, **kwargs: Any) -> Self:
        """Return a copy with given fields replaced."""
        from dataclasses import fields as dc_fields

        vals = {f.name: getattr(self, f.name) for f in dc_fields(self)}
        vals.update(kwargs)
        return type(self)(**vals)

    def __add__(self, other: Any) -> Plot:
        from plotten._expand_limits import ExpandLimits

        match other:
            case Layer():
                return self._replace(layers=(*self.layers, other))
            case ScaleBase():
                return self._replace(scales=(*self.scales, other))
            case Theme():
                return self._replace(theme=self.theme + other)
            case Labs():
                return self._replace(labs=self.labs + other)
            case CoordCartesian() | CoordFlip():
                return self._replace(coord=other)
            case FacetWrap() | FacetGrid():
                return self._replace(facet=other)
            case ExpandLimits():
                return self._replace(_expand_limits=(*self._expand_limits, other))
            case dict():
                # Guides dict
                existing = self.guides or {}
                return self._replace(guides={**existing, **other})
            case _:
                # Support new coord types
                from plotten.coords._equal import CoordEqual, CoordFixed
                from plotten.coords._polar import CoordPolar

                if isinstance(other, CoordEqual | CoordFixed | CoordPolar):
                    return self._replace(coord=other)
                return NotImplemented

    def __or__(self, other: Any) -> Any:
        from plotten._composition import PlotGrid

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="h")
        return NotImplemented

    def __truediv__(self, other: Any) -> Any:
        from plotten._composition import PlotGrid

        if isinstance(other, Plot | PlotGrid):
            return PlotGrid(plots=(self, other), direction="v")
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
            match units:
                case SizeUnit.INCHES:
                    factor = 1.0
                case SizeUnit.CM:
                    factor = 1 / 2.54
                case SizeUnit.MM:
                    factor = 1 / 25.4
                case SizeUnit.PX:
                    factor = 1 / dpi
                case _:
                    factor = 1.0
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
