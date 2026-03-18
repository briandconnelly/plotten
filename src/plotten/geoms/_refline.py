from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomHLine(GeomBase):
    """Draw a horizontal reference line."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, yintercept: float, **kwargs: Any) -> None:
        self._yintercept = yintercept
        self._style = kwargs

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axhline(self._yintercept, **kwargs)


class GeomVLine(GeomBase):
    """Draw a vertical reference line."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, xintercept: float, **kwargs: Any) -> None:
        self._xintercept = xintercept
        self._style = kwargs

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axvline(self._xintercept, **kwargs)


class GeomAbLine(GeomBase):
    """Draw a line with given slope and intercept."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, slope: float, intercept: float, **kwargs: Any) -> None:
        self._slope = slope
        self._intercept = intercept
        self._style = kwargs

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        for key in ("color", "linestyle", "linewidth", "alpha"):
            if key in params:
                kwargs[key] = params[key]
            elif key in self._style:
                kwargs[key] = self._style[key]
        ax.axline((0, self._intercept), slope=self._slope, **kwargs)
