"""Stat → Vega-Lite transform translation."""

from __future__ import annotations

from typing import Any


def translate_stat(
    stat: Any,
    geom: Any,
    encoding: dict[str, Any],
    mark: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Translate a stat into VL encoding modifications and transforms.

    Returns (updated_encoding, updated_mark, transforms).
    """
    if stat is None:
        return encoding, mark, []

    name = type(stat).__name__
    geom_name = type(geom).__name__

    if name == "StatIdentity":
        return encoding, mark, []

    if name == "StatCount":
        return _stat_count(encoding)

    if name == "StatBin":
        return _stat_bin(encoding, stat, geom_name)

    if name == "StatSmooth":
        return _stat_smooth(encoding, stat, geom)

    if name == "StatDensity":
        return _stat_density(encoding, stat)

    if name == "StatBoxplot":
        # Handled natively by VL mark: "boxplot"
        return encoding, mark, []

    # Fallback: pre-compute via stat is not handled at translation time.
    # The caller is responsible for pre-computing when needed.
    return encoding, mark, []


def _stat_count(
    encoding: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    enc = dict(encoding)
    enc["y"] = {"aggregate": "count", "type": "quantitative"}
    return enc, {}, []


def _stat_bin(
    encoding: dict[str, Any],
    stat: Any,
    geom_name: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    enc = dict(encoding)
    if "x" in enc:
        x_enc = dict(enc["x"])
        x_enc["bin"] = {"maxbins": stat.bins} if stat.bins != 30 else True
        enc["x"] = x_enc
    enc["y"] = {"aggregate": "count", "type": "quantitative"}
    return enc, {}, []


def _stat_smooth(
    encoding: dict[str, Any],
    stat: Any,
    geom: Any,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    transforms: list[dict[str, Any]] = []
    x_field = encoding.get("x", {}).get("field")
    y_field = encoding.get("y", {}).get("field")
    if x_field is None or y_field is None:
        return encoding, {}, []

    if stat.method == "lm":
        transforms.append({"regression": y_field, "on": x_field})
    else:
        transforms.append({"loess": y_field, "on": x_field})

    return encoding, {}, transforms


def _stat_density(
    encoding: dict[str, Any],
    stat: Any,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    x_field = encoding.get("x", {}).get("field")
    if x_field is None:
        return encoding, {}, []

    transforms: list[dict[str, Any]] = [{"density": x_field}]
    enc = dict(encoding)
    enc["x"] = {"field": "value", "type": "quantitative"}
    enc["y"] = {"field": "density", "type": "quantitative"}
    return enc, {}, transforms


def needs_precompute(stat: Any) -> bool:
    """Check if a stat needs pre-computation (no VL equivalent)."""
    if stat is None:
        return False
    name = type(stat).__name__
    _NATIVE = {
        "StatIdentity",
        "StatCount",
        "StatBin",
        "StatSmooth",
        "StatDensity",
        "StatBoxplot",
    }
    return name not in _NATIVE
