from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from plotten.scales._sec_axis import SecAxis

import narwhals as nw

from plotten.scales._base import ScaleBase


def _smart_format(value: float) -> str:
    """Format a number nicely: integers without decimals, others with ``:.6g``."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return f"{value:.6g}"


class ScaleContinuous(ScaleBase):
    """Linear scale for numeric position aesthetics."""

    __slots__ = ("_breaks", "_expand", "_labels", "_limits", "_padding", "_sec_axis")

    def __init__(
        self,
        aesthetic: str = "x",
        padding: float = 0.05,
        breaks: list[float] | Callable[[tuple[float, float]], list[float]] | None = None,
        limits: tuple[float, float] | None = None,
        labels: list[str] | Callable[[float], str] | None = None,
        expand: tuple[float, float] | None = None,
        sec_axis: SecAxis | None = None,
    ) -> None:
        from plotten._validation import validate_breaks_labels

        if not callable(labels) and not callable(breaks):
            validate_breaks_labels(breaks, labels)
        super().__init__(aesthetic)
        if expand is not None and padding != 0.05:
            from plotten._validation import ScaleError

            msg = "Cannot specify both 'padding' (non-default) and 'expand'"
            raise ScaleError(msg)
        self._expand = expand if expand is not None else (padding, 0)
        self._padding = padding
        self._breaks = breaks
        self._limits = limits
        self._labels = labels
        self._sec_axis = sec_axis
        self._domain_min: float | None = None
        self._domain_max: float | None = None

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        vmin = s.min()
        vmax = s.max()
        if self._domain_min is None or vmin < self._domain_min:
            self._domain_min = vmin
        if self._domain_max is None or vmax > self._domain_max:
            self._domain_max = vmax
        self._invalidate_cache()

    def map_data(self, values: Any) -> Any:
        return values  # identity — matplotlib handles position mapping

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return self._limits
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        span = hi - lo
        mult, add = self._expand
        pad = span * mult + add if span > 0 else 0.5
        return (lo - pad, hi + pad)

    def get_breaks(self) -> list:
        cached = self._cache.get("breaks")
        if cached is not None:
            return cached
        lo, hi = self.get_limits()
        if self._breaks is None:
            import numpy as np

            result = np.linspace(lo, hi, 6).tolist()
        elif callable(self._breaks):
            result = list(self._breaks((lo, hi)))  # type: ignore[operator]
        else:
            result = list(self._breaks)
        self._cache["breaks"] = result
        return result

    def get_labels(self) -> list[str]:
        cached = self._cache.get("labels")
        if cached is not None:
            return cached
        labels = self._labels
        if labels is None:
            result: list[str] = [_smart_format(b) for b in self.get_breaks()]
        elif isinstance(labels, list):
            result = list(labels)
        else:
            result = [labels(b) for b in self.get_breaks()]
        self._cache["labels"] = result
        return result


class ScaleDiscrete(ScaleBase):
    """Scale for categorical position aesthetics."""

    __slots__ = ("_expand", "_levels", "_manual_labels")

    def __init__(
        self,
        aesthetic: str = "x",
        labels: dict[str, str] | list[str] | None = None,
        expand: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_labels = labels
        self._expand = expand if expand is not None else (0, 0.6)

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        new_levels = s.unique().sort().to_list()
        for lev in new_levels:
            if lev not in self._levels:
                self._levels.append(lev)
        self._invalidate_cache()

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        mapping = {lev: i for i, lev in enumerate(self._levels)}
        return [mapping[v] for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        n = len(self._levels)
        if n == 0:
            return (-0.5, 0.5)
        mult, add = self._expand
        lo = -mult * (n - 1) - add
        hi = (n - 1) + mult * (n - 1) + add
        return (lo, hi)

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        cached = self._cache.get("labels")
        if cached is not None:
            return cached
        if self._manual_labels is not None:
            if isinstance(self._manual_labels, dict):
                result = [self._manual_labels.get(str(lev), str(lev)) for lev in self._levels]
            else:
                result = list(self._manual_labels)
        else:
            result = [str(lev) for lev in self._levels]
        self._cache["labels"] = result
        return result


def scale_x_continuous(**kwargs: Any) -> ScaleContinuous:
    """Set continuous x-axis scale with custom breaks, labels, or limits.

    Parameters
    ----------
    breaks : list of float or callable, optional
        Explicit tick positions or a function that receives limits.
    limits : tuple of float, optional
        Fixed ``(min, max)`` axis limits.
    labels : list of str or callable, optional
        Tick labels corresponding to ``breaks``.
    expand : tuple of float, optional
        Multiplicative and additive expansion ``(mult, add)``.

    Raises
    ------
    ScaleError
        If both ``padding`` and ``expand`` are specified.
        If ``breaks`` and ``labels`` have different lengths.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_continuous(limits=(0, 5))
    Plot(...)
    """
    return ScaleContinuous(aesthetic="x", **kwargs)


def scale_y_continuous(**kwargs: Any) -> ScaleContinuous:
    """Set continuous y-axis scale with custom breaks, labels, or limits.

    Parameters
    ----------
    breaks : list of float or callable, optional
        Explicit tick positions or a function that receives limits.
    limits : tuple of float, optional
        Fixed ``(min, max)`` axis limits.
    labels : list of str or callable, optional
        Tick labels corresponding to ``breaks``.
    expand : tuple of float, optional
        Multiplicative and additive expansion ``(mult, add)``.

    Raises
    ------
    ScaleError
        If both ``padding`` and ``expand`` are specified.
        If ``breaks`` and ``labels`` have different lengths.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_continuous(limits=(0, 10))
    Plot(...)
    """
    return ScaleContinuous(aesthetic="y", **kwargs)


def scale_x_discrete(**kwargs: Any) -> ScaleDiscrete:
    """Set discrete x-axis scale with custom labels or expansion.

    Parameters
    ----------
    labels : dict or list of str, optional
        Mapping from level names to display labels, or an ordered list.
    expand : tuple of float, optional
        Multiplicative and additive expansion ``(mult, add)``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_x_discrete
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_bar() + scale_x_discrete(labels={"a": "Alpha"})
    Plot(...)
    """
    return ScaleDiscrete(aesthetic="x", **kwargs)


def scale_y_discrete(**kwargs: Any) -> ScaleDiscrete:
    """Set discrete y-axis scale with custom labels or expansion.

    Parameters
    ----------
    labels : dict or list of str, optional
        Mapping from level names to display labels, or an ordered list.
    expand : tuple of float, optional
        Multiplicative and additive expansion ``(mult, add)``.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_y_discrete
    >>> df = pd.DataFrame({"x": [1, 4, 9], "y": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_bar() + scale_y_discrete()
    Plot(...)
    """
    return ScaleDiscrete(aesthetic="y", **kwargs)
