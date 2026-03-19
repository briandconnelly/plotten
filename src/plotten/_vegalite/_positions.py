"""Position → Vega-Lite stack/offset translation."""

from __future__ import annotations

from typing import Any

from plotten._vegalite._unsupported import warn_unsupported


def translate_position(
    position: Any,
    encoding: dict[str, Any],
    mapping: Any,
) -> dict[str, Any]:
    """Apply position adjustments to VL encoding. Returns updated encoding."""
    if position is None:
        return encoding

    name = type(position).__name__
    enc = dict(encoding)

    if name == "PositionIdentity":
        return enc

    if name == "PositionStack":
        if "y" in enc:
            y = dict(enc["y"])
            y["stack"] = True
            enc["y"] = y
        return enc

    if name == "PositionFill":
        if "y" in enc:
            y = dict(enc["y"])
            y["stack"] = "normalize"
            enc["y"] = y
        return enc

    if name == "PositionDodge" or name == "PositionDodge2":
        # Use xOffset for dodge grouping
        group_field = _find_group_field(mapping)
        if group_field:
            enc["xOffset"] = {"field": group_field}
        return enc

    if name in ("PositionJitter", "PositionJitterDodge", "PositionBeeswarm"):
        warn_unsupported(name, "Position will be ignored in Vega-Lite output.")
        return enc

    if name == "PositionNudge":
        warn_unsupported(name, "Position will be ignored in Vega-Lite output.")
        return enc

    return enc


def _find_group_field(mapping: Any) -> str | None:
    """Find the field used for grouping (color, fill, or group)."""
    for attr in ("color", "fill", "group"):
        val = getattr(mapping, attr, None)
        if val is not None and isinstance(val, str):
            return val
    return None
