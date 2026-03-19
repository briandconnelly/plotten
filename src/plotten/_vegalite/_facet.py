"""Facet → Vega-Lite facet spec translation."""

from __future__ import annotations

from typing import Any


def translate_facet(facet: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Convert a plotten facet to VL facet and resolve dicts.

    Returns (facet_spec, resolve_spec).
    """
    if facet is None:
        return {}, {}

    from plotten.facets._grid import FacetGrid
    from plotten.facets._wrap import FacetWrap

    if isinstance(facet, FacetWrap):
        return _facet_wrap(facet)
    if isinstance(facet, FacetGrid):
        return _facet_grid(facet)
    return {}, {}


def _facet_wrap(facet: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    facet_spec: dict[str, Any] = {
        "field": facet.facets,
        "type": "nominal",
    }
    top: dict[str, Any] = {"facet": facet_spec}
    if facet.ncol is not None:
        top["columns"] = facet.ncol
    resolve = _resolve_for_scales(facet.scales)
    return top, resolve


def _facet_grid(facet: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    facet_spec: dict[str, Any] = {}
    if facet.rows is not None:
        facet_spec["row"] = {"field": facet.rows, "type": "nominal"}
    if facet.cols is not None:
        facet_spec["column"] = {"field": facet.cols, "type": "nominal"}
    resolve = _resolve_for_scales(facet.scales)
    return {"facet": facet_spec}, resolve


def _resolve_for_scales(scales: str) -> dict[str, Any]:
    if scales == "fixed":
        return {}
    resolve_scale: dict[str, str] = {}
    if scales in ("free", "free_x"):
        resolve_scale["x"] = "independent"
    if scales in ("free", "free_y"):
        resolve_scale["y"] = "independent"
    if resolve_scale:
        return {"resolve": {"scale": resolve_scale}}
    return {}
