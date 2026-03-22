from __future__ import annotations

import difflib
import warnings
from dataclasses import fields
from typing import Any

_strict_mode: bool = False


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class PlottenError(Exception):
    """Base exception for all plotten errors.

    Catch this to handle any plotten error. Use subclasses for
    fine-grained handling.
    """


class ValidationError(PlottenError):
    """Invalid parameter values or aesthetic checks.

    Raised when a geom receives an unknown parameter, an aesthetic value
    is invalid (bad color, shape, linetype), or alpha/size are out of range.
    """


class DataError(PlottenError):
    """Data-related errors.

    Raised when mapped columns are missing from the data, required
    aesthetics are not satisfiable, or data contains only non-finite values.
    """


class ScaleError(PlottenError):
    """Scale configuration errors.

    Raised for unknown scale options (e.g. viridis palette), mismatched
    breaks/labels lengths, or conflicting scale parameters.
    """


class StatError(PlottenError):
    """Statistical transformation errors.

    Raised for unknown stat methods, summary functions, or statistical
    test names.
    """


class RenderError(PlottenError):
    """Errors during plot rendering.

    Wraps matplotlib exceptions that occur during ``geom.draw()`` with
    context about which geom, data keys, and params were involved.
    """


class ConfigError(PlottenError):
    """Configuration and setup errors.

    Raised for unknown theme properties, invalid margin units, unknown
    arrow styles, annotation types, or conflicting aes arguments.
    """


class FontError(PlottenError):
    """Font registration and loading errors.

    Raised when a font file is not found, has an unsupported format,
    or a Google Font download fails.
    """


class ExportError(PlottenError):
    """Export-related errors.

    Raised when a feature (geom, coord, mapping) is not supported by
    the target export format (e.g. Vega-Lite).
    """


class SpecError(PlottenError):
    """Spec format errors.

    Raised when a plot spec dict has invalid structure, unknown registry
    keys, or missing required fields.
    """


# ---------------------------------------------------------------------------
# Warning infrastructure
# ---------------------------------------------------------------------------


class PlottenWarning(UserWarning):
    """Warning category for recoverable plotten issues."""


def set_strict(enabled: bool = True) -> None:
    """Enable or disable strict mode.

    In strict mode, all :class:`PlottenWarning` warnings are raised as
    :class:`ValidationError` exceptions instead. This is useful for AI agents
    and CI pipelines that need hard failures rather than silent warnings.
    """
    global _strict_mode
    _strict_mode = enabled


def plotten_warn(message: str, *, stacklevel: int = 2) -> None:
    """Issue a :class:`PlottenWarning`, or raise :class:`ValidationError` in strict mode."""
    if _strict_mode:
        raise ValidationError(message)
    warnings.warn(message, PlottenWarning, stacklevel=stacklevel + 1)


# ---------------------------------------------------------------------------
# Data validation helpers
# ---------------------------------------------------------------------------


def _suggest_columns(missing: set[str] | frozenset[str], data_columns: list[str]) -> str:
    """Suggest similar column names for missing aesthetics."""
    suggestions: list[str] = []
    for m in sorted(missing):
        matches = difflib.get_close_matches(m, data_columns, n=2, cutoff=0.6)
        if matches:
            suggestions.append(f"  '{m}' — did you mean {matches}?")
    return "\n" + "\n".join(suggestions) if suggestions else ""


def validate_required_aes(geom: Any, merged_aes: Any, data_columns: list[str]) -> None:
    """Raise DataError if required aesthetics are not satisfiable."""
    required = getattr(geom, "required_aes", frozenset())
    if not required:
        return

    available = set(data_columns)
    # Also count aesthetics that are mapped
    for field_name in (f.name for f in fields(merged_aes)):
        col = getattr(merged_aes, field_name)
        if col is not None:
            available.add(field_name)

    missing = required - available
    if missing:
        geom_name = type(geom).__name__
        # Convert class name like GeomPoint -> geom_point
        friendly = geom_name.replace("Geom", "geom_").lower()
        if friendly.startswith("_"):
            friendly = friendly[1:]
        hint = _suggest_columns(missing, data_columns)
        raise DataError(
            f"{friendly} requires aesthetics {required}, "
            f"but {missing} {'is' if len(missing) == 1 else 'are'} "
            f"not mapped or present in data{hint}"
        )


def validate_mapped_columns(
    mappings: dict[str, str],
    data_columns: list[str],
    required_aes: frozenset[str] | None = None,
) -> None:
    """Raise DataError if mapped column names are not present in the data.

    Only checks aesthetics listed in *required_aes* (if provided) to avoid
    false positives for literal values like ``aes(fill='steelblue')``.
    Uses ``difflib.get_close_matches`` to suggest similar column names.
    """
    missing = {
        col_name: aes_field
        for aes_field, col_name in mappings.items()
        if col_name not in data_columns
        and col_name != aes_field
        and (required_aes is None or aes_field in required_aes)
    }
    if not missing:
        return

    parts: list[str] = []
    for col_name, aes_field in sorted(missing.items()):
        matches = difflib.get_close_matches(col_name, data_columns, n=2, cutoff=0.6)
        hint = f" Did you mean {matches}?" if matches else ""
        parts.append(
            f"  aes({aes_field}='{col_name}') — column '{col_name}' not found in data.{hint}"
        )
    raise DataError(
        "Column(s) referenced in aesthetic mapping not found in data:\n"
        + "\n".join(parts)
        + f"\nAvailable columns: {sorted(data_columns)}"
    )


def validate_data_type(
    aesthetic: str, series: Any, scale: Any, *, column_name: str | None = None
) -> None:
    """Warn if continuous scale gets all-string data or vice versa."""
    import narwhals as nw

    from plotten.scales._position import ScaleContinuous, ScaleDiscrete

    s = nw.from_native(series, series_only=True)
    col_info = f" (column '{column_name}')" if column_name else ""
    if isinstance(scale, ScaleContinuous) and not s.dtype.is_numeric():
        if not s.dtype.is_temporal():
            plotten_warn(
                f"Continuous scale for '{aesthetic}'{col_info} received "
                f"non-numeric data (dtype: {s.dtype}). "
                f"Consider using a discrete scale.",
                stacklevel=4,
            )
    elif isinstance(scale, ScaleDiscrete) and s.dtype.is_numeric():
        plotten_warn(
            f"Discrete scale for '{aesthetic}'{col_info} received "
            f"numeric data (dtype: {s.dtype}). "
            f"Consider using a continuous scale.",
            stacklevel=4,
        )


def validate_breaks_labels(breaks: list | None, labels: list | None) -> None:
    """Raise ScaleError if breaks and labels have different lengths."""
    if breaks is not None and labels is not None and len(breaks) != len(labels):
        raise ScaleError(
            f"breaks (length {len(breaks)}) and labels (length {len(labels)}) "
            f"must have the same length"
        )


# ---------------------------------------------------------------------------
# Geom parameter validation
# ---------------------------------------------------------------------------

_VALID_SHAPES: frozenset[str] = frozenset(
    {
        "o",
        "v",
        "^",
        "<",
        ">",
        "s",
        "p",
        "P",
        "*",
        "h",
        "H",
        "+",
        "x",
        "X",
        "D",
        "d",
        "|",
        "_",
        ".",
        ",",
        "1",
        "2",
        "3",
        "4",
        "8",
    }
)

_VALID_LINETYPES: frozenset[str] = frozenset(
    {"solid", "dashed", "dotted", "dashdot", "-", "--", "-.", ":", "none", "None", ""}
)

_VALID_HATCHES: frozenset[str] = frozenset(
    {
        "/",
        "\\",
        "|",
        "-",
        "+",
        "x",
        "o",
        "O",
        ".",
        "*",
        "//",
        "\\\\",
        "||",
        "--",
        "++",
        "xx",
        "oo",
        "OO",
        "..",
        "**",
    }
)


def validate_geom_params(
    geom_name: str,
    params: dict[str, Any],
    known_params: frozenset[str],
) -> None:
    """Warn on unknown geom parameters with typo suggestions."""
    unknown = set(params) - known_params
    if not unknown:
        return

    parts: list[str] = []
    for name in sorted(unknown):
        matches = difflib.get_close_matches(name, sorted(known_params), n=2, cutoff=0.5)
        if matches:
            parts.append(f"  '{name}' — did you mean {matches}?")
        else:
            parts.append(f"  '{name}'")
    plotten_warn(
        f"{geom_name} received unknown parameter(s):\n"
        + "\n".join(parts)
        + f"\nValid parameters: {sorted(known_params)}",
        stacklevel=3,
    )


def validate_aesthetic_value(name: str, value: Any) -> None:
    """Warn if a fixed aesthetic value is invalid."""
    if name == "shape" and isinstance(value, str) and value not in _VALID_SHAPES:
        plotten_warn(
            f"Invalid shape value: {value!r}. Valid shapes: {sorted(_VALID_SHAPES)}",
            stacklevel=3,
        )
    elif name == "linetype" and isinstance(value, str) and value not in _VALID_LINETYPES:
        matches = difflib.get_close_matches(value, sorted(_VALID_LINETYPES), n=2, cutoff=0.5)
        hint = f" Did you mean {matches}?" if matches else ""
        plotten_warn(
            f"Invalid linetype value: {value!r}.{hint} "
            f"Valid linetypes: {sorted(_VALID_LINETYPES)}",
            stacklevel=3,
        )
    elif name == "hatch" and isinstance(value, str) and value not in _VALID_HATCHES:
        plotten_warn(
            f"Invalid hatch value: {value!r}. Valid hatches: {sorted(_VALID_HATCHES)}",
            stacklevel=3,
        )


def validate_color(value: Any) -> None:
    """Warn if a color value is not recognized by matplotlib."""
    if not isinstance(value, str):
        return
    # Skip "none" (transparent) — always valid
    if value.lower() == "none":
        return
    try:
        from matplotlib.colors import CSS4_COLORS, to_rgba

        to_rgba(value)
    except (ValueError, KeyError):
        matches = difflib.get_close_matches(value, list(CSS4_COLORS), n=3, cutoff=0.6)
        hint = f" Did you mean {matches}?" if matches else ""
        plotten_warn(
            f"Invalid color value: {value!r}. "
            f"Must be a named color, hex code, or RGB tuple.{hint}",
            stacklevel=3,
        )


def validate_alpha(value: Any) -> None:
    """Warn if alpha is outside [0, 1]."""
    if isinstance(value, int | float) and not (0 <= value <= 1):
        plotten_warn(
            f"Alpha value {value} is outside the valid range [0, 1].",
            stacklevel=3,
        )


def validate_size(value: Any) -> None:
    """Warn if size is negative."""
    if isinstance(value, int | float) and value < 0:
        plotten_warn(
            f"Size value {value} is negative.",
            stacklevel=3,
        )
