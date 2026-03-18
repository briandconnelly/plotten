from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import narwhals as nw

from plotten._enums import FacetScales
from plotten.scales._base import ScaleBase, auto_scale

if TYPE_CHECKING:
    from plotten._aes import Aes
    from plotten._layer import Layer


@dataclass(slots=True)
class ResolvedLayer:
    """A layer with stat applied and data resolved to plain dicts."""

    geom: Any
    data: dict[str, Any]
    params: dict
    position: Any | None = None


@dataclass(slots=True)
class ResolvedPanel:
    """A single panel (facet) of layers and scales."""

    label: str
    layers: list[ResolvedLayer] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)


@dataclass(slots=True)
class ResolvedPlot:
    """Fully resolved plot ready for rendering."""

    panels: list[ResolvedPanel] = field(default_factory=list)
    scales: dict[str, ScaleBase] = field(default_factory=dict)
    coord: Any = None
    theme: Any = None
    labs: Any = None
    facet: Any = None
    guides: dict | None = None


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

        # Data-less layers (e.g. reference line geoms)
        if raw_data is None:
            if not layer.geom.required_aes:
                resolved_layers.append(
                    ResolvedLayer(geom=layer.geom, data={}, params=layer.params)
                )
            continue

        frame = nw.from_native(raw_data)

        # 3. Rename columns based on aesthetic mapping
        rename_exprs = {}
        for aes_field in merged_aes.__dataclass_fields__:
            col_name = getattr(merged_aes, aes_field)
            if col_name is not None and col_name in frame.columns and col_name != aes_field:
                rename_exprs[col_name] = aes_field

        if rename_exprs:
            frame = frame.rename(rename_exprs)

        # 3b. Validate required aesthetics
        from plotten._validation import validate_required_aes

        validate_required_aes(layer.geom, merged_aes, frame.columns)

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

        # 6. Infer and train scales (skip list-type columns like outliers_y, y_grid)
        for aes_name, _values_list in data_dict.items():
            series = frame.get_column(aes_name)
            if str(series.dtype).startswith(("List", "list", "Object", "object")):
                continue
            try:
                if aes_name not in scales:
                    native_series = series.to_native()
                    scales[aes_name] = auto_scale(aes_name, native_series)
                scales[aes_name].train(series.to_native())
            except (TypeError, ValueError):
                continue

        # 7. Map aesthetics through scales
        for aes_name in ("color", "fill", "size", "alpha", "shape", "linetype"):
            if aes_name in data_dict and aes_name in scales:
                scale = scales[aes_name]
                native_series = frame.get_column(aes_name).to_native()
                data_dict[aes_name] = scale.map_data(native_series)

        # 7b. Map x/y through discrete scales for position adjustment
        if "x" in data_dict and "x" in scales:
            from plotten.scales._position import ScaleDiscrete as _SD

            if isinstance(scales["x"], _SD):
                data_dict["x"] = scales["x"].map_data(frame.get_column("x").to_native())
        if "y" in data_dict and "y" in scales:
            from plotten.scales._position import ScaleDiscrete as _SD2

            if isinstance(scales["y"], _SD2):
                data_dict["y"] = scales["y"].map_data(frame.get_column("y").to_native())

        # 8. Apply position adjustment (after scale mapping)
        if layer.position is not None:
            data_dict = layer.position.adjust(data_dict, layer.params)

        resolved_layers.append(
            ResolvedLayer(
                geom=layer.geom,
                data=data_dict,
                params=layer.params,
                position=layer.position,
            )
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
        layers, scales = _resolve_layers(plot.data, plot.mapping, plot.layers, scales)
        panel = ResolvedPanel(label="", layers=layers, scales={})
        return ResolvedPlot(
            panels=[panel],
            scales=scales,
            coord=plot.coord,
            theme=plot.theme,
            labs=plot.labs,
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

        case FacetScales.FREE:
            # Each panel gets fully independent scales; color/fill also go to global
            # for the legend.
            for label, subset in panel_data:
                panel_scales = {k: copy.deepcopy(v) for k, v in explicit_scales.items()}
                layers, panel_scales = _resolve_layers(
                    subset, plot.mapping, plot.layers, panel_scales
                )
                # Promote color/fill scales to global so the legend can use them
                for k in ("color", "fill"):
                    if k in panel_scales and k not in global_scales:
                        global_scales[k] = panel_scales[k]
                panels.append(ResolvedPanel(label=label, layers=layers, scales=panel_scales))

        case FacetScales.FREE_X:
            # y (and color/fill) are shared; x is per-panel
            for label, subset in panel_data:
                panel_scales = {k: copy.deepcopy(v) for k, v in explicit_scales.items()}
                layers, panel_scales = _resolve_layers(
                    subset, plot.mapping, plot.layers, panel_scales
                )
                # Merge shared axes into global
                for k, v in panel_scales.items():
                    if k == "x":
                        continue  # x is free
                    if k not in global_scales:
                        global_scales[k] = v
                    elif k in ("y",):
                        # Train the global scale with this panel's data
                        global_scales[k]._domain_min = (
                            min(global_scales[k]._domain_min, v._domain_min)
                            if hasattr(v, "_domain_min")
                            and v._domain_min is not None
                            and global_scales[k]._domain_min is not None
                            else global_scales[k]._domain_min or getattr(v, "_domain_min", None)
                        )
                        global_scales[k]._domain_max = (
                            max(global_scales[k]._domain_max, v._domain_max)
                            if hasattr(v, "_domain_max")
                            and v._domain_max is not None
                            and global_scales[k]._domain_max is not None
                            else global_scales[k]._domain_max or getattr(v, "_domain_max", None)
                        )
                panels.append(ResolvedPanel(label=label, layers=layers, scales=panel_scales))

        case FacetScales.FREE_Y:
            # x (and color/fill) are shared; y is per-panel
            for label, subset in panel_data:
                panel_scales = {k: copy.deepcopy(v) for k, v in explicit_scales.items()}
                layers, panel_scales = _resolve_layers(
                    subset, plot.mapping, plot.layers, panel_scales
                )
                # Merge shared axes into global
                for k, v in panel_scales.items():
                    if k == "y":
                        continue  # y is free
                    if k not in global_scales:
                        global_scales[k] = v
                    elif k in ("x",):
                        global_scales[k]._domain_min = (
                            min(global_scales[k]._domain_min, v._domain_min)
                            if hasattr(v, "_domain_min")
                            and v._domain_min is not None
                            and global_scales[k]._domain_min is not None
                            else global_scales[k]._domain_min or getattr(v, "_domain_min", None)
                        )
                        global_scales[k]._domain_max = (
                            max(global_scales[k]._domain_max, v._domain_max)
                            if hasattr(v, "_domain_max")
                            and v._domain_max is not None
                            and global_scales[k]._domain_max is not None
                            else global_scales[k]._domain_max or getattr(v, "_domain_max", None)
                        )
                panels.append(ResolvedPanel(label=label, layers=layers, scales=panel_scales))

    return ResolvedPlot(
        panels=panels,
        scales=global_scales,
        coord=plot.coord,
        theme=plot.theme,
        labs=plot.labs,
        facet=facet,
        guides=plot.guides,
    )
