"""Shared drawing utilities for geom implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plotten._types import GeomDrawData, GeomParams


def scalar[T](values: list[T] | T) -> T:
    """First element if list, else pass through."""
    if isinstance(values, list):
        return values[0]
    return values


def extract_aesthetic(
    data: GeomDrawData,
    key: str,
    params: GeomParams,
    *,
    as_scalar: bool = False,
    param_key: str | None = None,
) -> Any:
    """Get aesthetic from data with fallback to params.

    *param_key* allows looking up a different key in params (e.g. ``linetype`` →
    ``linestyle``).
    """
    pk = param_key if param_key is not None else key
    if key in data:
        val = data[key]  # type: ignore[literal-required]
        return scalar(val) if as_scalar else val
    return params.get(pk)


def extract_fill_or_color(
    data: GeomDrawData,
    params: GeomParams | None = None,
) -> str | list[str] | None:
    """Try fill first, then color — for bar/col geoms."""
    if "fill" in data:
        return data["fill"]
    if "color" in data and isinstance(data["color"], str):
        return data["color"]
    if params is not None:
        return params.get("fill") or params.get("color")  # type: ignore[return-value]
    return None


def resolve_ls(value: Any) -> Any:
    """Resolve a linetype value through the ggplot2 translation layer."""
    from plotten._linetypes import resolve_linetype

    if isinstance(value, list):
        return [resolve_linetype(v) for v in value]
    return resolve_linetype(value)


def extract_per_index[T](values: list[T] | T, indices: list[int]) -> list[T] | T:
    """Subset by indices if list, else broadcast."""
    if isinstance(values, list):
        return [values[i] for i in indices]
    return values
