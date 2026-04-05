"""TOML serialization and deserialization for plotten themes."""

from __future__ import annotations

import functools
import tomllib
from dataclasses import fields as dc_fields
from enum import StrEnum
from pathlib import Path
from typing import Any, get_type_hints

from plotten.themes._elements import (
    ElementBlank,
    ElementLine,
    ElementRect,
    ElementText,
    Margin,
    Rel,
)
from plotten.themes._theme import Theme

# Built-in theme short names -> factory function names in _defaults
_BUILTIN_THEMES = {
    "default": "theme_default",
    "minimal": "theme_minimal",
    "dark": "theme_dark",
    "bw": "theme_bw",
    "classic": "theme_classic",
    "void": "theme_void",
    "gray": "theme_gray",
    "grey": "theme_grey",
    "538": "theme_538",
    "economist": "theme_economist",
    "tufte": "theme_tufte",
    "seaborn": "theme_seaborn",
    "linedraw": "theme_linedraw",
    "light": "theme_light",
    "test": "theme_test",
}


@functools.cache
def _build_hints() -> tuple[dict[str, Any], dict[str, type], frozenset[str]]:
    """Lazily resolve Theme type hints and classify fields."""
    # Theme uses `from __future__ import annotations`, so we must supply the
    # element types in the namespace for get_type_hints to resolve them.
    import plotten._enums as _enums
    import plotten.themes._elements as _elems

    ns = {**vars(_elems), **vars(_enums)}
    hints = get_type_hints(Theme, globalns=ns)
    element_fields: dict[str, type] = {}
    margin_fields: set[str] = set()
    for name, hint in hints.items():
        args = getattr(hint, "__args__", (hint,))
        for cls in (ElementText, ElementLine, ElementRect):
            if cls in args:
                element_fields[name] = cls
                break
        if Margin in args:
            margin_fields.add(name)
    return hints, element_fields, frozenset(margin_fields)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _parse_size(value: Any) -> float | Rel:
    """Parse a size value — plain number or ``{rel = 0.8}``."""
    if isinstance(value, dict) and "rel" in value:
        return Rel(factor=value["rel"])
    return value


def _parse_element(value: Any, element_cls: type) -> Any:
    """Convert a TOML table to an element dataclass."""
    if not isinstance(value, dict):
        return value  # scalar — pass through (e.g. str for panel_background)

    if value.get("blank", False):
        return ElementBlank()

    props = {k: v for k, v in value.items() if k != "blank"}

    # Resolve Rel in text size fields
    if "size" in props and element_cls is ElementText:
        props["size"] = _parse_size(props["size"])

    return element_cls(**props)


def _parse_margin(value: Any) -> Margin | tuple[float, ...] | float:
    """Parse a margin — number, 4-element array, or table with named sides."""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, list):
        return tuple(value)
    if isinstance(value, dict):
        return Margin(**value)
    return value


def theme_from_toml(path: str | Path) -> Theme:
    """Load a theme from a TOML file.

    The file may contain a ``base`` key naming a built-in theme
    (e.g. ``"minimal"``, ``"dark"``).  The remaining keys are layered
    on top of that base via :meth:`Theme.__add__`.

    Element fields are represented as TOML tables whose type is inferred
    from the :class:`Theme` field annotation.  Use ``blank = true``
    inside a table to represent :class:`ElementBlank`.

    Relative sizes use the inline-table form ``size = { rel = 0.8 }``.

    Margin fields accept a number, a 4-element array
    ``[top, right, bottom, left]``, or a table with named sides
    (``top``, ``right``, ``bottom``, ``left``, and optional ``unit``).

    Parameters
    ----------
    path : str or Path
        Path to the TOML file.

    Returns
    -------
    Theme
        The loaded theme.

    Raises
    ------
    ConfigError
        If the file contains invalid theme properties or an unknown
        base theme name.
    FileNotFoundError
        If the file does not exist.

    Examples
    --------
    A minimal TOML theme file::

        base = "minimal"
        base_size = 14
        font_family = "serif"

        [axis_title]
        size = 14
        color = "#333333"

        [axis_ticks]
        blank = true

        [plot_caption]
        size = { rel = 0.8 }
    """
    _THEME_HINTS, _ELEMENT_FIELDS, _MARGIN_FIELDS = _build_hints()
    path = Path(path)

    with path.open("rb") as f:
        data = tomllib.load(f)

    # --- base theme inheritance ---
    base_name = data.pop("base", None)
    base_theme: Theme | None = None
    if base_name is not None:
        if base_name not in _BUILTIN_THEMES:
            from plotten._validation import ConfigError

            valid = sorted(_BUILTIN_THEMES)
            msg = f"Unknown base theme: {base_name!r}. Valid base themes: {valid}"
            raise ConfigError(msg)
        from plotten.themes import _defaults

        factory = getattr(_defaults, _BUILTIN_THEMES[base_name])
        base_theme = factory()

    # --- validate keys ---
    valid_fields = {f.name for f in dc_fields(Theme)}
    invalid = set(data) - valid_fields
    if invalid:
        from plotten._validation import ConfigError

        msg = f"Unknown theme properties: {sorted(invalid)}"
        raise ConfigError(msg)

    # --- convert values ---
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        element_cls = _ELEMENT_FIELDS.get(key)

        if isinstance(value, dict) and element_cls is not None:
            kwargs[key] = _parse_element(value, element_cls)
        elif isinstance(value, dict) and key in _MARGIN_FIELDS:
            kwargs[key] = _parse_margin(value)
        elif isinstance(value, list):
            kwargs[key] = tuple(value)
        else:
            kwargs[key] = value

    theme_obj = Theme(**kwargs)

    if base_theme is not None:
        theme_obj = base_theme + theme_obj

    return theme_obj


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------

_TOML_SCALAR = (bool, int, float, str)


def _format_value(value: Any) -> str:
    """Format a single Python value as a TOML value literal."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # Ensure floats always have a decimal point for TOML compliance
        s = repr(value)
        return s
    if isinstance(value, str):
        # Escape backslashes and quotes for TOML basic strings
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, StrEnum):
        return f'"{value.value}"'
    if isinstance(value, (list, tuple)):
        items = ", ".join(_format_value(v) for v in value)
        return f"[{items}]"
    if isinstance(value, Rel):
        return f"{{ rel = {_format_value(value.factor)} }}"
    from plotten._validation import ExportError

    msg = f"Cannot serialize to TOML: {type(value).__name__}: {value!r}"
    raise ExportError(msg)


def _serialize_element(element: ElementText | ElementLine | ElementRect) -> dict[str, Any]:
    """Extract non-None fields from an element as a plain dict."""
    return {
        f.name: getattr(element, f.name)
        for f in dc_fields(element)
        if getattr(element, f.name) is not None
    }


def _commented_element_template(field_name: str, element_cls: type) -> str:
    """Return a commented-out TOML table showing available properties."""
    lines = [f"# [{field_name}]"]
    if element_cls is ElementText:
        lines.extend(
            [
                "# size =",
                "# color =",
                "# family =",
                "# weight =",
                "# style =",
                "# rotation =",
                "# ha =",
                "# va =",
            ]
        )
    elif element_cls is ElementLine:
        lines.extend(["# color =", "# size =", "# linetype ="])
    elif element_cls is ElementRect:
        lines.extend(["# fill =", "# color =", "# size ="])
    lines.append("# blank = false")
    return "\n".join(lines)


def theme_to_toml(
    theme_obj: Theme,
    path: str | Path,
    *,
    complete: bool = False,
) -> None:
    """Save a theme to a TOML file.

    By default only fields that differ from :class:`Theme` defaults are
    written, producing a minimal representation.  Pass ``complete=True``
    to emit every field — active fields are written normally while
    unused fields appear as commented-out lines showing the available
    properties.  This makes the output a ready-made template for
    developing a new theme.

    Parameters
    ----------
    theme_obj : Theme
        The theme to save.
    path : str or Path
        Destination file path.
    complete : bool, optional
        If ``True``, write all fields.  Unused fields appear
        commented-out as a reference.  Default ``False``.

    Examples
    --------
    >>> from plotten import theme_minimal, theme
    >>> t = theme_minimal() + theme(base_size=14, font_family="serif")
    >>> theme_to_toml(t, "my_theme.toml")

    Export a complete template for theme development:

    >>> theme_to_toml(t, "full_theme.toml", complete=True)

    Raises
    ------
    ExportError
        If a theme field value cannot be serialized to TOML.
    """
    _THEME_HINTS, _ELEMENT_FIELDS, _MARGIN_FIELDS = _build_hints()
    path = Path(path)
    default = Theme()

    scalars: list[str] = []
    tables: list[str] = []

    for f in dc_fields(Theme):
        value = getattr(theme_obj, f.name)
        is_default = value == getattr(default, f.name)
        element_cls = _ELEMENT_FIELDS.get(f.name)

        # --- value is None ---
        if value is None:
            if complete:
                if element_cls is not None:
                    tables.append("\n" + _commented_element_template(f.name, element_cls))
                elif f.name in _MARGIN_FIELDS:
                    tables.append(
                        f"\n# [{f.name}]\n# top =\n# right =\n# bottom =\n# left =\n# unit ="
                    )
                else:
                    scalars.append(f"# {f.name} =")
            continue

        # In minimal mode, skip values at their defaults
        if not complete and is_default:
            continue

        # --- emit the value ---
        if isinstance(value, ElementBlank):
            tables.append(f"\n[{f.name}]\nblank = true")
        elif isinstance(value, (ElementText, ElementLine, ElementRect)):
            props = _serialize_element(value)
            if props:
                lines = [f"\n[{f.name}]"]
                for k, v in props.items():
                    lines.append(f"{k} = {_format_value(v)}")
                tables.append("\n".join(lines))
        elif isinstance(value, Margin):
            lines = [f"\n[{f.name}]"]
            lines.append(f"top = {_format_value(value.top)}")
            lines.append(f"right = {_format_value(value.right)}")
            lines.append(f"bottom = {_format_value(value.bottom)}")
            lines.append(f"left = {_format_value(value.left)}")
            if value.unit != "npc":
                lines.append(f'unit = "{value.unit}"')
            tables.append("\n".join(lines))
        else:
            scalars.append(f"{f.name} = {_format_value(value)}")

    parts = []
    if scalars:
        parts.append("\n".join(scalars))
    if tables:
        parts.append("".join(tables))
    content = "\n".join(parts).strip() + "\n"

    path.write_text(content)
