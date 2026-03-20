"""Scale training, mapping, and domain utilities."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

import narwhals as nw

from plotten._defaults import MAPPED_AESTHETICS, detect_backend
from plotten._validation import plotten_warn
from plotten.scales._base import ScaleBase, auto_scale

if TYPE_CHECKING:
    from plotten._render._structures import ResolvedPanel

_AUX_TO_POSITION = {"ymin": "y", "ymax": "y", "xmin": "x", "xmax": "x"}


def _opt_min(a: float | None, b: float | None) -> float | None:
    if a is None:
        return b
    return min(a, b) if b is not None else a


def _opt_max(a: float | None, b: float | None) -> float | None:
    if a is None:
        return b
    return max(a, b) if b is not None else a


def _merge_domain(target: ScaleBase, source: ScaleBase) -> None:
    """Merge domain min/max from source into target scale."""
    target._domain_min = _opt_min(target._domain_min, source._domain_min)
    target._domain_max = _opt_max(target._domain_max, source._domain_max)


def _train_scales(
    frame: Any,
    data_dict: dict[str, Any],
    scales: dict[str, ScaleBase],
    column_origins: dict[str, str] | None = None,
) -> None:
    """Infer and train scales from computed data. Mutates *scales* in-place."""
    from plotten._validation import validate_data_type

    for aes_name in data_dict:
        series = frame.get_column(aes_name)
        dtype = series.dtype
        if isinstance(dtype, (nw.List, nw.Array, nw.Object)):
            continue
        if aes_name not in scales:
            native_series = series.to_native()
            scales[aes_name] = auto_scale(aes_name, native_series)
        try:
            col_name = column_origins.get(aes_name) if column_origins else None
            validate_data_type(
                aes_name, series.to_native(), scales[aes_name], column_name=col_name
            )
            scales[aes_name].train(series.to_native())
        except (TypeError, ValueError) as e:
            plotten_warn(
                f"Scale training skipped for '{aes_name}': {e}",
                stacklevel=2,
            )
            continue

    # Widen position scales with auxiliary columns (ymin/ymax → y, xmin/xmax → x)
    for aux_col, pos_aes in _AUX_TO_POSITION.items():
        if aux_col in data_dict:
            try:
                aux_series = frame.get_column(aux_col)
                if isinstance(aux_series.dtype, (nw.List, nw.Array, nw.Object)):
                    continue
                native = aux_series.to_native()
                if pos_aes not in scales:
                    scales[pos_aes] = auto_scale(pos_aes, native)
                scales[pos_aes].train(native)
            except (TypeError, ValueError, KeyError) as e:
                plotten_warn(
                    f"Scale training skipped for auxiliary '{aux_col}' → '{pos_aes}': {e}",
                    stacklevel=2,
                )
                continue


def _map_aesthetics(
    frame: Any,
    data_dict: dict[str, Any],
    scales: dict[str, ScaleBase],
    after_scale_mappings: dict[str, str],
) -> None:
    """Map non-position aesthetics through scales. Mutates *data_dict* in-place."""
    from plotten.scales._binned_position import ScaleBinnedPosition
    from plotten.scales._position import ScaleDiscrete

    for aes_name in MAPPED_AESTHETICS:
        if aes_name in data_dict and aes_name in scales:
            scale = scales[aes_name]
            native_series = frame.get_column(aes_name).to_native()
            data_dict[aes_name] = scale.map_data(native_series)

    # Map x/y through discrete or binned position scales
    for pos in ("x", "y"):
        if (
            pos in data_dict
            and pos in scales
            and isinstance(scales[pos], (ScaleDiscrete, ScaleBinnedPosition))
        ):
            data_dict[pos] = scales[pos].map_data(frame.get_column(pos).to_native())

    # Apply after_scale mappings
    for aes_field, var_name in after_scale_mappings.items():
        if var_name in data_dict:
            data_dict[aes_field] = data_dict[var_name]


def _resolve_free_panels(
    panel_data: list,
    plot: Any,
    explicit_scales: dict[str, ScaleBase],
    free_axes: frozenset[str],
    global_scales: dict[str, ScaleBase],
    panels: list[ResolvedPanel],
) -> None:
    """Resolve panels with free scales, promoting shared scales to global."""
    from plotten._render._data_pipeline import _resolve_layers

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

        from plotten._render._structures import ResolvedPanel

        panels.append(ResolvedPanel(label=label, layers=layers, scales=panel_scales))


def _apply_expand_limits(scales: dict[str, ScaleBase], expand_limits: tuple) -> None:
    """Train position scales with sentinel values from expand_limits()."""
    backend = detect_backend()
    for el in expand_limits:
        if el.x and "x" in scales:
            series = nw.new_series("x", list(el.x), dtype=nw.Float64, backend=backend)
            scales["x"].train(nw.to_native(series))
        if el.y and "y" in scales:
            series = nw.new_series("y", list(el.y), dtype=nw.Float64, backend=backend)
            scales["y"].train(nw.to_native(series))
