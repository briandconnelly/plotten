from __future__ import annotations

import difflib
import warnings
from typing import Any


class PlottenError(Exception):
    """Custom exception with helpful messages for plotten users."""

    pass


def _suggest_columns(missing: set[str] | frozenset[str], data_columns: list[str]) -> str:
    """Suggest similar column names for missing aesthetics."""
    suggestions: list[str] = []
    for m in sorted(missing):
        matches = difflib.get_close_matches(m, data_columns, n=2, cutoff=0.6)
        if matches:
            suggestions.append(f"  '{m}' — did you mean {matches}?")
    return "\n" + "\n".join(suggestions) if suggestions else ""


def validate_required_aes(geom: Any, merged_aes: Any, data_columns: list[str]) -> None:
    """Raise PlottenError if required aesthetics are not satisfiable."""
    required = getattr(geom, "required_aes", frozenset())
    if not required:
        return

    available = set(data_columns)
    # Also count aesthetics that are mapped
    for field_name in merged_aes.__dataclass_fields__:
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
        raise PlottenError(
            f"{friendly} requires aesthetics {required}, "
            f"but {missing} {'is' if len(missing) == 1 else 'are'} "
            f"not mapped or present in data{hint}"
        )


def validate_data_type(aesthetic: str, series: Any, scale: Any) -> None:
    """Warn if continuous scale gets all-string data or vice versa."""
    import narwhals as nw

    from plotten.scales._position import ScaleContinuous, ScaleDiscrete

    s = nw.from_native(series, series_only=True)
    if isinstance(scale, ScaleContinuous) and not s.dtype.is_numeric():
        dtype_str = str(s.dtype).lower()
        if not any(t in dtype_str for t in ("date", "datetime", "timestamp")):
            warnings.warn(
                f"Continuous scale for '{aesthetic}' received non-numeric data "
                f"(dtype: {s.dtype}). Consider using a discrete scale.",
                stacklevel=4,
            )
    elif isinstance(scale, ScaleDiscrete) and s.dtype.is_numeric():
        warnings.warn(
            f"Discrete scale for '{aesthetic}' received numeric data "
            f"(dtype: {s.dtype}). Consider using a continuous scale.",
            stacklevel=4,
        )


def validate_breaks_labels(breaks: list | None, labels: list | None) -> None:
    """Raise PlottenError if breaks and labels have different lengths."""
    if breaks is not None and labels is not None and len(breaks) != len(labels):
        raise PlottenError(
            f"breaks (length {len(breaks)}) and labels (length {len(labels)}) "
            f"must have the same length"
        )
