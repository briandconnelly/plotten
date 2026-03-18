from __future__ import annotations

from plotten.scales._position import ScaleContinuous


class ScaleSqrt(ScaleContinuous):
    """Square root scale for position aesthetics."""

    def __init__(self, aesthetic: str = "x", **kwargs) -> None:
        super().__init__(aesthetic, **kwargs)

    def get_limits(self) -> tuple[float, float]:
        lo, hi = super().get_limits()
        return (max(lo, 0), hi)


def scale_x_sqrt(**kwargs) -> ScaleSqrt:
    """Create a sqrt x scale."""
    return ScaleSqrt(aesthetic="x", **kwargs)


def scale_y_sqrt(**kwargs) -> ScaleSqrt:
    """Create a sqrt y scale."""
    return ScaleSqrt(aesthetic="y", **kwargs)
