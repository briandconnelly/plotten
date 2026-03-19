"""Vega-Lite export for plotten plots."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from plotten._vegalite._coord import translate_coord
from plotten._vegalite._data import serialize_data
from plotten._vegalite._encoding import translate_aes
from plotten._vegalite._facet import translate_facet
from plotten._vegalite._marks import translate_mark
from plotten._vegalite._positions import translate_position
from plotten._vegalite._scales import translate_scales
from plotten._vegalite._stats import translate_stat
from plotten._vegalite._theme import translate_theme

if TYPE_CHECKING:
    from plotten._plot import Plot

__all__ = ["to_html", "to_vegalite"]


def to_vegalite(plot: Plot) -> dict[str, Any]:
    """Convert a plotten Plot to a Vega-Lite v5 specification dict."""
    spec: dict[str, Any] = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json"}

    # Data
    if plot.data is not None:
        spec["data"] = {"values": serialize_data(plot.data)}

    # Labs → title
    _apply_labs(spec, plot.labs)

    # Check if any layer maps both color and fill
    has_both = _any_layer_has_color_and_fill(plot)

    # Global encoding from plot.mapping
    global_encoding = translate_aes(
        plot.mapping,
        plot.scales,
        has_both_color_fill=has_both,
    )

    if len(plot.layers) == 0:
        spec["encoding"] = global_encoding
    elif len(plot.layers) == 1:
        layer = plot.layers[0]
        mark, encoding, transforms = _build_layer(layer, global_encoding, plot, has_both)
        spec["mark"] = mark
        spec["encoding"] = encoding
        if transforms:
            spec["transform"] = transforms
    else:
        # Multi-layer
        vl_layers: list[dict[str, Any]] = []
        for layer in plot.layers:
            mark, encoding, transforms = _build_layer(layer, global_encoding, plot, has_both)
            layer_spec: dict[str, Any] = {"mark": mark, "encoding": encoding}
            if transforms:
                layer_spec["transform"] = transforms
            if layer.data is not None:
                layer_spec["data"] = {"values": serialize_data(layer.data)}
            vl_layers.append(layer_spec)
        spec["encoding"] = global_encoding
        spec["layer"] = vl_layers

    # Apply axis labels from labs
    _apply_axis_labels(spec, plot.labs)
    # Clean up internal labs
    spec.pop("_labs", None)

    # Facet
    facet_spec, resolve_spec = translate_facet(plot.facet)
    if facet_spec:
        # Wrap mark/encoding into "spec" for faceted charts
        inner: dict[str, Any] = {}
        if "mark" in spec:
            inner["mark"] = spec.pop("mark")
        if "encoding" in spec:
            inner["encoding"] = spec.pop("encoding")
        if "layer" in spec:
            inner["layer"] = spec.pop("layer")
            if "encoding" in spec:
                inner["encoding"] = spec.pop("encoding")
        spec.update(facet_spec)
        spec["spec"] = inner
    if resolve_spec:
        spec.update(resolve_spec)

    # Theme → config
    config = translate_theme(plot.theme)
    if config:
        spec["config"] = config

    return spec


def to_html(plot: Plot) -> str:
    """Convert a plotten Plot to a standalone HTML page with vega-embed."""
    spec = to_vegalite(plot)
    spec_json = json.dumps(spec, indent=2)
    return _HTML_TEMPLATE.format(spec=spec_json)


def _build_layer(
    layer: Any,
    global_encoding: dict[str, Any],
    plot: Any,
    has_both: bool,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Build mark and encoding for a single layer."""
    geom = layer.geom
    stat = layer.stat if layer.stat is not None else geom.default_stat()
    geom_name = type(geom).__name__
    is_text = geom_name in ("GeomText", "GeomLabel")

    # Re-translate global mapping with layer-specific flags (e.g. is_text_mark)
    effective_global = (
        translate_aes(
            plot.mapping,
            plot.scales,
            is_text_mark=is_text,
            has_both_color_fill=has_both,
        )
        if is_text
        else global_encoding
    )
    layer_encoding = translate_aes(
        layer.mapping,
        plot.scales,
        is_text_mark=is_text,
        has_both_color_fill=has_both,
    )
    merged = {**effective_global, **layer_encoding}

    # Handle HLine/VLine special encoding
    if geom_name == "GeomHLine":
        merged["y"] = {"datum": geom._yintercept}
    elif geom_name == "GeomVLine":
        merged["x"] = {"datum": geom._xintercept}

    # Mark
    mark = translate_mark(geom, layer.params)

    # Stat
    merged, mark_updates, transforms = translate_stat(stat, geom, merged, mark)
    if mark_updates:
        mark.update(mark_updates)

    # Position
    effective_mapping = (
        layer.mapping
        if any(getattr(layer.mapping, f) for f in ("color", "fill", "group"))
        else plot.mapping
    )
    merged = translate_position(layer.position, merged, effective_mapping)

    # Scales
    merged = translate_scales(plot.scales, merged)

    # Coord
    merged = translate_coord(plot.coord, merged)

    return mark, merged, transforms


def _apply_labs(spec: dict[str, Any], labs: Any) -> None:
    """Apply labs to the VL spec."""
    if labs.title is not None:
        if labs.subtitle is not None:
            spec["title"] = {"text": labs.title, "subtitle": labs.subtitle}
        else:
            spec["title"] = labs.title

    # Axis labels are applied to encoding later — store on spec for reference
    spec["_labs"] = {}
    for attr in ("x", "y", "color", "fill", "size"):
        val = getattr(labs, attr, None)
        if val is not None:
            spec["_labs"][attr] = val


def _apply_axis_labels(spec: dict[str, Any], labs: Any) -> None:
    """Apply axis title labels from labs to encoding channels."""
    _LABS_TO_CHANNEL = {"x": "x", "y": "y", "color": "color", "fill": "color", "size": "size"}
    # Find the encoding dict to modify
    enc = spec.get("encoding")
    if enc is None:
        return
    for lab_attr, channel in _LABS_TO_CHANNEL.items():
        val = getattr(labs, lab_attr, None)
        if val is not None and channel in enc:
            ch = dict(enc[channel])
            ch["title"] = val
            enc[channel] = ch


def _any_layer_has_color_and_fill(plot: Any) -> bool:
    """Check if any layer or global mapping has both color and fill."""
    for mapping in [plot.mapping, *(layer.mapping for layer in plot.layers)]:
        if mapping.color is not None and mapping.fill is not None:
            return True
    return False


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
</head>
<body>
  <div id="vis"></div>
  <script>vegaEmbed('#vis', {spec});</script>
</body>
</html>"""
