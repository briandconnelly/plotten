"""Resolution pipeline: transforms a Plot spec into a RenderablePlot.

Steps:
1. Collect explicit scales from the plot spec.
2. Split data into facet panels (or use a single panel).
3. For each panel, resolve layers:
   a. Merge global and per-layer aesthetic mappings.
   b. Separate AfterStat/AfterScale mappings from normal string mappings.
   c. Rename columns to match aesthetic names.
   d. Run the stat transformation.
   e. Apply after_stat column renames.
   f. Infer and train scales from the computed data.
   g. Map non-position aesthetics through their scales.
   h. Apply after_scale mappings.
   i. Apply position adjustments.
   j. Split by group for line-like geoms.
4. Merge panel scales into global scales (respecting facet free-scale settings).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import MAPPED_AESTHETICS
from plotten._enums import FacetScales
from plotten._render._data_pipeline import (
    _resolve_layers,
)
from plotten._render._scale_resolution import (
    _apply_expand_limits,
    _resolve_free_panels,
)
from plotten._render._structures import (
    ResolvedLayer,
    ResolvedPanel,
    ResolvedPlot,
)

if TYPE_CHECKING:
    from plotten.scales._base import ScaleBase


def _split_facet_label(label: str, facet: Any) -> tuple[str | None, str | None]:
    """Split a combined facet label into (row_label, col_label).

    For ``FacetGrid`` with both rows and cols, the label is
    ``"row_val ~ col_val"``; for rows-only, the label is the row value;
    for cols-only, it is the col value.
    """
    from plotten.facets._grid import FacetGrid

    if not isinstance(facet, FacetGrid):
        return None, label  # facet_wrap → col-like strip
    if facet.rows is not None and facet.cols is not None:
        parts = label.split(" ~ ", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return label, label
    if facet.rows is not None:
        return label, None
    if facet.cols is not None:
        return None, label
    return None, None


def resolve(plot: Any) -> ResolvedPlot:
    """Walk a Plot spec and produce a ResolvedPlot."""
    from plotten._plot import Plot

    if not isinstance(plot, Plot):
        from plotten._validation import ConfigError

        raise ConfigError(f"Expected Plot, got {type(plot).__name__}")

    # Collect explicit scales keyed by aesthetic
    explicit_scales: dict[str, ScaleBase] = {}
    for s in plot.scales:
        explicit_scales[s.aesthetic] = s

    facet = plot.facet

    labs = _default_labs(plot.labs, plot.mapping)
    legend_keys = _infer_legend_keys(plot)

    if facet is None:
        # Single panel
        scales = dict(explicit_scales)
        layers, scales = _resolve_layers(plot.data, plot.mapping, plot.layers, scales)
        _apply_expand_limits(scales, getattr(plot, "_expand_limits", ()))
        panel = ResolvedPanel(label="", layers=layers, scales={})
        return ResolvedPlot(
            panels=[panel],
            scales=scales,
            coord=plot.coord,
            theme=plot.theme,
            labs=labs,
            facet=None,
            guides=plot.guides,
            legend_keys=legend_keys,
        )

    # Faceted: split data into panels
    panel_data = facet.facet_data(plot.data)
    panels: list[ResolvedPanel] = []
    global_scales: dict[str, ScaleBase] = dict(explicit_scales)
    free_scales = getattr(facet, "scales", "fixed")

    match free_scales:
        case FacetScales.FIXED:
            # All panels share global scales
            for label, subset in panel_data:
                layers, global_scales = _resolve_layers(
                    subset, plot.mapping, plot.layers, global_scales
                )
                row_label, col_label = _split_facet_label(label, facet)
                panels.append(
                    ResolvedPanel(
                        label=label,
                        layers=layers,
                        scales={},
                        row_label=row_label,
                        col_label=col_label,
                    )
                )

        case FacetScales.FREE | FacetScales.FREE_X | FacetScales.FREE_Y:
            free_axes: frozenset[str] = {
                FacetScales.FREE: frozenset(("x", "y")),
                FacetScales.FREE_X: frozenset(("x",)),
                FacetScales.FREE_Y: frozenset(("y",)),
            }[free_scales]
            _resolve_free_panels(
                panel_data, plot, explicit_scales, free_axes, global_scales, panels
            )

    _apply_expand_limits(global_scales, getattr(plot, "_expand_limits", ()))

    return ResolvedPlot(
        panels=panels,
        scales=global_scales,
        coord=plot.coord,
        theme=plot.theme,
        labs=labs,
        facet=facet,
        guides=plot.guides,
        legend_keys=legend_keys,
    )


def _infer_legend_keys(plot: Any) -> dict[str, str]:
    """Map each aesthetic to the legend_key of the first geom that uses it."""
    keys: dict[str, str] = {}
    for layer in plot.layers:
        merged = plot.mapping | layer.mapping
        for aes_name in MAPPED_AESTHETICS:
            if aes_name not in keys and getattr(merged, aes_name, None) is not None:
                keys[aes_name] = getattr(layer.geom, "legend_key", "rect")
    return keys


def _default_labs(labs_obj: Any, mapping: Any) -> Any:
    """Fill missing axis/aesthetic labels from the aes mapping variable names."""
    from plotten._labs import Labs

    if labs_obj is None:
        labs_obj = Labs()

    defaults: dict[str, str] = {}
    for field_name in ("x", "y", *MAPPED_AESTHETICS):
        if getattr(labs_obj, field_name) is None:
            aes_val = getattr(mapping, field_name, None)
            if isinstance(aes_val, str):
                defaults[field_name] = aes_val

    if defaults:
        return labs_obj + Labs(**defaults)
    return labs_obj


__all__ = [
    "ResolvedLayer",
    "ResolvedPanel",
    "ResolvedPlot",
    "resolve",
]
