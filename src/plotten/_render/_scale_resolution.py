"""Scale training, mapping, and domain utilities."""

from __future__ import annotations

import copy
import warnings
from typing import TYPE_CHECKING, Any, Literal

import narwhals as nw

from plotten._validation import PlottenWarning
from plotten.scales._base import ScaleBase, auto_scale

if TYPE_CHECKING:
    from plotten._render._structures import ResolvedPanel

_AUX_TO_POSITION = {"ymin": "y", "ymax": "y", "xmin": "x", "xmax": "x"}


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
        try:
            if aes_name not in scales:
                native_series = series.to_native()
                scales[aes_name] = auto_scale(aes_name, native_series)
            col_name = column_origins.get(aes_name) if column_origins else None
            validate_data_type(
                aes_name, series.to_native(), scales[aes_name], column_name=col_name
            )
            scales[aes_name].train(series.to_native())
        except (TypeError, ValueError) as e:
            warnings.warn(
                f"Scale training skipped for '{aes_name}': {e}",
                PlottenWarning,
                stacklevel=2,
            )
            continue

    # Widen position scales with auxiliary columns (ymin/ymax → y, xmin/xmax → x)
    for aux_col, pos_aes in _AUX_TO_POSITION.items():
        if aux_col in data_dict and pos_aes in scales:
            try:
                aux_series = frame.get_column(aux_col)
                if not isinstance(aux_series.dtype, (nw.List, nw.Array, nw.Object)):
                    scales[pos_aes].train(aux_series.to_native())
            except (TypeError, ValueError, KeyError) as e:
                warnings.warn(
                    f"Scale training skipped for auxiliary '{aux_col}' → '{pos_aes}': {e}",
                    PlottenWarning,
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


def _get_backend() -> Literal["polars", "pandas"]:
    """Return the first available dataframe backend name."""
    try:
        import polars as _  # noqa: F401

        return "polars"
    except ImportError:
        return "pandas"


def _apply_expand_limits(scales: dict[str, ScaleBase], expand_limits: tuple) -> None:
    """Train position scales with sentinel values from expand_limits()."""
    backend = _get_backend()
    for el in expand_limits:
        if el.x and "x" in scales:
            series = nw.new_series("x", list(el.x), dtype=nw.Float64, backend=backend)
            scales["x"].train(nw.to_native(series))
        if el.y and "y" in scales:
            series = nw.new_series("y", list(el.y), dtype=nw.Float64, backend=backend)
            scales["y"].train(nw.to_native(series))
