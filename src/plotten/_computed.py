from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AfterStat:
    """Reference a variable computed by the stat layer."""

    var: str


@dataclass(frozen=True, slots=True)
class AfterScale:
    """Reference a variable after scale mapping."""

    var: str


def after_stat(var: str) -> AfterStat:
    """Reference a variable computed by the stat layer.

    ``computed()`` is a Pythonic alias for this function.
    """
    return AfterStat(var=var)


# Pythonic alias
computed = after_stat
"""Alias for :func:`after_stat` — reference a stat-computed variable."""


def after_scale(var: str) -> AfterScale:
    """Reference a variable after scale mapping.

    ``scaled()`` is a Pythonic alias for this function.
    """
    return AfterScale(var=var)


# Pythonic alias
scaled = after_scale
"""Alias for :func:`after_scale` — reference a scale-mapped variable."""


def stage(
    start: str | None = None,
    after_stat: str | AfterStat | None = None,
    after_scale: str | AfterScale | None = None,
) -> str | AfterStat | AfterScale:
    """Stage aesthetic mapping across the pipeline.

    Returns the latest-stage mapping provided.

    Raises
    ------
    ConfigError
        If no arguments are provided.
    """
    if after_scale is not None:
        if isinstance(after_scale, str):
            return AfterScale(var=after_scale)
        return after_scale
    if after_stat is not None:
        if isinstance(after_stat, str):
            return AfterStat(var=after_stat)
        return after_stat
    if start is not None:
        return start
    from plotten._validation import ConfigError

    msg = "stage() requires at least one argument (start, after_stat, or after_scale)"
    raise ConfigError(msg)
