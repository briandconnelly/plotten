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
    """Create an AfterStat mapping."""
    return AfterStat(var=var)


def after_scale(var: str) -> AfterScale:
    """Create an AfterScale mapping."""
    return AfterScale(var=var)


def stage(
    start: str | None = None,
    after_stat: str | AfterStat | None = None,
    after_scale: str | AfterScale | None = None,
) -> str | AfterStat | AfterScale:
    """Stage aesthetic mapping across the pipeline.

    Returns the latest-stage mapping provided.
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
    msg = "stage() requires at least one argument"
    raise ValueError(msg)
