from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale, MappedDiscreteScale


class ScaleColorContinuous(MappedContinuousScale):
    """Map numeric values to a matplotlib colormap."""

    __slots__ = ("_cmap", "_cmap_name")

    def __init__(
        self,
        aesthetic: str = "color",
        cmap_name: str = "viridis",
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        import matplotlib

        super().__init__(aesthetic)
        self._cmap_name = cmap_name
        self._cmap = matplotlib.colormaps[cmap_name]
        self._breaks = breaks
        self._limits = limits

    def map_data(self, values: Any) -> Any:
        import matplotlib.colors as mcolors

        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        normalized = [(v - lo) / span for v in s.to_list()]
        return [mcolors.to_hex(self._cmap(n)) for n in normalized]

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


class ScaleColorDiscrete(MappedDiscreteScale):
    """Map categorical values to distinct colors."""

    __slots__ = ("_cmap", "_manual_values", "_palette_name")

    def __init__(
        self,
        aesthetic: str = "color",
        palette: str = "tab10",
        values: dict[str, str] | None = None,
    ) -> None:
        import matplotlib

        super().__init__(aesthetic)
        self._palette_name = palette
        self._cmap = matplotlib.colormaps[palette]
        self._levels: list = []
        self._manual_values = values

    def map_data(self, values: Any) -> Any:
        import matplotlib.colors as mcolors

        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [self._manual_values.get(str(v), "#000000") for v in s.to_list()]
        n = max(len(self._levels), 1)
        color_map = {
            lev: mcolors.to_hex(self._cmap(i / max(n - 1, 1)))
            for i, lev in enumerate(self._levels)
        }
        return [color_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        entries = []
        if self._manual_values:
            for lev in self._levels:
                hex_color = self._manual_values.get(str(lev), "#000000")
                if self.aesthetic == "fill":
                    entries.append(LegendEntry(label=str(lev), fill=hex_color))
                else:
                    entries.append(LegendEntry(label=str(lev), color=hex_color))
            return entries
        n = max(len(self._levels), 1)
        for i, lev in enumerate(self._levels):
            hex_color = mcolors.to_hex(self._cmap(i / max(n - 1, 1)))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=str(lev), fill=hex_color))
            else:
                entries.append(LegendEntry(label=str(lev), color=hex_color))
        return entries


def scale_color_continuous(cmap: str = "viridis") -> ScaleColorContinuous:
    """Map continuous values to a sequential color palette.

    Parameters
    ----------
    cmap : str, optional
        Matplotlib colormap name (default ``"viridis"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_continuous("plasma")
    Plot(...)
    """
    return ScaleColorContinuous(cmap_name=cmap)


def scale_color_discrete(palette: str = "tab10") -> ScaleColorDiscrete:
    """Map discrete values to distinct colors from a qualitative palette.

    Parameters
    ----------
    palette : str, optional
        Matplotlib qualitative colormap name (default ``"tab10"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_discrete
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + scale_color_discrete("Set2")
    Plot(...)
    """
    return ScaleColorDiscrete(palette=palette)


def scale_color_manual(values: dict[str, str]) -> ScaleColorDiscrete:
    """Create a discrete color scale with manually specified colors."""
    return ScaleColorDiscrete(values=values)


def scale_fill_manual(values: dict[str, str]) -> ScaleColorDiscrete:
    """Create a discrete fill scale with manually specified colors."""
    return ScaleColorDiscrete(aesthetic="fill", values=values)


def scale_fill_continuous(cmap: str = "viridis") -> ScaleColorContinuous:
    """Map continuous values to a sequential fill palette.

    Parameters
    ----------
    cmap : str, optional
        Matplotlib colormap name (default ``"viridis"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_continuous
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_continuous("plasma")
    Plot(...)
    """
    return ScaleColorContinuous(aesthetic="fill", cmap_name=cmap)


def scale_fill_discrete(palette: str = "tab10") -> ScaleColorDiscrete:
    """Map discrete values to distinct fill colors from a qualitative palette.

    Parameters
    ----------
    palette : str, optional
        Matplotlib qualitative colormap name (default ``"tab10"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_discrete
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y", fill="x")) + geom_bar() + scale_fill_discrete("Pastel1")
    Plot(...)
    """
    return ScaleColorDiscrete(aesthetic="fill", palette=palette)
