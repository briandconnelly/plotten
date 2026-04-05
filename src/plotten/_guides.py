from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class GuideLegend:
    """Customization for discrete legends."""

    title: str | None = None
    n_rows: int | None = None
    n_cols: int | None = None
    reverse: bool = False
    override_aes: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GuideColorbar:
    """Customization for continuous colorbar legends."""

    title: str | None = None
    barwidth: float | None = None
    barheight: float | None = None
    nbin: int = 256
    reverse: bool = False


def guide_legend(**kwargs: Any) -> GuideLegend:
    """Configure the appearance of a discrete legend.

    Parameters
    ----------
    title : str or None
        Override the legend title.
    n_rows : int or None
        Number of rows in the legend layout.
    n_cols : int or None
        Number of columns in the legend layout.
    reverse : bool
        Whether to reverse the order of legend keys.
    override_aes : dict or None
        Aesthetic overrides applied to legend keys (e.g., ``{"size": 5}``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten._guides import guide_legend, guides
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + guides(color=guide_legend(title="Group"))
    """
    # Handle deprecated aliases
    if "nrow" in kwargs:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("nrow is deprecated. Use n_rows instead.")
        kwargs["n_rows"] = kwargs.pop("nrow")
    if "ncol" in kwargs:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn("ncol is deprecated. Use n_cols instead.")
        kwargs["n_cols"] = kwargs.pop("ncol")
    return GuideLegend(**kwargs)


def guide_colorbar(**kwargs: Any) -> GuideColorbar:
    """Configure the appearance of a continuous colorbar legend.

    Parameters
    ----------
    title : str or None
        Override the colorbar title.
    barwidth : float or None
        Width of the colorbar in points.
    barheight : float or None
        Height of the colorbar in points.
    nbin : int
        Number of discrete bins used to render the gradient.
    reverse : bool
        Whether to reverse the direction of the colorbar.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten._guides import guide_colorbar, guides
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + guides(color=guide_colorbar(title="Value"))
    """
    return GuideColorbar(**kwargs)


class Guides(dict):
    """Guide specifications for aesthetics.

    A dict subclass mapping aesthetic names (``"color"``, ``"fill"``, etc.)
    to :class:`GuideLegend` or :class:`GuideColorbar` objects.

    Mutation methods are disabled — use ``Guides({**existing, **new})`` to
    create an updated copy.
    """

    _frozen = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._frozen = True

    def _raise_immutable(self) -> None:
        if self._frozen:
            raise TypeError("Guides is immutable; create a new Guides instead")

    def __setitem__(self, key: Any, value: Any) -> None:
        self._raise_immutable()
        super().__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        self._raise_immutable()
        super().__delitem__(key)

    def pop(self, *args: Any) -> Any:
        self._raise_immutable()
        return super().pop(*args)

    def update(self, *args: Any, **kwargs: Any) -> None:
        self._raise_immutable()
        super().update(*args, **kwargs)

    def clear(self) -> None:
        self._raise_immutable()
        super().clear()

    def setdefault(self, key: Any, default: Any = None) -> Any:
        self._raise_immutable()
        return super().setdefault(key, default)

    def __repr__(self) -> str:
        items = ", ".join(f"{k}={v!r}" for k, v in self.items())
        return f"Guides({items})"


def guides(**kwargs: Any) -> Guides:
    """Set guide specifications for one or more aesthetics.

    Parameters
    ----------
    **kwargs
        Keyword arguments mapping aesthetic names to guide objects created by
        :func:`guide_legend` or :func:`guide_colorbar`.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten._guides import guide_legend, guides
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + guides(color=guide_legend(n_rows=1))
    """
    return Guides(kwargs)
