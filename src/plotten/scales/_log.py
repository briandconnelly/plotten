from __future__ import annotations

import math

from plotten.scales._position import ScaleContinuous


class ScaleLog(ScaleContinuous):
    """Logarithmic scale for position aesthetics."""

    def __init__(self, aesthetic: str = "x", base: int = 10) -> None:
        super().__init__(aesthetic, expand=(0, 0))
        self._base = base

    def get_limits(self) -> tuple[float, float]:
        lo = self._domain_min if self._domain_min is not None else 1.0
        hi = self._domain_max if self._domain_max is not None else 10.0
        # Ensure positive
        lo = max(lo, 1e-10)
        hi = max(hi, lo * 10)
        return (lo, hi)

    def get_breaks(self) -> list:
        lo, hi = self.get_limits()
        log_lo = math.floor(math.log(lo, self._base))
        log_hi = math.ceil(math.log(hi, self._base))
        return [self._base**i for i in range(log_lo, log_hi + 1)]


def scale_x_log10() -> ScaleLog:
    """Set x-axis to a log-base-10 scale.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_log10
    >>> df = pd.DataFrame({"x": [1, 10, 100], "y": [1, 2, 3]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_log10()
    Plot(...)
    """
    return ScaleLog(aesthetic="x", base=10)


def scale_y_log10() -> ScaleLog:
    """Set y-axis to a log-base-10 scale.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_log10
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 10, 100]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_log10()
    Plot(...)
    """
    return ScaleLog(aesthetic="y", base=10)
