"""Declarative dict-based plot specification: from_spec."""

from __future__ import annotations

from typing import Any

from plotten._validation import SpecError


def spec_schema() -> dict[str, Any]:
    """Return a JSON Schema describing the valid structure for :func:`from_spec`.

    The schema is self-contained and includes ``enum`` values for every
    registry (geoms, scales, coords, positions, themes, facets, recipes)
    so that agents can validate specs before submitting them.

    Returns
    -------
    dict
        A JSON Schema (draft 2020-12) dictionary.

    Examples
    --------
    Feed the schema into an agent's system prompt::

        import json
        from plotten import spec_schema
        system_prompt = f"Use this schema: {json.dumps(spec_schema())}"

    Validate a spec before building a plot::

        import jsonschema  # optional dependency
        from plotten import spec_schema, from_spec
        jsonschema.validate(my_spec, spec_schema())
        plot = from_spec(my_spec, data=df)
    """
    _build_registries()

    mapping_schema: dict[str, Any] = {
        "type": "object",
        "description": (
            "Aesthetic mappings from column names to visual properties. "
            "Keys are aesthetic names (x, y, color, fill, size, shape, alpha, "
            "linetype, linewidth, group, label, weight, hatch). "
            "Values are column name strings, or dicts for computed mappings: "
            '{"after_stat": "density"} or {"after_scale": "fill"}.'
        ),
        "additionalProperties": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "after_stat": {"type": "string"},
                        "after_scale": {"type": "string"},
                    },
                    "oneOf": [
                        {"required": ["after_stat"]},
                        {"required": ["after_scale"]},
                    ],
                },
            ]
        },
    }

    position_schema: dict[str, Any] = {
        "oneOf": [
            {"type": "string", "enum": sorted(_POSITION_REGISTRY)},
            {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": sorted(_POSITION_REGISTRY)},
                },
                "required": ["type"],
                "additionalProperties": True,
                "description": (
                    'Position adjustment with parameters. E.g. {"type": "jitter", "width": 0.2}.'
                ),
            },
        ]
    }

    layer_schema: dict[str, Any] = {
        "type": "object",
        "required": ["geom"],
        "properties": {
            "geom": {
                "type": "string",
                "enum": sorted(_GEOM_REGISTRY),
                "description": "The geometry type for this layer.",
            },
            "mapping": mapping_schema,
            "position": position_schema,
        },
        "additionalProperties": True,
        "description": (
            "A plot layer. The 'geom' key is required. "
            "Optional 'mapping' overrides aesthetics for this layer. "
            "All other keys are passed as keyword arguments to the geom "
            "factory (e.g. color, size, alpha, bins, method, se, "
            "yintercept, xintercept)."
        ),
    }

    scale_schema: dict[str, Any] = {
        "type": "object",
        "required": ["fn"],
        "properties": {
            "fn": {
                "type": "string",
                "enum": sorted(_SCALE_REGISTRY),
                "description": "The scale function name.",
            },
        },
        "additionalProperties": True,
        "description": (
            "A scale specification. 'fn' is the scale function name. "
            "All other keys are passed as keyword arguments "
            "(e.g. values, limits, breaks, labels, name, palette)."
        ),
    }

    coord_schema: dict[str, Any] = {
        "type": "object",
        "required": ["fn"],
        "properties": {
            "fn": {
                "type": "string",
                "enum": sorted(_COORD_REGISTRY),
                "description": "The coordinate system function name.",
            },
        },
        "additionalProperties": True,
    }

    facet_schema: dict[str, Any] = {
        "type": "object",
        "required": ["fn"],
        "properties": {
            "fn": {
                "type": "string",
                "enum": sorted(_FACET_REGISTRY),
                "description": "The faceting function name.",
            },
            "facets": {
                "type": "string",
                "description": "Column name to facet by (for facet_wrap).",
            },
            "ncol": {"type": "integer", "description": "Number of columns."},
            "nrow": {"type": "integer", "description": "Number of rows."},
            "rows": {
                "type": "string",
                "description": "Row variable (for facet_grid).",
            },
            "cols": {
                "type": "string",
                "description": "Column variable (for facet_grid).",
            },
        },
        "additionalProperties": True,
    }

    theme_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "base": {
                "type": "string",
                "enum": sorted(_THEME_REGISTRY),
                "description": "Base theme name.",
            },
            "overrides": {
                "type": "object",
                "additionalProperties": True,
                "description": (
                    "Theme property overrides applied on top of the base theme. "
                    "Common keys: title_size, label_size, tick_size, font_family, "
                    "background, panel_background, grid_color, legend_position, "
                    "axis_text_x_rotation, strip_text_size."
                ),
            },
        },
        "additionalProperties": False,
    }

    guide_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["legend", "colorbar"],
                "description": "Guide type.",
            },
            "ncol": {"type": "integer"},
            "nrow": {"type": "integer"},
            "reverse": {"type": "boolean"},
            "title": {"type": "string"},
            "barwidth": {"type": "number"},
            "barheight": {"type": "number"},
        },
        "additionalProperties": True,
    }

    annotation_schema: dict[str, Any] = {
        "type": "object",
        "required": ["geom_type"],
        "properties": {
            "geom_type": {
                "type": "string",
                "enum": ["text", "rect", "segment", "curve", "bracket"],
                "description": "Annotation geometry type.",
            },
        },
        "additionalProperties": True,
        "description": (
            "An annotation. Keys depend on geom_type: "
            "text needs x, y, label; rect needs xmin, xmax, ymin, ymax; "
            "segment needs x, y, xend, yend."
        ),
    }

    recipe_names = sorted(_RECIPE_REGISTRY)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Plotten Plot Specification",
        "description": (
            "Declarative specification for building plots with plotten. "
            "Pass to plotten.from_spec(spec, data=df) to create a Plot."
        ),
        "type": "object",
        "properties": {
            "mapping": mapping_schema,
            "layers": {
                "type": "array",
                "items": layer_schema,
                "description": "List of plot layers (geom_*() calls).",
            },
            "scales": {
                "type": "array",
                "items": scale_schema,
                "description": "List of scale specifications.",
            },
            "coord": coord_schema,
            "facet": facet_schema,
            "theme": theme_schema,
            "labs": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "x": {"type": "string"},
                    "y": {"type": "string"},
                    "color": {"type": "string"},
                    "fill": {"type": "string"},
                    "size": {"type": "string"},
                    "caption": {"type": "string"},
                },
                "additionalProperties": True,
                "description": "Axis and legend labels.",
            },
            "guides": {
                "type": "object",
                "additionalProperties": guide_schema,
                "description": (
                    "Guide overrides keyed by aesthetic name (e.g. color, fill, size)."
                ),
            },
            "annotations": {
                "type": "array",
                "items": annotation_schema,
                "description": "List of annotations to overlay on the plot.",
            },
            "recipe": {
                "type": "string",
                "enum": recipe_names,
                "description": (
                    "Shortcut: use a pre-built recipe instead of layers. "
                    "When present, all other keys except data-related ones "
                    "are passed as kwargs to the recipe function."
                ),
            },
        },
        "additionalProperties": False,
    }


# ---------------------------------------------------------------------------
# Forward registries: name → factory function
# ---------------------------------------------------------------------------

_GEOM_REGISTRY: dict[str, Any] = {}
_SCALE_REGISTRY: dict[str, Any] = {}
_COORD_REGISTRY: dict[str, Any] = {}
_POSITION_REGISTRY: dict[str, Any] = {}
_THEME_REGISTRY: dict[str, Any] = {}
_FACET_REGISTRY: dict[str, Any] = {}
_RECIPE_REGISTRY: dict[str, Any] = {}

_registries_built = False


def _build_registries() -> None:
    global _registries_built
    if _registries_built:
        return
    _registries_built = True

    # --- Geoms ---
    from plotten.geoms import (
        geom_abline,
        geom_area,
        geom_bar,
        geom_bin2d,
        geom_blank,
        geom_boxplot,
        geom_col,
        geom_contour,
        geom_contour_filled,
        geom_count,
        geom_crossbar,
        geom_curve,
        geom_density,
        geom_density_ridges,
        geom_dotplot,
        geom_errorbar,
        geom_errorbarh,
        geom_freqpoly,
        geom_hex,
        geom_histogram,
        geom_hline,
        geom_jitter,
        geom_label,
        geom_label_repel,
        geom_line,
        geom_linerange,
        geom_path,
        geom_point,
        geom_pointrange,
        geom_polygon,
        geom_qq,
        geom_qq_line,
        geom_quantile,
        geom_raster,
        geom_rect,
        geom_ribbon,
        geom_rug,
        geom_segment,
        geom_smooth,
        geom_spoke,
        geom_step,
        geom_text,
        geom_text_repel,
        geom_tile,
        geom_violin,
        geom_vline,
        stat_cor,
        stat_density_2d,
        stat_density_2d_filled,
        stat_ecdf,
        stat_ellipse,
        stat_poly_eq,
        stat_sum,
        stat_summary,
        stat_summary_bin,
        stat_unique,
    )

    _geom_map = {
        "point": geom_point,
        "line": geom_line,
        "path": geom_path,
        "step": geom_step,
        "bar": geom_bar,
        "col": geom_col,
        "area": geom_area,
        "ribbon": geom_ribbon,
        "tile": geom_tile,
        "rect": geom_rect,
        "polygon": geom_polygon,
        "text": geom_text,
        "label": geom_label,
        "boxplot": geom_boxplot,
        "violin": geom_violin,
        "errorbar": geom_errorbar,
        "errorbarh": geom_errorbarh,
        "crossbar": geom_crossbar,
        "pointrange": geom_pointrange,
        "linerange": geom_linerange,
        "segment": geom_segment,
        "curve": geom_curve,
        "spoke": geom_spoke,
        "rug": geom_rug,
        "hex": geom_hex,
        "smooth": geom_smooth,
        "histogram": geom_histogram,
        "freqpoly": geom_freqpoly,
        "density": geom_density,
        "density_ridges": geom_density_ridges,
        "dotplot": geom_dotplot,
        "quantile": geom_quantile,
        "contour": geom_contour,
        "contour_filled": geom_contour_filled,
        "raster": geom_raster,
        "blank": geom_blank,
        "hline": geom_hline,
        "vline": geom_vline,
        "abline": geom_abline,
        "jitter": geom_jitter,
        "bin2d": geom_bin2d,
        "count": geom_count,
        "text_repel": geom_text_repel,
        "label_repel": geom_label_repel,
        "qq": geom_qq,
        "qq_line": geom_qq_line,
        # stat_* aliases
        "stat_ecdf": stat_ecdf,
        "stat_ellipse": stat_ellipse,
        "stat_summary": stat_summary,
        "stat_summary_bin": stat_summary_bin,
        "stat_cor": stat_cor,
        "stat_poly_eq": stat_poly_eq,
        "stat_density_2d": stat_density_2d,
        "stat_density_2d_filled": stat_density_2d_filled,
        "stat_sum": stat_sum,
        "stat_unique": stat_unique,
    }
    _GEOM_REGISTRY.update(_geom_map)

    # --- Scales ---
    import plotten.scales as _scales_mod

    for name in dir(_scales_mod):
        if name.startswith("scale_"):
            obj = getattr(_scales_mod, name)
            if callable(obj):
                _SCALE_REGISTRY[name] = obj

    # --- Coords ---
    from plotten.coords import (
        coord_cartesian,
        coord_equal,
        coord_fixed,
        coord_flip,
        coord_polar,
        coord_trans,
    )

    _COORD_REGISTRY.update(
        {
            "coord_cartesian": coord_cartesian,
            "coord_flip": coord_flip,
            "coord_equal": coord_equal,
            "coord_fixed": coord_fixed,
            "coord_polar": coord_polar,
            "coord_trans": coord_trans,
        }
    )

    # --- Positions ---
    from plotten.positions import (
        position_beeswarm,
        position_dodge,
        position_dodge2,
        position_fill,
        position_identity,
        position_jitter,
        position_jitterdodge,
        position_nudge,
        position_stack,
    )

    _POSITION_REGISTRY.update(
        {
            "identity": position_identity,
            "stack": position_stack,
            "fill": position_fill,
            "dodge": position_dodge,
            "dodge2": position_dodge2,
            "jitter": position_jitter,
            "jitterdodge": position_jitterdodge,
            "nudge": position_nudge,
            "beeswarm": position_beeswarm,
        }
    )

    # --- Themes ---
    from plotten.themes import (
        theme_538,
        theme_bw,
        theme_classic,
        theme_dark,
        theme_default,
        theme_economist,
        theme_gray,
        theme_light,
        theme_linedraw,
        theme_minimal,
        theme_seaborn,
        theme_test,
        theme_tufte,
        theme_void,
    )

    _THEME_REGISTRY.update(
        {
            "minimal": theme_minimal,
            "bw": theme_bw,
            "classic": theme_classic,
            "dark": theme_dark,
            "default": theme_default,
            "economist": theme_economist,
            "gray": theme_gray,
            "grey": theme_gray,
            "light": theme_light,
            "linedraw": theme_linedraw,
            "seaborn": theme_seaborn,
            "test": theme_test,
            "tufte": theme_tufte,
            "void": theme_void,
            "538": theme_538,
        }
    )

    # --- Facets ---
    from plotten.facets import facet_grid, facet_wrap

    _FACET_REGISTRY.update(
        {
            "facet_wrap": facet_wrap,
            "facet_grid": facet_grid,
        }
    )

    # --- Recipes ---
    from plotten.recipes import (
        plot_dumbbell,
        plot_forest,
        plot_lollipop,
        plot_slope,
        plot_waffle,
        plot_waterfall,
    )

    _RECIPE_REGISTRY.update(
        {
            "plot_waterfall": plot_waterfall,
            "plot_dumbbell": plot_dumbbell,
            "plot_lollipop": plot_lollipop,
            "plot_slope": plot_slope,
            "plot_forest": plot_forest,
            "plot_waffle": plot_waffle,
        }
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_mapping(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert mapping dict values, handling after_stat/after_scale dicts."""
    from plotten._computed import after_scale, after_stat

    resolved: dict[str, Any] = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            if "after_stat" in value:
                resolved[key] = after_stat(value["after_stat"])
            elif "after_scale" in value:
                resolved[key] = after_scale(value["after_scale"])
            else:
                resolved[key] = value
        else:
            resolved[key] = value
    return resolved


def _resolve_position(pos_spec: str | dict[str, Any] | None) -> Any:
    """Convert a position spec (string or dict) to a Position object."""
    if pos_spec is None:
        return None
    _build_registries()
    if isinstance(pos_spec, str):
        factory = _POSITION_REGISTRY.get(pos_spec)
        if factory is None:
            raise SpecError(
                f"Unknown position: {pos_spec!r}. Valid positions: {sorted(_POSITION_REGISTRY)}"
            )
        return factory()
    if isinstance(pos_spec, dict):
        pos_type = pos_spec.pop("type", None)
        if pos_type is None:
            raise SpecError("Position dict must have a 'type' key.")
        factory = _POSITION_REGISTRY.get(pos_type)
        if factory is None:
            raise SpecError(
                f"Unknown position type: {pos_type!r}. "
                f"Valid positions: {sorted(_POSITION_REGISTRY)}"
            )
        return factory(**pos_spec)
    return pos_spec


# ---------------------------------------------------------------------------
# from_spec
# ---------------------------------------------------------------------------


def from_spec(spec: dict[str, Any], data: Any = None) -> Any:
    """Build a :class:`~plotten.Plot` from a declarative dict specification.

    Parameters
    ----------
    spec : dict
        Plot specification.  Call :func:`spec_schema` for the full JSON
        Schema, or see the examples below.
    data : DataFrame, optional
        Default dataset.

    Returns
    -------
    Plot

    Examples
    --------
    Scatter plot with color mapping::

        from_spec({
            "mapping": {"x": "speed", "y": "dist", "color": "group"},
            "layers": [{"geom": "point", "size": 50, "alpha": 0.8}],
        }, data=df)

    Multi-layer plot with a trend line::

        from_spec({
            "mapping": {"x": "x", "y": "y"},
            "layers": [
                {"geom": "point", "color": "steelblue"},
                {"geom": "smooth", "method": "lm", "se": False},
            ],
            "labs": {"title": "Speed vs Distance", "x": "Speed (mph)"},
        }, data=df)

    Faceted bar chart with a custom theme::

        from_spec({
            "mapping": {"x": "category", "fill": "group"},
            "layers": [{"geom": "bar", "position": "dodge"}],
            "facet": {"fn": "facet_wrap", "facets": "region", "ncol": 2},
            "scales": [
                {"fn": "scale_fill_manual", "values": {"a": "red", "b": "blue"}}
            ],
            "theme": {"base": "minimal", "overrides": {"legend_position": "bottom"}},
        }, data=df)

    Reference lines::

        from_spec({
            "mapping": {"x": "x", "y": "y"},
            "layers": [
                {"geom": "point"},
                {"geom": "hline", "yintercept": 5, "color": "red", "linetype": "dashed"},
                {"geom": "vline", "xintercept": 3, "color": "grey", "alpha": 0.5},
            ],
        }, data=df)

    Histogram with computed aesthetic::

        from_spec({
            "layers": [{
                "geom": "histogram",
                "mapping": {"x": "value", "y": {"after_stat": "density"}},
                "bins": 30,
                "fill": "steelblue",
            }],
        }, data=df)

    Recipe shortcut (all non-recipe keys become kwargs)::

        from_spec({"recipe": "plot_waterfall", "x": "cat", "y": "val"}, data=df)

    Raises
    ------
    SpecError
        If the spec contains unknown geom, scale, coord, theme, facet,
        guide, position, or recipe names, or if a layer dict is missing
        the required ``"geom"`` key.
    """
    _build_registries()
    from plotten._aes import aes
    from plotten._labs import labs
    from plotten._plot import ggplot
    from plotten.themes._theme import theme

    # --- Recipes shortcut ---
    if "recipe" in spec:
        recipe_name = spec["recipe"]
        factory = _RECIPE_REGISTRY.get(recipe_name)
        if factory is None:
            raise SpecError(
                f"Unknown recipe: {recipe_name!r}. Valid recipes: {sorted(_RECIPE_REGISTRY)}"
            )
        recipe_kwargs = {k: v for k, v in spec.items() if k != "recipe"}
        return factory(data, **recipe_kwargs)

    # --- Build base plot ---
    mapping_raw = spec.get("mapping", {})
    mapping_kwargs = _resolve_mapping(mapping_raw)
    plot = ggplot(data, aes(**mapping_kwargs))

    # --- Layers ---
    for layer_spec in spec.get("layers", []):
        layer_spec = dict(layer_spec)  # don't mutate caller's dict
        geom_name = layer_spec.pop("geom", None)
        if geom_name is None:
            raise SpecError("Each layer must have a 'geom' key.")
        factory = _GEOM_REGISTRY.get(geom_name)
        if factory is None:
            raise SpecError(f"Unknown geom: {geom_name!r}. Valid geoms: {sorted(_GEOM_REGISTRY)}")
        # Extract layer-level mapping
        layer_mapping = layer_spec.pop("mapping", None)
        # Handle position
        pos = layer_spec.pop("position", None)
        if pos is not None:
            layer_spec["position"] = _resolve_position(pos)
        # Convert mapping values
        if layer_mapping:
            layer_mapping = _resolve_mapping(layer_mapping)
            layer_spec.update(layer_mapping)
        layer = factory(**layer_spec)
        plot = plot + layer

    # --- Scales ---
    for scale_spec in spec.get("scales", []):
        scale_spec = dict(scale_spec)
        fn_name = scale_spec.pop("fn", None)
        if fn_name is None:
            raise SpecError("Each scale must have an 'fn' key.")
        factory = _SCALE_REGISTRY.get(fn_name)
        if factory is None:
            raise SpecError(f"Unknown scale: {fn_name!r}. Valid scales: {sorted(_SCALE_REGISTRY)}")
        plot = plot + factory(**scale_spec)

    # --- Coord ---
    coord_spec = spec.get("coord")
    if coord_spec is not None:
        coord_spec = dict(coord_spec)
        fn_name = coord_spec.pop("fn", None)
        if fn_name is None:
            raise SpecError("Coord must have an 'fn' key.")
        factory = _COORD_REGISTRY.get(fn_name)
        if factory is None:
            raise SpecError(f"Unknown coord: {fn_name!r}. Valid coords: {sorted(_COORD_REGISTRY)}")
        plot = plot + factory(**coord_spec)

    # --- Facet ---
    facet_spec = spec.get("facet")
    if facet_spec is not None:
        facet_spec = dict(facet_spec)
        fn_name = facet_spec.pop("fn", None)
        if fn_name is None:
            raise SpecError("Facet must have an 'fn' key.")
        factory = _FACET_REGISTRY.get(fn_name)
        if factory is None:
            raise SpecError(f"Unknown facet: {fn_name!r}. Valid facets: {sorted(_FACET_REGISTRY)}")
        plot = plot + factory(**facet_spec)

    # --- Theme ---
    theme_spec = spec.get("theme")
    if theme_spec is not None:
        base_name = theme_spec.get("base")
        if base_name is not None:
            base_factory = _THEME_REGISTRY.get(base_name)
            if base_factory is None:
                raise SpecError(
                    f"Unknown theme: {base_name!r}. Valid themes: {sorted(_THEME_REGISTRY)}"
                )
            plot = plot + base_factory()
        overrides = theme_spec.get("overrides")
        if overrides:
            plot = plot + theme(**overrides)

    # --- Labs ---
    labs_spec = spec.get("labs")
    if labs_spec is not None:
        plot = plot + labs(**labs_spec)

    # --- Guides ---
    guides_spec = spec.get("guides")
    if guides_spec is not None:
        from plotten._guides import guide_colorbar, guide_legend, guides

        guide_dict: dict[str, Any] = {}
        for aes_name, guide_spec in guides_spec.items():
            guide_spec = dict(guide_spec)
            guide_type = guide_spec.pop("type", "legend")
            if guide_type == "legend":
                guide_dict[aes_name] = guide_legend(**guide_spec)
            elif guide_type == "colorbar":
                guide_dict[aes_name] = guide_colorbar(**guide_spec)
            else:
                raise SpecError(f"Unknown guide type: {guide_type!r}. Use 'legend' or 'colorbar'.")
        plot = plot + guides(**guide_dict)

    # --- Annotations ---
    for annot_spec in spec.get("annotations", []):
        from plotten._annotate import annotate

        annot_spec = dict(annot_spec)
        plot = plot + annotate(**annot_spec)

    return plot


def from_spec_json(json_str: str, data: Any = None) -> Any:
    """Build a Plot from a JSON string spec."""
    import json

    spec = json.loads(json_str)
    return from_spec(spec, data)
