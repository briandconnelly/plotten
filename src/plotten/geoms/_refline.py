from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomHLine:
    """Draw a horizontal reference line."""

    required_aes: frozenset[str] = frozenset()
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linestyle", "linewidth"})

    def __init__(self, yintercept: float, **kwargs: Any) -> None:
        self._yintercept = yintercept
        self._style = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axhline(self._yintercept, **kwargs)


class GeomVLine:
    """Draw a vertical reference line."""

    required_aes: frozenset[str] = frozenset()
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linestyle", "linewidth"})

    def __init__(self, xintercept: float, **kwargs: Any) -> None:
        self._xintercept = xintercept
        self._style = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axvline(self._xintercept, **kwargs)


class GeomAbLine:
    """Draw a line with given slope and intercept."""

    required_aes: frozenset[str] = frozenset()
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linestyle", "linewidth"})

    def __init__(self, slope: float, intercept: float, **kwargs: Any) -> None:
        self._slope = slope
        self._intercept = intercept
        self._style = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axline((0, self._intercept), slope=self._slope, **kwargs)
