from __future__ import annotations

from dataclasses import dataclass, fields


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


def _validate_element_kwargs(cls: type, factory_name: str, kwargs: dict) -> None:
    """Raise ConfigError if kwargs contain invalid field names."""
    valid = {f.name for f in fields(cls)}
    invalid = set(kwargs) - valid
    if invalid:
        from plotten._validation import ConfigError

        raise ConfigError(
            f"{factory_name}() got unexpected keyword argument(s): {sorted(invalid)}. "
            f"Valid fields: {sorted(valid)}"
        )


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
    _validate_element_kwargs(ElementText, "element_text", kwargs)
    return ElementText(**kwargs)


def element_line(**kwargs) -> ElementLine:
    """Create a line element."""
    _validate_element_kwargs(ElementLine, "element_line", kwargs)
    return ElementLine(**kwargs)


def element_rect(**kwargs) -> ElementRect:
    """Create a rect element."""
    _validate_element_kwargs(ElementRect, "element_rect", kwargs)
    return ElementRect(**kwargs)


def element_blank() -> ElementBlank:
    """Create a blank element that suppresses drawing."""
    return ElementBlank()


_Element = ElementText | ElementLine | ElementRect


def _merge_element[T: _Element](
    element: T | ElementBlank | None,
    base: T | ElementBlank | None,
    cls: type[T],
) -> T | ElementBlank | None:
    """Merge two theme elements, using the base for any None fields.

    ElementBlank on either side short-circuits: if *element* is blank it wins
    (suppresses drawing); if only *base* is blank it is ignored.
    """
    if isinstance(element, ElementBlank):
        return element
    if isinstance(base, ElementBlank):
        base = None
    if element is None:
        return base
    if base is None or not isinstance(base, cls):
        return element
    from dataclasses import fields

    merged = {
        f.name: (
            getattr(element, f.name)
            if getattr(element, f.name) is not None
            else getattr(base, f.name)
        )
        for f in fields(cls)
    }
    return cls(**merged)


def merge_text(
    element: ElementText | ElementBlank | None,
    base: ElementText | ElementBlank | None,
) -> ElementText | ElementBlank | None:
    """Merge a text element with a base, using the base for any None fields."""
    return _merge_element(element, base, ElementText)


def merge_line(
    element: ElementLine | ElementBlank | None,
    base: ElementLine | ElementBlank | None,
) -> ElementLine | ElementBlank | None:
    """Merge a line element with a base, using the base for any None fields."""
    return _merge_element(element, base, ElementLine)


def merge_rect(
    element: ElementRect | ElementBlank | None,
    base: ElementRect | ElementBlank | None,
) -> ElementRect | ElementBlank | None:
    """Merge a rect element with a base, using the base for any None fields."""
    return _merge_element(element, base, ElementRect)


def resolve_background(
    value: str | ElementRect | None,
) -> tuple[str | None, str | None, float | None]:
    """Extract (fill, border_color, border_width) from a background value.

    Accepts a plain color string (interpreted as fill) or an
    :class:`ElementRect` for full control.  Returns a 3-tuple of
    ``(fill, color, size)`` where any component may be ``None``.
    """
    if value is None:
        return None, None, None
    if isinstance(value, ElementRect):
        return value.fill, value.color, value.size
    return value, None, None


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
