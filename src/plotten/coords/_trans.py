"""Coordinate transformation with arbitrary functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import numpy as np


@dataclass(frozen=True, slots=True)
class CoordTrans:
    """Apply arbitrary transformations to x and/or y axes."""

    x: str | Callable = "identity"
    y: str | Callable = "identity"

    def transform(self, data: Any, ax: Any) -> Any:
        """No-op axes adjustment (limits are handled elsewhere)."""
        return data

    def transform_data(self, data: dict, scales: dict) -> dict:
        """Transform data coordinates."""
        result = dict(data)
        if "x" in result:
            result["x"] = self._apply(result["x"], self.x)
        if "y" in result:
            result["y"] = self._apply(result["y"], self.y)
        # Also transform endpoint aesthetics (for segments, etc.)
        if "xend" in result:
            result["xend"] = self._apply(result["xend"], self.x)
        if "yend" in result:
            result["yend"] = self._apply(result["yend"], self.y)
        return result

    def _apply(self, values: Any, trans: str | Callable) -> list:
        if trans == "identity":
            return values
        if callable(trans):
            if isinstance(values, list):
                return [trans(v) for v in values]  # type: ignore[operator]
            return trans(values)  # type: ignore[operator]
        # Named transforms
        fn = _TRANSFORMS.get(trans)
        if fn is None:
            msg = f"Unknown transform: {trans!r}. Available: {sorted(_TRANSFORMS)}"
            raise ValueError(msg)
        if isinstance(values, list):
            return [fn(v) for v in values]
        return fn(values)


_TRANSFORMS: dict[str, Callable] = {
    "identity": lambda x: x,
    "log10": lambda x: np.log10(x) if x > 0 else float("nan"),
    "sqrt": lambda x: np.sqrt(x) if x >= 0 else float("nan"),
    "reverse": lambda x: -x,
    "exp": lambda x: np.exp(x),
    "reciprocal": lambda x: 1 / x if x != 0 else float("nan"),
}


def coord_trans(
    x: str | Callable = "identity",
    y: str | Callable = "identity",
) -> CoordTrans:
    """Create a coordinate transformation.

    Parameters
    ----------
    x, y : str or callable
        Transformation for each axis. Built-in options: "identity", "log10",
        "sqrt", "reverse", "exp", "reciprocal". Or pass a callable.
    """
    return CoordTrans(x=x, y=y)
