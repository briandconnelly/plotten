"""Viridis family convenience scales."""

from __future__ import annotations

from plotten._enums import ViridisOption
from plotten.scales._color import ScaleColorContinuous

# Map ggplot2-style letter codes and names to matplotlib cmap names
_VIRIDIS_OPTIONS: dict[str, str] = {
    "viridis": "viridis",
    "magma": "magma",
    "inferno": "inferno",
    "plasma": "plasma",
    "cividis": "cividis",
    "A": "magma",
    "B": "inferno",
    "C": "plasma",
    "D": "viridis",
    "E": "cividis",
}


_LETTER_CODES = {"A", "B", "C", "D", "E"}


def _resolve_option(option: str) -> str:
    if option in _LETTER_CODES:
        from plotten._validation import plotten_deprecation_warn

        plotten_deprecation_warn(
            f"Single-letter viridis option code {option!r} is deprecated. "
            f"Use the full name {_VIRIDIS_OPTIONS[option]!r} instead.",
            stacklevel=3,
        )
    if option in _VIRIDIS_OPTIONS:
        return _VIRIDIS_OPTIONS[option]
    from plotten._validation import ScaleError

    msg = (
        f"Unknown viridis option: {option!r}. "
        f"Valid options: {sorted(k for k in _VIRIDIS_OPTIONS if len(k) > 1)}"
    )
    raise ScaleError(msg)


def scale_color_viridis(
    option: str | ViridisOption = ViridisOption.VIRIDIS, *, aesthetic: str = "color", **kwargs
) -> ScaleColorContinuous:
    """Map continuous color aesthetic using a viridis-family palette.

    Parameters
    ----------
    option : str, optional
        Palette variant: ``"viridis"``, ``"magma"``, ``"inferno"``,
        ``"plasma"``, or ``"cividis"`` (default ``"viridis"``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Raises
    ------
    ScaleError
        If *option* is not a recognized viridis palette name.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_viridis
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_viridis("magma")
    Plot(...)
    """
    return ScaleColorContinuous(aesthetic=aesthetic, cmap_name=_resolve_option(option), **kwargs)


def scale_fill_viridis(
    option: str | ViridisOption = ViridisOption.VIRIDIS, **kwargs
) -> ScaleColorContinuous:
    """Map continuous fill aesthetic using a viridis-family palette.

    Parameters
    ----------
    option : str, optional
        Palette variant: ``"viridis"``, ``"magma"``, ``"inferno"``,
        ``"plasma"``, or ``"cividis"`` (default ``"viridis"``).
    **kwargs
        Passed to the underlying scale (e.g. ``breaks``, ``limits``).

    Raises
    ------
    ScaleError
        If *option* is not a recognized viridis palette name.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_viridis
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_viridis("plasma")
    Plot(...)
    """
    return ScaleColorContinuous(aesthetic="fill", cmap_name=_resolve_option(option), **kwargs)
