"""Identity scales — use data values directly as aesthetic values."""

from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import ScaleBase


class ScaleIdentity(ScaleBase):
    """Use data values directly as aesthetic values, with no transformation."""

    __slots__ = ("_guide", "_levels")

    def __init__(self, aesthetic: str, guide: str = "none") -> None:
        super().__init__(aesthetic)
        self._guide = guide

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        levels = s.unique().sort().to_list()
        if self._domain_min is None:
            self._levels: list = []
        for lev in levels:
            if lev not in self._levels:
                self._levels.append(lev)

    def map_data(self, values: Any) -> Any:
        # Identity: return data as-is (no transformation)
        return values

    def get_limits(self) -> tuple[float, float]:
        return (0, max(len(self._levels) - 1, 1))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        return [str(v) for v in self._levels]

    def legend_entries(self) -> list | None:
        if self._guide == "none":
            return None
        return None


def scale_color_identity(guide: str = "none") -> ScaleIdentity:
    """Map color aesthetic using data values directly as color specifications.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "c": ["red", "green", "blue"]})
    >>> ggplot(df, aes(x="x", y="y", color="c")) + geom_point() + scale_color_identity()
    Plot(...)
    """
    return ScaleIdentity("color", guide=guide)


def scale_fill_identity(guide: str = "none") -> ScaleIdentity:
    """Map fill aesthetic using data values directly as color specifications.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_identity
    >>> df = pd.DataFrame({"x": ["a", "b"], "y": [3, 5], "f": ["#ff0000", "#0000ff"]})
    >>> ggplot(df, aes(x="x", y="y", fill="f")) + geom_bar() + scale_fill_identity()
    Plot(...)
    """
    return ScaleIdentity("fill", guide=guide)


def scale_alpha_identity(guide: str = "none") -> ScaleIdentity:
    """Map alpha aesthetic using data values directly as opacity levels.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_alpha_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "a": [0.3, 0.6, 1.0]})
    >>> ggplot(df, aes(x="x", y="y", alpha="a")) + geom_point() + scale_alpha_identity()
    Plot(...)
    """
    return ScaleIdentity("alpha", guide=guide)


def scale_size_identity(guide: str = "none") -> ScaleIdentity:
    """Map size aesthetic using data values directly as point sizes.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_size_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "s": [2, 5, 10]})
    >>> ggplot(df, aes(x="x", y="y", size="s")) + geom_point() + scale_size_identity()
    Plot(...)
    """
    return ScaleIdentity("size", guide=guide)


def scale_shape_identity(guide: str = "none") -> ScaleIdentity:
    """Map shape aesthetic using data values directly as marker strings.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_shape_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "m": ["o", "s", "^"]})
    >>> ggplot(df, aes(x="x", y="y", shape="m")) + geom_point() + scale_shape_identity()
    Plot(...)
    """
    return ScaleIdentity("shape", guide=guide)


def scale_linetype_identity(guide: str = "none") -> ScaleIdentity:
    """Map linetype aesthetic using data values directly as linestyle strings.

    Parameters
    ----------
    guide : str, optional
        Legend guide type (default ``"none"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linetype_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "lt": ["solid", "dashed", "dotted"]})
    >>> ggplot(df, aes(x="x", y="y", linetype="lt")) + geom_line() + scale_linetype_identity()
    Plot(...)
    """
    return ScaleIdentity("linetype", guide=guide)
