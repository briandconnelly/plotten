"""Coord → Vega-Lite encoding swaps / domain clips / errors."""

from __future__ import annotations

from typing import Any

from plotten._validation import PlottenError
from plotten._vegalite._unsupported import warn_unsupported


def translate_coord(
    coord: Any,
    encoding: dict[str, Any],
) -> dict[str, Any]:
    """Apply coord transformations to VL encoding. Returns updated encoding."""
    if coord is None:
        return encoding

    name = type(coord).__name__
    enc = dict(encoding)

    if name == "CoordCartesian":
        _apply_domain_clip(enc, coord)
        return enc

    if name == "CoordFlip":
        _swap_xy(enc)
        _apply_domain_clip(enc, coord)
        return enc

    if name == "CoordPolar":
        msg = (
            "CoordPolar is not supported by Vega-Lite export. "
            "Use render() or ggsave() for the matplotlib backend instead."
        )
        raise PlottenError(msg)

    if name in ("CoordEqual", "CoordFixed"):
        warn_unsupported(name, "Aspect ratio constraints are ignored.")
        _apply_domain_clip(enc, coord)
        return enc

    if name == "CoordTrans":
        _check_coord_trans(coord)
        return enc

    return enc


def _apply_domain_clip(enc: dict[str, Any], coord: Any) -> None:
    """Set scale domain from coord xlim/ylim."""
    if hasattr(coord, "xlim") and coord.xlim is not None and "x" in enc:
        x = dict(enc["x"])
        x.setdefault("scale", {})["domain"] = list(coord.xlim)
        enc["x"] = x

    if hasattr(coord, "ylim") and coord.ylim is not None and "y" in enc:
        y = dict(enc["y"])
        y.setdefault("scale", {})["domain"] = list(coord.ylim)
        enc["y"] = y


def _swap_xy(enc: dict[str, Any]) -> None:
    """Swap x and y encoding channels."""
    x = enc.pop("x", None)
    y = enc.pop("y", None)
    if x is not None:
        enc["y"] = x
    if y is not None:
        enc["x"] = y


def _check_coord_trans(coord: Any) -> None:
    """Raise error for non-identity coordinate transforms."""
    for attr in ("x", "y"):
        val = getattr(coord, attr, "identity")
        if val != "identity" and not (
            callable(val) and getattr(val, "__name__", "") == "identity"
        ):
            msg = (
                "CoordTrans with non-identity transforms is not supported "
                "by Vega-Lite export. Use render() or ggsave() for the "
                "matplotlib backend instead."
            )
            raise PlottenError(msg)
