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

import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import narwhals as nw

from plotten._enums import FacetScales
from plotten.scales._base import ScaleBase, auto_scale

if TYPE_CHECKING:
    from plotten._aes import Aes
    from plotten._labs import Labs
    from plotten._layer import Layer
    from plotten._protocols import Coord, Geom, Position
    from plotten.themes._theme import Theme


@dataclass(slots=True)
class ResolvedLayer:
    """A layer with stat applied and data resolved to plain dicts."""

    geom: Geom
    data: dict[str, Any]
    params: dict
    position: Position | None = None


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
    coord: Coord | None = None
    theme: Theme | None = None
    labs: Labs | None = None
    facet: Any = None
    guides: dict | None = None


def _merge_domain(target: ScaleBase, source: ScaleBase) -> None:
    """Merge domain min/max from source into target scale."""
    src_min = source._domain_min
    src_max = source._domain_max
    tgt_min = target._domain_min
    tgt_max = target._domain_max

    if src_min is not None and tgt_min is not None:
        target._domain_min = min(tgt_min, src_min)
    elif src_min is not None:
        target._domain_min = src_min

    if src_max is not None and tgt_max is not None:
        target._domain_max = max(tgt_max, src_max)
    elif src_max is not None:
        target._domain_max = src_max


def _separate_mappings(
    merged_aes: Aes,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Separate merged aesthetics into normal, after_stat, and after_scale mappings."""
    from plotten._computed import AfterScale, AfterStat

    normal: dict[str, str] = {}
    after_stat: dict[str, str] = {}
    after_scale: dict[str, str] = {}

    for aes_field in merged_aes.__dataclass_fields__:
        val = getattr(merged_aes, aes_field)
        if val is None:
            continue
        if isinstance(val, AfterStat):
            after_stat[aes_field] = val.var
        elif isinstance(val, AfterScale):
            after_scale[aes_field] = val.var
        else:
            normal[aes_field] = val

    return normal, after_stat, after_scale


_AUX_TO_POSITION = {"ymin": "y", "ymax": "y", "xmin": "x", "xmax": "x"}


def _train_scales(frame: Any, data_dict: dict[str, Any], scales: dict[str, ScaleBase]) -> None:
    """Infer and train scales from computed data. Mutates *scales* in-place."""
    for aes_name in data_dict:
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

    # Widen position scales with auxiliary columns (ymin/ymax → y, xmin/xmax → x)
    for aux_col, pos_aes in _AUX_TO_POSITION.items():
        if aux_col in data_dict and pos_aes in scales:
            try:
                aux_series = frame.get_column(aux_col)
                if not str(aux_series.dtype).startswith(("List", "list", "Object", "object")):
                    scales[pos_aes].train(aux_series.to_native())
            except (TypeError, ValueError, KeyError):
                continue


def _map_aesthetics(
    frame: Any,
    data_dict: dict[str, Any],
    scales: dict[str, ScaleBase],
    after_scale_mappings: dict[str, str],
) -> None:
    """Map non-position aesthetics through scales. Mutates *data_dict* in-place."""
    from plotten.scales._position import ScaleDiscrete

    for aes_name in ("color", "fill", "size", "alpha", "shape", "linetype"):
        if aes_name in data_dict and aes_name in scales:
            scale = scales[aes_name]
            native_series = frame.get_column(aes_name).to_native()
            data_dict[aes_name] = scale.map_data(native_series)

    # Map x/y through discrete scales for position adjustment
    for pos in ("x", "y"):
        if pos in data_dict and pos in scales and isinstance(scales[pos], ScaleDiscrete):
            data_dict[pos] = scales[pos].map_data(frame.get_column(pos).to_native())

    # Apply after_scale mappings
    for aes_field, var_name in after_scale_mappings.items():
        if var_name in data_dict:
            data_dict[aes_field] = data_dict[var_name]


def _resolve_layers(
    data: Any,
    plot_mapping: Aes,
    layers: tuple[Layer, ...],
    scales: dict[str, ScaleBase],
) -> tuple[list[ResolvedLayer], dict[str, ScaleBase]]:
    """Resolve layers against a data subset. Returns (resolved_layers, scales)."""
    resolved_layers: list[ResolvedLayer] = []

    for layer in layers:
        merged_aes: Aes = plot_mapping | layer.mapping
        raw_data = layer.data if layer.data is not None else data

        # Data-less layers (e.g. reference line geoms)
        if raw_data is None:
            if not layer.geom.required_aes:
                resolved_layers.append(
                    ResolvedLayer(geom=layer.geom, data={}, params=layer.params)
                )
            continue

        frame = nw.from_native(raw_data)
        normal_mappings, after_stat_mappings, after_scale_mappings = _separate_mappings(merged_aes)

        # Rename columns based on aesthetic mapping
        rename_exprs = {
            col_name: aes_field
            for aes_field, col_name in normal_mappings.items()
            if col_name in frame.columns and col_name != aes_field
        }
        if rename_exprs:
            frame = frame.rename(rename_exprs)

        # Run stat
        stat = layer.stat
        if stat is None:
            stat = layer.geom.default_stat()

        from plotten._validation import validate_required_aes
        from plotten.stats._identity import StatIdentity

        if isinstance(stat, StatIdentity):
            validate_required_aes(layer.geom, merged_aes, frame.columns)
        else:
            validate_required_aes(stat, merged_aes, frame.columns)
        frame = nw.from_native(stat.compute(nw.to_native(frame)))

        # Apply after_stat mappings
        if after_stat_mappings:
            for aes_field, var_name in after_stat_mappings.items():
                if var_name in frame.columns and var_name != aes_field:
                    if aes_field in frame.columns:
                        frame = frame.drop(aes_field)
                    frame = frame.rename({var_name: aes_field})

        # Build data dict
        data_dict: dict[str, Any] = {col: frame.get_column(col).to_list() for col in frame.columns}

        _train_scales(frame, data_dict, scales)
        _map_aesthetics(frame, data_dict, scales, after_scale_mappings)

        # Position adjustment
        if layer.position is not None:
            data_dict = layer.position.adjust(data_dict, layer.params)

        # Group splitting for line-like geoms
        if getattr(layer.geom, "supports_group_splitting", False):
            group_key = _detect_group_key(data_dict)
            if group_key is not None:
                for sub_data in _split_by_group(data_dict, group_key):
                    resolved_layers.append(
                        ResolvedLayer(
                            geom=layer.geom,
                            data=sub_data,
                            params=layer.params,
                            position=layer.position,
                        )
                    )
                continue

        resolved_layers.append(
            ResolvedLayer(
                geom=layer.geom,
                data=data_dict,
                params=layer.params,
                position=layer.position,
            )
        )

    return resolved_layers, scales


def _detect_group_key(data_dict: dict[str, Any]) -> str | None:
    """Return the first aesthetic key suitable for group splitting."""
    for key in ("group", "color", "fill", "linetype"):
        vals = data_dict.get(key)
        if isinstance(vals, list) and len(set(vals)) > 1:
            return key
    return None


def _split_by_group(data_dict: dict[str, Any], group_key: str) -> list[dict[str, Any]]:
    """Split data_dict into sub-dicts by unique values of group_key."""
    group_vals = data_dict[group_key]
    unique_groups = list(dict.fromkeys(group_vals))  # preserve order
    result: list[dict[str, Any]] = []

    for group_val in unique_groups:
        indices = [i for i, v in enumerate(group_vals) if v == group_val]
        sub: dict[str, Any] = {}
        for k, v in data_dict.items():
            if isinstance(v, list):
                sub[k] = [v[i] for i in indices]
            else:
                sub[k] = v
        result.append(sub)

    return result


def _resolve_free_panels(
    panel_data: list,
    plot: Any,
    explicit_scales: dict[str, ScaleBase],
    free_axes: frozenset[str],
    global_scales: dict[str, ScaleBase],
    panels: list[ResolvedPanel],
) -> None:
    """Resolve panels with free scales, promoting shared scales to global."""
    all_position_free = "x" in free_axes and "y" in free_axes

    for label, subset in panel_data:
        panel_scales = {k: copy.deepcopy(v) for k, v in explicit_scales.items()}
        layers, panel_scales = _resolve_layers(subset, plot.mapping, plot.layers, panel_scales)

        if all_position_free:
            # Only promote color/fill to global (first-wins, no domain merge)
            for k in ("color", "fill"):
                if k in panel_scales and k not in global_scales:
                    global_scales[k] = panel_scales[k]
        else:
            # Promote everything non-free; merge domains for shared position scales
            for k, v in panel_scales.items():
                if k in free_axes:
                    continue
                if k not in global_scales:
                    global_scales[k] = v
                elif k in ("x", "y"):
                    _merge_domain(global_scales[k], v)

        panels.append(ResolvedPanel(label=label, layers=layers, scales=panel_scales))


def resolve(plot: Any) -> ResolvedPlot:
    """Walk a Plot spec and produce a ResolvedPlot."""
    from plotten._plot import Plot

    if not isinstance(plot, Plot):
        raise TypeError(f"Expected Plot, got {type(plot).__name__}")

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

        case FacetScales.FREE | FacetScales.FREE_X | FacetScales.FREE_Y:
            free_axes: frozenset[str] = {
                FacetScales.FREE: frozenset(("x", "y")),
                FacetScales.FREE_X: frozenset(("x",)),
                FacetScales.FREE_Y: frozenset(("y",)),
            }[free_scales]
            _resolve_free_panels(
                panel_data, plot, explicit_scales, free_axes, global_scales, panels
            )

    return ResolvedPlot(
        panels=panels,
        scales=global_scales,
        coord=plot.coord,
        theme=plot.theme,
        labs=plot.labs,
        facet=facet,
        guides=plot.guides,
    )
