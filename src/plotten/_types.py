from __future__ import annotations

from typing import Any, TypedDict

type DataDict = dict[str, list[Any]]


class GeomDrawData(TypedDict, total=False):
    """Data dictionary passed to Geom.draw() — all keys optional."""

    x: list[Any]
    y: list[Any]
    color: list[str] | str
    fill: list[str] | str
    size: list[float] | float
    alpha: list[float] | float
    linetype: list[str] | str
    shape: list[str] | str
    label: list[str]
    group: list[Any]
    ymin: list[float]
    ymax: list[float]
    xmin: list[float]
    xmax: list[float]
    xend: list[float]
    yend: list[float]
    weight: list[float]
    angle: list[float]
    radius: list[float]
    z: list[float]
    upper: list[float]
    lower: list[float]
    middle: list[float]
    outliers_y: list[list[float]]
    density: list[float]
    y_grid: list[float]


class GeomParams(TypedDict, total=False):
    """Parameters dictionary passed to Geom.draw() — all keys optional."""

    color: str
    fill: str | bool
    size: float
    alpha: float
    width: float
    height: float
    linewidth: float
    linetype: str
    ha: str
    va: str
    bins: int
    method: str
    curvature: float
    direction: str
    family: str
    fontsize: float
    linestyle: str
    padding: float
    style: str
    weight: str
