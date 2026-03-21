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

from plotten._enums import FacetScales
from plotten._render._data_pipeline import (
    _detect_group_key,
    _resolve_layers,
    _separate_mappings,
    _split_by_group,
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
                panels.append(ResolvedPanel(label=label, layers=layers, scales={}))

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
    )


def _default_labs(labs_obj: Any, mapping: Any) -> Any:
    """Fill missing axis/aesthetic labels from the aes mapping variable names."""
    from plotten._labs import Labs

    if labs_obj is None:
        labs_obj = Labs()

    defaults: dict[str, str] = {}
    for field_name in (
        "x",
        "y",
        "color",
        "fill",
        "size",
        "alpha",
        "shape",
        "linetype",
        "linewidth",
        "hatch",
    ):
        if getattr(labs_obj, field_name) is None:
            aes_val = getattr(mapping, field_name, None)
            if isinstance(aes_val, str):
                defaults[field_name] = aes_val

    if defaults:
        return labs_obj + Labs(**defaults)
    return labs_obj


# Re-export for backwards compatibility with existing imports
__all__ = [
    "ResolvedLayer",
    "ResolvedPanel",
    "ResolvedPlot",
    "_detect_group_key",
    "_resolve_layers",
    "_separate_mappings",
    "_split_by_group",
    "resolve",
]
