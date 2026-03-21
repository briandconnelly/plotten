from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rel:
    """Relative size multiplier.

    When used as the ``size`` of an :class:`ElementText`, the final font
    size is ``factor * default_size`` where *default_size* comes from the
    theme hierarchy.
    """

    factor: float


def rel(factor: float) -> Rel:
    """Create a relative size multiplier.

    Parameters
    ----------
    factor : float
        Multiplicative factor applied to the parent element's default
        size.  For example, ``rel(0.8)`` means 80 % of the default.

    Examples
    --------
    >>> from plotten.themes import element_text, rel
    >>> element_text(size=rel(1.2))
    ElementText(size=Rel(factor=1.2), ...)
    """
    return Rel(factor)


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementText:
    """Theme element for text."""

    size: float | Rel | None = None
    color: str | None = None
    family: str | None = None
    weight: str | None = None
    style: str | None = None
    rotation: float | None = None
    ha: str | float | None = None
    va: str | float | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementLine:
    """Theme element for lines."""

    color: str | None = None
    size: float | None = None
    linetype: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ElementRect:
    """Theme element for rectangles."""

    fill: str | None = None
    color: str | None = None
    size: float | None = None


@dataclass(frozen=True, slots=True)
class ElementBlank:
    """Suppresses drawing of the element."""

    pass


def element_text(**kwargs) -> ElementText:
    """Create a text element.

    Accepts ``hjust`` / ``vjust`` as aliases for ``ha`` / ``va``
    (ggplot2 convention).  Numeric values (0-1) are translated:
    ``hjust``: 0 = left, 0.5 = center, 1 = right.
    ``vjust``: 0 = bottom, 0.5 = center, 1 = top.
    """
    if "hjust" in kwargs:
        kwargs.setdefault("ha", kwargs.pop("hjust"))
    if "vjust" in kwargs:
        kwargs.setdefault("va", kwargs.pop("vjust"))
    return ElementText(**kwargs)


def element_line(**kwargs) -> ElementLine:
    """Create a line element."""
    return ElementLine(**kwargs)


def element_rect(**kwargs) -> ElementRect:
    """Create a rect element."""
    return ElementRect(**kwargs)


def element_blank() -> ElementBlank:
    """Create a blank element that suppresses drawing."""
    return ElementBlank()


def merge_text(element: ElementText | None, base: ElementText | None) -> ElementText | None:
    """Merge a text element with a base, using the base for any None fields."""
    if element is None:
        return base
    if base is None:
        return element
    return ElementText(
        size=element.size if element.size is not None else base.size,
        color=element.color if element.color is not None else base.color,
        family=element.family if element.family is not None else base.family,
        weight=element.weight if element.weight is not None else base.weight,
        style=element.style if element.style is not None else base.style,
        rotation=element.rotation if element.rotation is not None else base.rotation,
        ha=element.ha if element.ha is not None else base.ha,
        va=element.va if element.va is not None else base.va,
    )


def merge_line(element: ElementLine | None, base: ElementLine | None) -> ElementLine | None:
    """Merge a line element with a base, using the base for any None fields."""
    if element is None:
        return base
    if base is None:
        return element
    return ElementLine(
        color=element.color if element.color is not None else base.color,
        size=element.size if element.size is not None else base.size,
        linetype=element.linetype if element.linetype is not None else base.linetype,
    )


def merge_rect(element: ElementRect | None, base: ElementRect | None) -> ElementRect | None:
    """Merge a rect element with a base, using the base for any None fields."""
    if element is None:
        return base
    if base is None:
        return element
    return ElementRect(
        fill=element.fill if element.fill is not None else base.fill,
        color=element.color if element.color is not None else base.color,
        size=element.size if element.size is not None else base.size,
    )


@dataclass(frozen=True, slots=True)
class Margin:
    """Margin specification with optional unit.

    When used as ``plot_margin`` in a theme, the four sides are specified
    in the given ``unit``.

    Supported units:

    * ``"npc"`` — normalised parent coordinates (0-1), used directly.
    * ``"in"`` — inches, converted using figure size at render time.
    * ``"cm"`` — centimetres, converted via inches.
    * ``"mm"`` — millimetres, converted via inches.
    """

    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0
    unit: str = "npc"

    def to_npc(self, fig_width: float, fig_height: float) -> tuple[float, float, float, float]:
        """Convert to normalised parent coordinates.

        Parameters
        ----------
        fig_width : float
            Figure width in inches.
        fig_height : float
            Figure height in inches.

        Returns
        -------
        tuple of float
            ``(top, right, bottom, left)`` in NPC (0-1).
        """
        if self.unit == "npc":
            return (self.top, self.right, self.bottom, self.left)

        # Convert to inches first
        scale = {"in": 1.0, "cm": 1 / 2.54, "mm": 1 / 25.4}.get(self.unit)
        if scale is None:
            from plotten._validation import ConfigError

            msg = f"Unknown margin unit: {self.unit!r}. Use 'npc', 'in', 'cm', or 'mm'."
            raise ConfigError(msg)

        return (
            self.top * scale / fig_height,
            self.right * scale / fig_width,
            self.bottom * scale / fig_height,
            self.left * scale / fig_width,
        )


def margin(
    top: float = 0,
    right: float = 0,
    bottom: float = 0,
    left: float = 0,
    unit: str = "npc",
) -> Margin:
    """Create a margin specification.

    Parameters
    ----------
    top : float, optional
        Top margin (default 0).
    right : float, optional
        Right margin (default 0).
    bottom : float, optional
        Bottom margin (default 0).
    left : float, optional
        Left margin (default 0).
    unit : str, optional
        Unit for values: ``"npc"`` (default), ``"in"``, ``"cm"``, or
        ``"mm"``.

    Examples
    --------
    >>> from plotten import theme, margin
    >>> theme(plot_margin=margin(0.05, 0.05, 0.05, 0.05))
    Theme(...)
    """
    return Margin(top=top, right=right, bottom=bottom, left=left, unit=unit)
