from __future__ import annotations

from typing import Any

from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous


class ScaleGradient(ScaleColorContinuous):
    """Two-color linear gradient scale."""

    __slots__ = ("_high", "_low")

    def __init__(
        self,
        aesthetic: str = "color",
        low: str = "#132B43",
        high: str = "#56B1F7",
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        from matplotlib.colors import LinearSegmentedColormap

        super().__init__(aesthetic=aesthetic, cmap_name="viridis", breaks=breaks, limits=limits)
        self._low = low
        self._high = high
        self._cmap = LinearSegmentedColormap.from_list("gradient2", [low, high], N=256)

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


class ScaleGradient2(ScaleColorContinuous):
    """Diverging three-color gradient scale with a midpoint."""

    __slots__ = ("_high", "_low", "_mid", "_midpoint")

    def __init__(
        self,
        aesthetic: str = "color",
        low: str = "#67001F",
        mid: str = "#FFFFFF",
        high: str = "#053061",
        midpoint: float = 0,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        from matplotlib.colors import LinearSegmentedColormap

        super().__init__(aesthetic=aesthetic, cmap_name="viridis", breaks=breaks, limits=limits)
        self._low = low
        self._mid = mid
        self._high = high
        self._midpoint = midpoint
        self._cmap = LinearSegmentedColormap.from_list("gradient3", [low, mid, high], N=256)

    def map_data(self, values: Any) -> Any:
        import matplotlib.colors as mcolors
        import narwhals as nw

        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        mid = self._midpoint
        result = []
        for v in s.to_list():
            if v <= mid:
                span = mid - lo if mid != lo else 1.0
                norm = (v - lo) / span * 0.5
            else:
                span = hi - mid if hi != mid else 1.0
                norm = 0.5 + (v - mid) / span * 0.5
            norm = max(0.0, min(1.0, norm))
            result.append(mcolors.to_hex(self._cmap(norm)))
        return result

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        mid = self._midpoint
        entries = []
        for b in breaks:
            if b <= mid:
                span = mid - lo if mid != lo else 1.0
                norm = (b - lo) / span * 0.5
            else:
                span = hi - mid if hi != mid else 1.0
                norm = 0.5 + (b - mid) / span * 0.5
            norm = max(0.0, min(1.0, norm))
            hex_color = mcolors.to_hex(self._cmap(norm))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=f"{b:.3g}", fill=hex_color))
            else:
                entries.append(LegendEntry(label=f"{b:.3g}", color=hex_color))
        return entries


def scale_color_gradient(
    low: str = "#132B43", high: str = "#56B1F7", **kwargs: Any
) -> ScaleGradient:
    """Create a two-color sequential gradient for the color aesthetic.

    Parameters
    ----------
    low : str, optional
        Color for the low end of the gradient (default ``"#132B43"``).
    high : str, optional
        Color for the high end of the gradient (default ``"#56B1F7"``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_gradient
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_gradient("white", "red")
    Plot(...)
    """
    return ScaleGradient(aesthetic="color", low=low, high=high, **kwargs)


def scale_fill_gradient(
    low: str = "#132B43", high: str = "#56B1F7", **kwargs: Any
) -> ScaleGradient:
    """Create a two-color sequential gradient for the fill aesthetic.

    Parameters
    ----------
    low : str, optional
        Color for the low end of the gradient (default ``"#132B43"``).
    high : str, optional
        Color for the high end of the gradient (default ``"#56B1F7"``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_gradient
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_gradient("white", "blue")
    Plot(...)
    """
    return ScaleGradient(aesthetic="fill", low=low, high=high, **kwargs)


def scale_color_gradient2(
    low: str = "#67001F",
    mid: str = "#FFFFFF",
    high: str = "#053061",
    midpoint: float = 0,
    **kwargs: Any,
) -> ScaleGradient2:
    """Create a diverging three-color gradient for the color aesthetic.

    Parameters
    ----------
    low : str, optional
        Color for the low end (default ``"#67001F"``).
    mid : str, optional
        Color for the midpoint (default ``"#FFFFFF"``).
    high : str, optional
        Color for the high end (default ``"#053061"``).
    midpoint : float, optional
        Data value at the center of the diverging palette (default ``0``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_gradient2
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [-1, 0, 1]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_gradient2()
    Plot(...)
    """
    return ScaleGradient2(
        aesthetic="color", low=low, mid=mid, high=high, midpoint=midpoint, **kwargs
    )


def scale_fill_gradient2(
    low: str = "#67001F",
    mid: str = "#FFFFFF",
    high: str = "#053061",
    midpoint: float = 0,
    **kwargs: Any,
) -> ScaleGradient2:
    """Create a diverging three-color gradient for the fill aesthetic.

    Parameters
    ----------
    low : str, optional
        Color for the low end (default ``"#67001F"``).
    mid : str, optional
        Color for the midpoint (default ``"#FFFFFF"``).
    high : str, optional
        Color for the high end (default ``"#053061"``).
    midpoint : float, optional
        Data value at the center of the diverging palette (default ``0``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_gradient2
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [-1, 0, 1]})
    >>> ggplot(df, aes(x="x", y="y", fill="y")) + geom_bar() + scale_fill_gradient2()
    Plot(...)
    """
    return ScaleGradient2(
        aesthetic="fill", low=low, mid=mid, high=high, midpoint=midpoint, **kwargs
    )


class ScaleGradientN(ScaleColorContinuous):
    """Multi-stop gradient scale with arbitrary color stops."""

    __slots__ = ("_colors", "_values")

    def __init__(
        self,
        aesthetic: str = "color",
        colors: list[str] | None = None,
        values: list[float] | None = None,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        from matplotlib.colors import LinearSegmentedColormap

        if colors is None:
            colors = ["#132B43", "#56B1F7"]
        super().__init__(aesthetic=aesthetic, cmap_name="viridis", breaks=breaks, limits=limits)
        self._colors = colors
        self._values = values
        if values is not None:
            if len(values) != len(colors):
                msg = (
                    f"Length of values ({len(values)}) must match length of colors ({len(colors)})"
                )
                raise ValueError(msg)
            self._cmap = LinearSegmentedColormap.from_list(
                "gradientn",
                list(zip(values, [self._parse_color(c) for c in colors], strict=True)),
                N=256,
            )
        else:
            self._cmap = LinearSegmentedColormap.from_list("gradientn", colors, N=256)

    @staticmethod
    def _parse_color(color: str) -> tuple[float, ...]:
        import matplotlib.colors as mcolors

        return mcolors.to_rgba(color)

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


def scale_color_gradientn(
    colors: list[str] | None = None,
    values: list[float] | None = None,
    **kwargs: Any,
) -> ScaleGradientN:
    """Create a multi-stop color gradient scale.

    Parameters
    ----------
    colors : list of str
        List of colors (hex or named) for the gradient stops.
    values : list of float, optional
        Positions (0-1) for each color stop. If ``None``, colors are
        evenly spaced.
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_gradientn
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_gradientn(["red", "white", "blue"])
    Plot(...)
    """
    return ScaleGradientN(aesthetic="color", colors=colors, values=values, **kwargs)


def scale_fill_gradientn(
    colors: list[str] | None = None,
    values: list[float] | None = None,
    **kwargs: Any,
) -> ScaleGradientN:
    """Create a multi-stop fill gradient scale.

    Parameters
    ----------
    colors : list of str
        List of colors (hex or named) for the gradient stops.
    values : list of float, optional
        Positions (0-1) for each color stop. If ``None``, colors are
        evenly spaced.
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_gradientn
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_gradientn(["red", "white", "blue"])
    Plot(...)
    """
    return ScaleGradientN(aesthetic="fill", colors=colors, values=values, **kwargs)
