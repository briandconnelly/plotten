"""Stat → Vega-Lite transform translation."""

from __future__ import annotations

from typing import Any


def translate_stat(
    stat: Any,
    geom: Any,
    encoding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Translate a stat into VL encoding modifications and transforms.

    Returns (updated_encoding, transforms).
    """
    from plotten.stats._bin import StatBin
    from plotten.stats._boxplot import StatBoxplot
    from plotten.stats._count import StatCount
    from plotten.stats._density import StatDensity
    from plotten.stats._identity import StatIdentity
    from plotten.stats._smooth import StatSmooth

    if stat is None or isinstance(stat, StatIdentity):
        return encoding, []

    if isinstance(stat, StatCount):
        return _stat_count(encoding)

    if isinstance(stat, StatBin):
        return _stat_bin(encoding, stat)

    if isinstance(stat, StatSmooth):
        return _stat_smooth(encoding, stat)

    if isinstance(stat, StatDensity):
        return _stat_density(encoding, stat)

    if isinstance(stat, StatBoxplot):
        # Handled natively by VL mark: "boxplot"
        return encoding, []

    # Fallback: pre-compute via stat is not handled at translation time.
    # The caller is responsible for pre-computing when needed.
    return encoding, []


def _stat_count(
    encoding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    enc = dict(encoding)
    enc["y"] = {"aggregate": "count", "type": "quantitative"}
    return enc, []


def _stat_bin(
    encoding: dict[str, Any],
    stat: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    enc = dict(encoding)
    if "x" in enc:
        x_enc = dict(enc["x"])
        x_enc["bin"] = {"maxbins": stat.bins} if stat.bins != 30 else True
        enc["x"] = x_enc
    enc["y"] = {"aggregate": "count", "type": "quantitative"}
    return enc, []


def _stat_smooth(
    encoding: dict[str, Any],
    stat: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    x_field = encoding.get("x", {}).get("field")
    y_field = encoding.get("y", {}).get("field")
    if x_field is None or y_field is None:
        return encoding, []

    if stat.method == "lm":
        return encoding, [{"regression": y_field, "on": x_field}]
    return encoding, [{"loess": y_field, "on": x_field}]


def _stat_density(
    encoding: dict[str, Any],
    stat: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    x_field = encoding.get("x", {}).get("field")
    if x_field is None:
        return encoding, []

    enc = dict(encoding)
    enc["x"] = {"field": "value", "type": "quantitative"}
    enc["y"] = {"field": "density", "type": "quantitative"}
    return enc, [{"density": x_field}]


def needs_precompute(stat: Any) -> bool:
    """Check if a stat needs pre-computation (no VL equivalent)."""
    from plotten.stats._bin import StatBin
    from plotten.stats._boxplot import StatBoxplot
    from plotten.stats._count import StatCount
    from plotten.stats._density import StatDensity
    from plotten.stats._identity import StatIdentity
    from plotten.stats._smooth import StatSmooth

    if stat is None:
        return False
    return not isinstance(
        stat,
        (StatIdentity, StatCount, StatBin, StatSmooth, StatDensity, StatBoxplot),
    )
