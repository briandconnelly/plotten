from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import narwhals as nw

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.scales._base import ScaleBase, auto_scale


@dataclass
class ResolvedLayer:
    """A layer with stat applied and data resolved to plain dicts."""

    geom: Any
    data: dict[str, Any]
    params: dict


@dataclass
class ResolvedPanel:
    """A single panel (facet) of layers and scales."""

    label: str
    layers: list[ResolvedLayer] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)


@dataclass
class ResolvedPlot:
    """Fully resolved plot ready for rendering."""

    panels: list[ResolvedPanel] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)
    coord: Any = None
    theme: Any = None
    labs: Any = None
    facet: Any = None


def _resolve_layers(
    data: Any,
    plot_mapping: Aes,
    layers: tuple[Layer, ...],
    scales: dict[str, ScaleBase],
) -> tuple[list[ResolvedLayer], dict[str, ScaleBase]]:
    """Resolve layers against a data subset. Returns (resolved_layers, scales)."""
    resolved_layers: list[ResolvedLayer] = []

    for layer in layers:
        # 1. Merge global aes with per-layer aes
        merged_aes: Aes = plot_mapping | layer.mapping

        # 2. Get data (layer override or passed-in data)
        raw_data = layer.data if layer.data is not None else data
        if raw_data is None:
            continue

        frame = nw.from_native(raw_data)

        # 3. Rename columns based on aesthetic mapping
        rename_exprs = {}
        for aes_field in merged_aes.__dataclass_fields__:
            col_name = getattr(merged_aes, aes_field)
            if col_name is not None and col_name in frame.columns:
                if col_name != aes_field:
                    rename_exprs[col_name] = aes_field

        if rename_exprs:
            frame = frame.rename(rename_exprs)

        # 4. Run stat
        stat = layer.stat
        if stat is None:
            stat = layer.geom.default_stat()
        native_data = nw.to_native(frame)
        computed = stat.compute(native_data)
        frame = nw.from_native(computed)

        # 5. Build data dict for the geom
        data_dict: dict[str, Any] = {}
        for col in frame.columns:
            series = frame.get_column(col)
            data_dict[col] = series.to_list()

        # 6. Infer and train scales
        for aes_name, values_list in data_dict.items():
            if aes_name not in scales:
                native_series = frame.get_column(aes_name).to_native()
                scales[aes_name] = auto_scale(aes_name, native_series)
            scales[aes_name].train(frame.get_column(aes_name).to_native())

        # 7. Map color/fill through scales
        for aes_name in ("color", "fill"):
            if aes_name in data_dict and aes_name in scales:
                scale = scales[aes_name]
                native_series = frame.get_column(aes_name).to_native()
                data_dict[aes_name] = scale.map_data(native_series)

        resolved_layers.append(
            ResolvedLayer(geom=layer.geom, data=data_dict, params=layer.params)
        )

    return resolved_layers, scales


def resolve(plot: Any) -> ResolvedPlot:
    """Walk a Plot spec and produce a ResolvedPlot."""
    from plotten._plot import Plot

    assert isinstance(plot, Plot)

    # Collect explicit scales keyed by aesthetic
    explicit_scales: dict[str, ScaleBase] = {}
    for s in plot.scales:
        explicit_scales[s.aesthetic] = s

    facet = plot.facet

    if facet is None:
        # Single panel
        scales = dict(explicit_scales)
        layers, scales = _resolve_layers(
            plot.data, plot.mapping, plot.layers, scales
        )
        panel = ResolvedPanel(label="", layers=layers, scales={})
        return ResolvedPlot(
            panels=[panel],
            scales=scales,
            coord=plot.coord,
            theme=plot.theme,
            labs=plot.labs,
            facet=None,
        )

    # Faceted: split data into panels
    panel_data = facet.facet_data(plot.data)
    panels: list[ResolvedPanel] = []
    global_scales: dict[str, ScaleBase] = dict(explicit_scales)
    free_scales = getattr(facet, "scales", "fixed")

    for label, subset in panel_data:
        if free_scales == "fixed":
            # All panels share global scales
            layers, global_scales = _resolve_layers(
                subset, plot.mapping, plot.layers, global_scales
            )
            panels.append(ResolvedPanel(label=label, layers=layers, scales={}))
        else:
            # Each panel gets its own scales (copy explicit ones as starting point)
            panel_scales = {k: _copy_scale(v) for k, v in explicit_scales.items()}
            layers, panel_scales = _resolve_layers(
                subset, plot.mapping, plot.layers, panel_scales
            )
            # For "free_x" / "free_y", merge the non-free axis into global
            if free_scales == "free_x":
                # y is shared
                for k, v in panel_scales.items():
                    if k != "x" and k not in global_scales:
                        global_scales[k] = v
                    elif k != "x":
                        global_scales[k].train(
                            _dummy_series_from_scale(v)
                        ) if hasattr(v, '_domain_min') else None
            elif free_scales == "free_y":
                for k, v in panel_scales.items():
                    if k != "y" and k not in global_scales:
                        global_scales[k] = v
            # For fully free, keep everything per-panel
            panels.append(
                ResolvedPanel(label=label, layers=layers, scales=panel_scales)
            )

    return ResolvedPlot(
        panels=panels,
        scales=global_scales,
        coord=plot.coord,
        theme=plot.theme,
        labs=plot.labs,
        facet=facet,
    )


def _copy_scale(scale: ScaleBase) -> ScaleBase:
    """Create a fresh copy of a scale."""
    import copy
    return copy.deepcopy(scale)


def _dummy_series_from_scale(scale: ScaleBase) -> Any:
    """Not used in practice for simple cases — placeholder for scale merging."""
    return None
