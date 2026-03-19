from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class CoordFlip:
    """Flip x and y axes."""

    def __init__(
        self,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
    ) -> None:
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, data: Any, ax: Axes) -> Any:
        return data

    @staticmethod
    def flip_resolved(resolved: Any) -> Any:
        """Swap x/y in all panel layer data and scales for CoordFlip."""
        from plotten._render._resolve import ResolvedLayer, ResolvedPanel, ResolvedPlot

        new_scales = {}
        for k, v in resolved.scales.items():
            if k == "x":
                new_scales["y"] = v
            elif k == "y":
                new_scales["x"] = v
            else:
                new_scales[k] = v

        new_panels = []
        for panel in resolved.panels:
            new_layers = []
            for layer in panel.layers:
                new_data = dict(layer.data)
                # Swap x and y
                if "x" in new_data and "y" in new_data:
                    new_data["x"], new_data["y"] = new_data["y"], new_data["x"]
                elif "x" in new_data:
                    new_data["y"] = new_data.pop("x")
                elif "y" in new_data:
                    new_data["x"] = new_data.pop("y")
                new_layers.append(
                    ResolvedLayer(geom=layer.geom, data=new_data, params=layer.params)
                )
            new_panels.append(
                ResolvedPanel(label=panel.label, layers=new_layers, scales=panel.scales)
            )

        return ResolvedPlot(
            panels=new_panels,
            scales=new_scales,
            coord=resolved.coord,
            theme=resolved.theme,
            labs=resolved.labs,
            facet=resolved.facet,
            guides=resolved.guides,
        )


def coord_flip(
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> CoordFlip:
    """Create a flipped coordinate system."""
    return CoordFlip(xlim=xlim, ylim=ylim)
