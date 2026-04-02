from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

    import narwhals as nw
    import narwhals.typing


class StatFunction:
    """Stat that evaluates y = f(x) over an x grid.

    Computed Variables
    ------------------
    x
        Evenly spaced x values over the specified range.
    y
        Function values f(x) at each x position.
    """

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

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        import narwhals as nw

        frame = cast("nw.DataFrame", nw.from_native(df))

        # Determine x range
        if self._xlim is not None:
            xmin, xmax = self._xlim
        else:
            try:
                if "x" in frame.columns:
                    col = frame.get_column("x")
                    xmin, xmax = col.min(), col.max()
                else:
                    xmin, xmax = 0.0, 1.0
            except (KeyError, TypeError) as e:
                from plotten._validation import plotten_warn

                plotten_warn(
                    f"Could not determine x range from data: {e}; defaulting to [0, 1]",
                    stacklevel=2,
                )
                xmin, xmax = 0.0, 1.0

        x = np.linspace(xmin, xmax, self._n)
        y = self._fun(x)
        result = {"x": x.tolist(), "y": y.tolist() if hasattr(y, "tolist") else list(y)}
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
