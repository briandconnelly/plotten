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

    *param_key* allows looking up a different key in params (e.g. ``linetype`` ->
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
    """Try fill first, then color -- for bar/col geoms."""
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


def build_line_kwargs(
    data: GeomDrawData,
    params: GeomParams,
) -> dict[str, Any]:
    """Build common kwargs for line-based geoms (color, alpha, linestyle, linewidth).

    Handles data-vs-params fallback and scalar coercion for grouped data.
    """
    kwargs: dict[str, Any] = {}
    _add_scalar(kwargs, data, params, "color", "color")
    _add_scalar(kwargs, data, params, "alpha", "alpha")
    if "linetype" in data:
        kwargs["linestyle"] = resolve_ls(scalar(data["linetype"]))
    elif "linetype" in params:
        kwargs["linestyle"] = resolve_ls(params["linetype"])
    # linewidth: prefer explicit linewidth, fall back to size
    if "linewidth" in data:
        _add_scalar(kwargs, data, params, "linewidth", "linewidth")
    elif "size" in data:
        _add_scalar(kwargs, data, params, "size", "linewidth")
    elif "linewidth" in params:
        kwargs["linewidth"] = params["linewidth"]
    elif "size" in params:
        kwargs["linewidth"] = params["size"]
    return kwargs


def build_fill_kwargs(
    data: GeomDrawData,
    params: GeomParams,
    *,
    default_alpha: float | None = None,
) -> dict[str, Any]:
    """Build common kwargs for filled geoms (color from fill/color, alpha, linewidth, hatch).

    For fill_between/bar-style geoms. Uses ``fill`` aesthetic as ``color`` kwarg.
    """
    kwargs: dict[str, Any] = {}
    fill_color = extract_fill_or_color(data, params)
    if fill_color is not None:
        kwargs["color"] = scalar(fill_color) if isinstance(fill_color, list) else fill_color
    if default_alpha is not None:
        kwargs["alpha"] = params.get("alpha", default_alpha)
    elif "alpha" in params:
        kwargs["alpha"] = params["alpha"]
    if "linewidth" in data:
        kwargs["linewidth"] = (
            scalar(data["linewidth"]) if isinstance(data["linewidth"], list) else data["linewidth"]
        )
    elif "linewidth" in params:
        kwargs["linewidth"] = params["linewidth"]
    hatch = data.get("hatch", params.get("hatch"))
    if hatch is not None:
        kwargs["hatch"] = scalar(hatch) if isinstance(hatch, list) else hatch
    return kwargs


def draw_bars(
    data: GeomDrawData,
    ax: Any,
    params: GeomParams,
    *,
    orientation: str = "x",
) -> None:
    """Shared bar-drawing logic for GeomBar and GeomCol."""
    kwargs = build_fill_kwargs(data, params)
    width = params.get("width", 0.8)
    if orientation == "y":
        ax.barh(data["x"], data["y"], height=width, **kwargs)
    else:
        ax.bar(data["x"], data["y"], width=width, **kwargs)


def _add_scalar(
    kwargs: dict[str, Any],
    data: GeomDrawData,
    params: GeomParams,
    data_key: str,
    kwarg_key: str,
) -> None:
    """Add a scalar aesthetic to kwargs with data/params fallback."""
    if data_key in data:
        val = data[data_key]  # type: ignore[literal-required]
        kwargs[kwarg_key] = scalar(val) if isinstance(val, list) else val
    elif data_key in params:
        kwargs[kwarg_key] = params[data_key]  # type: ignore[literal-required]
