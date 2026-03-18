from __future__ import annotations

from plotten.scales._position import ScaleContinuous


class ScaleReverse(ScaleContinuous):
    """Reversed scale for position aesthetics."""

    def __init__(self, aesthetic: str = "x", **kwargs) -> None:
        super().__init__(aesthetic, **kwargs)

    def get_limits(self) -> tuple[float, float]:
        lo, hi = super().get_limits()
        return (hi, lo)


def scale_x_reverse(**kwargs) -> ScaleReverse:
    """Create a reversed x scale."""
    return ScaleReverse(aesthetic="x", **kwargs)


def scale_y_reverse(**kwargs) -> ScaleReverse:
    """Create a reversed y scale."""
    return ScaleReverse(aesthetic="y", **kwargs)
