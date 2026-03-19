"""Watermark overlay for draft/confidential marking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Watermark:
    """Diagonal text overlay across the entire figure."""

    text: str
    alpha: float = 0.1
    fontsize: float = 50
    rotation: float = 30
    color: str = "#cccccc"


def watermark(
    text: str,
    *,
    alpha: float = 0.1,
    fontsize: float = 50,
    rotation: float = 30,
    color: str = "#cccccc",
) -> Watermark:
    """Create a watermark overlay specification."""
    return Watermark(
        text=text,
        alpha=alpha,
        fontsize=fontsize,
        rotation=rotation,
        color=color,
    )
