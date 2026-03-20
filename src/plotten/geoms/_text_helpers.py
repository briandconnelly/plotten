"""Shared helpers for text and label geoms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


def extract_text_params(params: GeomParams) -> tuple[str, float, dict[str, Any]]:
    """Extract common text drawing parameters.

    Returns (color, fontsize, font_kwargs) where font_kwargs contains
    ha, va, and optional fontfamily/fontweight/fontstyle.
    """
    color: str = params.get("color", "black")
    fontsize: float = params.get("size", 10)
    ha = params.get("ha", "center")
    va = params.get("va", "center")

    font_kwargs: dict[str, Any] = {"ha": ha, "va": va}
    if params.get("family") is not None:
        font_kwargs["fontfamily"] = params["family"]
    if params.get("weight") is not None:
        font_kwargs["fontweight"] = params["weight"]
    if params.get("style") is not None:
        font_kwargs["fontstyle"] = params["style"]

    return color, fontsize, font_kwargs


def extract_label_data(data: GeomDrawData) -> tuple[list[float], list[float], list[str]]:
    """Extract x, y, label lists from draw data."""
    return list(data["x"]), list(data["y"]), [str(v) for v in data["label"]]


def draw_repel_connectors(
    ax: Axes,
    xs: list[float],
    ys: list[float],
    adjusted: list[tuple[float, float]],
    *,
    segment_color: str,
    segment_size: float,
    segment_alpha: float,
    min_segment_length: float,
) -> None:
    """Draw connector segments from original points to repelled label positions."""
    transform = ax.transData
    for i, (adj_x, adj_y) in enumerate(adjusted):
        orig = transform.transform((xs[i], ys[i]))
        dest = transform.transform((adj_x, adj_y))
        seg_len = float(np.linalg.norm(np.array(orig) - np.array(dest)))
        if seg_len > min_segment_length:
            ax.plot(
                [xs[i], adj_x],
                [ys[i], adj_y],
                color=segment_color,
                linewidth=segment_size,
                alpha=segment_alpha,
                zorder=1,
            )
