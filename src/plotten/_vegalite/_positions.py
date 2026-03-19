"""Position → Vega-Lite stack/offset translation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._vegalite._unsupported import warn_unsupported

if TYPE_CHECKING:
    from plotten._aes import Aes


def translate_position(
    position: Any,
    encoding: dict[str, Any],
    mapping: Aes,
) -> dict[str, Any]:
    """Apply position adjustments to VL encoding. Returns updated encoding."""
    from plotten.positions._dodge import PositionDodge
    from plotten.positions._dodge2 import PositionDodge2
    from plotten.positions._fill import PositionFill
    from plotten.positions._identity import PositionIdentity
    from plotten.positions._jitter import PositionJitter
    from plotten.positions._jitterdodge import PositionJitterDodge
    from plotten.positions._nudge import PositionNudge
    from plotten.positions._stack import PositionStack

    if position is None or isinstance(position, PositionIdentity):
        return encoding

    enc = dict(encoding)

    if isinstance(position, PositionStack):
        if "y" in enc:
            y = dict(enc["y"])
            y["stack"] = True
            enc["y"] = y
        return enc

    if isinstance(position, PositionFill):
        if "y" in enc:
            y = dict(enc["y"])
            y["stack"] = "normalize"
            enc["y"] = y
        return enc

    if isinstance(position, (PositionDodge, PositionDodge2)):
        group_field = _find_group_field(mapping)
        if group_field:
            enc["xOffset"] = {"field": group_field}
        return enc

    if isinstance(position, (PositionJitter, PositionJitterDodge)):
        warn_unsupported(
            type(position).__name__,
            "Position will be ignored in Vega-Lite output.",
        )
        return enc

    if isinstance(position, PositionNudge):
        warn_unsupported(
            "PositionNudge",
            "Position will be ignored in Vega-Lite output.",
        )
        return enc

    return enc


def _find_group_field(mapping: Aes) -> str | None:
    """Find the field used for grouping (color, fill, or group)."""
    for attr in ("color", "fill", "group"):
        val = getattr(mapping, attr, None)
        if val is not None and isinstance(val, str):
            return val
    return None
