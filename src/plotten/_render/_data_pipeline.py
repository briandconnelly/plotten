"""Data pipeline: mapping separation, layer resolution, and group splitting."""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING, Any, cast

import narwhals as nw

from plotten._render._scale_resolution import _map_aesthetics, _train_scales
from plotten._render._structures import ResolvedLayer

if TYPE_CHECKING:
    from plotten._aes import Aes
    from plotten._layer import Layer
    from plotten.scales._base import ScaleBase


def _separate_mappings(
    merged_aes: Aes,
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, Any]]:
    """Separate merged aesthetics into normal, after_stat, after_scale, and interaction mappings."""
    from plotten._computed import AfterScale, AfterStat
    from plotten._interaction import Interaction

    normal: dict[str, str] = {}
    after_stat: dict[str, str] = {}
    after_scale: dict[str, str] = {}
    interactions: dict[str, Any] = {}

    for aes_field in (f.name for f in fields(merged_aes)):
        val = getattr(merged_aes, aes_field)
        if val is None:
            continue
        if isinstance(val, AfterStat):
            after_stat[aes_field] = val.var
        elif isinstance(val, AfterScale):
            after_scale[aes_field] = val.var
        elif isinstance(val, Interaction):
            interactions[aes_field] = val
        else:
            normal[aes_field] = val

    return normal, after_stat, after_scale, interactions


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

        wrapped = nw.from_native(raw_data)

        normal_mappings, after_stat_mappings, after_scale_mappings, interaction_mappings = (
            _separate_mappings(merged_aes)
        )

        # For lazy frames with lazy_select enabled, select only the columns
        # referenced by aesthetic mappings before collecting. This enables
        # projection pushdown (e.g. polars/duckdb skip reading unused columns).
        if hasattr(wrapped, "collect"):
            from plotten._validation import get_lazy_select

            if get_lazy_select():
                needed_cols: set[str] = set(normal_mappings.values())
                for inter in interaction_mappings.values():
                    needed_cols.update(inter.columns)
                available = set(wrapped.collect_schema().names())
                select_cols = sorted(needed_cols & available)
                if select_cols and len(select_cols) < len(available):
                    wrapped = wrapped.select(select_cols)
            frame = cast("nw.DataFrame", wrapped.collect())
        else:
            frame = cast("nw.DataFrame", wrapped)

        # Cast Decimal columns to Float64 (e.g. DuckDB infers DECIMAL for literals)
        decimal_cols = [col for col, dtype in frame.schema.items() if "Decimal" in str(dtype)]
        if decimal_cols:
            frame = frame.with_columns(nw.col(c).cast(nw.Float64) for c in decimal_cols)

        # Resolve interaction mappings: create combined columns via narwhals expressions
        for aes_field, inter in interaction_mappings.items():
            cols = inter.columns
            # Build concatenated string expression using narwhals
            expr = nw.col(cols[0]).cast(nw.String)
            for c in cols[1:]:
                expr = expr + nw.lit(".") + nw.col(c).cast(nw.String)
            frame = frame.with_columns(expr.alias(aes_field))

        # Validate that mapped column names exist in the data
        from plotten._validation import validate_mapped_columns

        validate_mapped_columns(normal_mappings, frame.columns, layer.geom.required_aes)

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
        frame = cast("nw.DataFrame", nw.from_native(stat.compute(nw.to_native(frame))))

        # Apply after_stat mappings
        if after_stat_mappings:
            for aes_field, var_name in after_stat_mappings.items():
                if var_name not in frame.columns:
                    from plotten._validation import DataError

                    available = sorted(frame.columns)
                    raise DataError(
                        f"after_stat('{var_name}') references a column that "
                        f"does not exist in the stat output. "
                        f"Available computed columns: {available}"
                    )
                if var_name != aes_field:
                    if aes_field in frame.columns:
                        frame = frame.drop(aes_field)
                    frame = frame.rename({var_name: aes_field})

        # Build data dict
        data_dict: dict[str, Any] = {col: frame.get_column(col).to_list() for col in frame.columns}

        # Map aesthetic names back to original column names for error messages
        column_origins = {
            aes_field: col_name
            for aes_field, col_name in normal_mappings.items()
            if col_name != aes_field
        }
        _train_scales(frame, data_dict, scales, column_origins)
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
