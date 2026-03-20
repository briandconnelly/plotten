from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class GuideLegend:
    """Customization for discrete legends."""

    title: str | None = None
    nrow: int | None = None
    ncol: int | None = None
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
    nrow : int or None
        Number of rows in the legend layout.
    ncol : int or None
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


def guides(**kwargs: Any) -> dict[str, GuideLegend | GuideColorbar]:
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
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + guides(color=guide_legend(nrow=1))
    """
    return dict(kwargs)
