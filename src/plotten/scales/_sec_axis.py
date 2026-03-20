from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class SecAxis:
    """Secondary axis specification with forward and inverse transforms."""

    def __init__(
        self,
        trans: Callable[[Any], Any],
        inverse: Callable[[Any], Any],
        name: str | None = None,
        breaks: list[float] | None = None,
        labels: list[str] | None = None,
    ) -> None:
        self.trans = trans
        self.inverse = inverse
        self.name = name
        self.breaks = breaks
        self.labels = labels


def sec_axis(
    trans: Callable[[Any], Any],
    inverse: Callable[[Any], Any],
    name: str | None = None,
    **kwargs: Any,
) -> SecAxis:
    """Create a secondary axis with forward and inverse transforms.

    Parameters
    ----------
    trans : callable
        Forward transformation from primary to secondary axis values.
    inverse : callable
        Inverse transformation from secondary back to primary axis values.
    name : str, optional
        Label for the secondary axis.
    **kwargs
        Additional arguments such as ``breaks`` or ``labels``.

    Examples
    --------
    >>> from plotten import scale_y_continuous, sec_axis
    >>> scale_y_continuous(sec_axis=sec_axis(trans=lambda x: x * 1.8 + 32, inverse=lambda x: (x - 32) / 1.8, name="Fahrenheit"))
    ScaleContinuous(...)
    """
    return SecAxis(trans=trans, inverse=inverse, name=name, **kwargs)


def dup_axis(name: str | None = None) -> SecAxis:
    """Create a duplicate secondary axis mirroring the primary axis.

    Parameters
    ----------
    name : str, optional
        Label for the secondary axis.

    Examples
    --------
    >>> from plotten import scale_y_continuous, dup_axis
    >>> scale_y_continuous(sec_axis=dup_axis(name="Same scale"))
    ScaleContinuous(...)
    """
    return SecAxis(trans=lambda x: x, inverse=lambda x: x, name=name)
