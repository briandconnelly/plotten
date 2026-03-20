from __future__ import annotations

from typing import Any

from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete


class ScaleBrewerDiscrete(ScaleColorDiscrete):
    """Discrete ColorBrewer palette scale."""

    __slots__ = ("_direction",)

    def __init__(
        self,
        aesthetic: str = "color",
        palette: str = "Set1",
        direction: int = 1,
    ) -> None:
        super().__init__(aesthetic=aesthetic, palette=palette)
        self._direction = direction

    def map_data(self, values: Any) -> Any:
        import matplotlib.colors as mcolors
        import narwhals as nw

        s = nw.from_native(values, series_only=True)
        n = max(len(self._levels), 1)
        indices = list(range(n))
        if self._direction == -1:
            indices = indices[::-1]
        color_map = {
            lev: mcolors.to_hex(self._cmap(indices[i] / max(n - 1, 1)))
            for i, lev in enumerate(self._levels)
        }
        return [color_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        n = max(len(self._levels), 1)
        indices = list(range(n))
        if self._direction == -1:
            indices = indices[::-1]
        entries = []
        for i, lev in enumerate(self._levels):
            hex_color = mcolors.to_hex(self._cmap(indices[i] / max(n - 1, 1)))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=str(lev), fill=hex_color))
            else:
                entries.append(LegendEntry(label=str(lev), color=hex_color))
        return entries


class ScaleBrewerContinuous(ScaleColorContinuous):
    """Continuous ColorBrewer palette scale (distiller)."""

    __slots__ = ("_direction",)

    def __init__(
        self,
        aesthetic: str = "color",
        palette: str = "RdYlBu",
        direction: int = 1,
    ) -> None:
        import matplotlib

        super().__init__(aesthetic=aesthetic, cmap_name=palette)
        self._direction = direction
        if direction == -1:
            self._cmap = matplotlib.colormaps[palette].reversed()

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        entries = []
        for b in breaks:
            norm = (b - lo) / span
            hex_color = mcolors.to_hex(self._cmap(norm))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=f"{b:.3g}", fill=hex_color))
            else:
                entries.append(LegendEntry(label=f"{b:.3g}", color=hex_color))
        return entries


def scale_color_brewer(palette: str = "Set1", direction: int = 1) -> ScaleBrewerDiscrete:
    """Map discrete color aesthetic using ColorBrewer palettes.

    Parameters
    ----------
    palette : str, optional
        ColorBrewer palette name (default ``"Set1"``).
    direction : int, optional
        Direction of the palette. Use ``1`` for normal order and ``-1``
        for reversed (default ``1``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_brewer
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + scale_color_brewer("Set2")
    Plot(...)
    """
    return ScaleBrewerDiscrete(aesthetic="color", palette=palette, direction=direction)


def scale_fill_brewer(palette: str = "Set1", direction: int = 1) -> ScaleBrewerDiscrete:
    """Map discrete fill aesthetic using ColorBrewer palettes.

    Parameters
    ----------
    palette : str, optional
        ColorBrewer palette name (default ``"Set1"``).
    direction : int, optional
        Direction of the palette. Use ``1`` for normal order and ``-1``
        for reversed (default ``1``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_brewer
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y", fill="x")) + geom_bar() + scale_fill_brewer("Pastel1")
    Plot(...)
    """
    return ScaleBrewerDiscrete(aesthetic="fill", palette=palette, direction=direction)


def scale_color_distiller(palette: str = "RdYlBu", direction: int = 1) -> ScaleBrewerContinuous:
    """Map continuous color aesthetic using a ColorBrewer sequential palette.

    Parameters
    ----------
    palette : str, optional
        ColorBrewer palette name (default ``"RdYlBu"``).
    direction : int, optional
        Direction of the palette. Use ``1`` for normal order and ``-1``
        for reversed (default ``1``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_distiller
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_distiller("Blues")
    Plot(...)
    """
    return ScaleBrewerContinuous(aesthetic="color", palette=palette, direction=direction)


def scale_fill_distiller(palette: str = "RdYlBu", direction: int = 1) -> ScaleBrewerContinuous:
    """Map continuous fill aesthetic using a ColorBrewer sequential palette.

    Parameters
    ----------
    palette : str, optional
        ColorBrewer palette name (default ``"RdYlBu"``).
    direction : int, optional
        Direction of the palette. Use ``1`` for normal order and ``-1``
        for reversed (default ``1``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_distiller
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_distiller("Blues")
    Plot(...)
    """
    return ScaleBrewerContinuous(aesthetic="fill", palette=palette, direction=direction)
