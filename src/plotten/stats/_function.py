from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


class StatFunction:
    """Stat that evaluates y = f(x) over an x grid."""

    required_aes: frozenset[str] = frozenset()

    def __init__(
        self,
        fun: Callable[[Any], Any],
        n: int = 101,
        xlim: tuple[float, float] | None = None,
    ) -> None:
        self._fun = fun
        self._n = n
        self._xlim = xlim

    def compute(self, df: Any) -> Any:
        import pandas as pd

        # Determine x range
        if self._xlim is not None:
            xmin, xmax = self._xlim
        else:
            try:
                import narwhals as nw

                frame = nw.from_native(df)
                if "x" in frame.columns:
                    col = frame.get_column("x")
                    xmin, xmax = col.min(), col.max()
                else:
                    xmin, xmax = 0.0, 1.0
            except (KeyError, TypeError):
                xmin, xmax = 0.0, 1.0

        x = np.linspace(xmin, xmax, self._n)
        y = self._fun(x)
        return pd.DataFrame({"x": x, "y": y})
