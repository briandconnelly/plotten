"""Tests for declarative spec format: from_spec."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from plotten import (
    Plot,
    from_spec,
    from_spec_json,
    spec_schema,
)
from plotten._validation import SpecError


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 3, 5, 4],
            "group": ["a", "a", "b", "b", "b"],
        }
    )


# ---------------------------------------------------------------------------
# from_spec basics
# ---------------------------------------------------------------------------


class TestFromSpec:
    def test_basic_scatter(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
        }
        plot = from_spec(spec, data=sample_df)
        assert isinstance(plot, Plot)
        assert plot.mapping.x == "x"
        assert plot.mapping.y == "y"
        assert len(plot.layers) == 1

    def test_layer_with_fixed_params(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point", "color": "steelblue", "size": 50, "alpha": 0.8}],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 1

    def test_layer_with_mapping(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point", "mapping": {"color": "group"}}],
        }
        plot = from_spec(spec, data=sample_df)
        layer = plot.layers[0]
        assert layer.mapping.color == "group"

    def test_multi_layer(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [
                {"geom": "point", "color": "steelblue"},
                {"geom": "smooth", "method": "lm", "se": False},
            ],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 2

    def test_hline_geom(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [
                {"geom": "point"},
                {"geom": "hline", "yintercept": 3.5, "color": "red", "linetype": "dashed"},
            ],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 2

    def test_vline_geom(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [
                {"geom": "point"},
                {"geom": "vline", "xintercept": 3},
            ],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 2

    def test_histogram(self, sample_df):
        spec = {
            "layers": [{"geom": "histogram", "mapping": {"x": "x"}, "bins": 10}],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 1

    def test_scales(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "scales": [{"fn": "scale_x_log10"}],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.scales) == 1

    def test_coord_flip(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "coord": {"fn": "coord_flip"},
        }
        plot = from_spec(spec, data=sample_df)
        from plotten.coords._flip import CoordFlip

        assert isinstance(plot.coord, CoordFlip)

    def test_facet_wrap(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "facet": {"fn": "facet_wrap", "facets": "group", "n_cols": 2},
        }
        plot = from_spec(spec, data=sample_df)
        from plotten.facets._wrap import FacetWrap

        assert isinstance(plot.facet, FacetWrap)

    def test_theme_base_and_overrides(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "theme": {"base": "minimal", "overrides": {"title_size": 16}},
        }
        plot = from_spec(spec, data=sample_df)
        assert plot.theme.title_size == 16

    def test_labs(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "labs": {"title": "My Plot", "x": "Speed"},
        }
        plot = from_spec(spec, data=sample_df)
        assert plot.labs.title == "My Plot"
        assert plot.labs.x == "Speed"

    def test_guides(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y", "color": "group"},
            "layers": [{"geom": "point"}],
            "guides": {
                "color": {"type": "legend", "n_cols": 2},
            },
        }
        plot = from_spec(spec, data=sample_df)
        assert plot.guides is not None
        assert "color" in plot.guides

    def test_guides_colorbar(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y", "color": "y"},
            "layers": [{"geom": "point"}],
            "guides": {
                "color": {"type": "colorbar", "barwidth": 15},
            },
        }
        plot = from_spec(spec, data=sample_df)
        from plotten._guides import GuideColorbar

        assert isinstance(plot.guides["color"], GuideColorbar)

    def test_annotations(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "annotations": [
                {"geom_type": "rect", "xmin": 1, "xmax": 3, "ymin": 2, "ymax": 4, "alpha": 0.3}
            ],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 2  # point + annotation

    def test_after_stat_mapping(self, sample_df):
        spec = {
            "layers": [
                {
                    "geom": "histogram",
                    "mapping": {"x": "x", "y": {"after_stat": "density"}},
                }
            ],
        }
        plot = from_spec(spec, data=sample_df)
        from plotten._computed import AfterStat

        layer = plot.layers[0]
        assert isinstance(layer.mapping.y, AfterStat)
        assert layer.mapping.y.var == "density"

    def test_position_string(self, sample_df):
        spec = {
            "mapping": {"x": "group", "fill": "group"},
            "layers": [{"geom": "bar", "position": "dodge"}],
        }
        plot = from_spec(spec, data=sample_df)
        from plotten.positions._dodge import PositionDodge

        assert isinstance(plot.layers[0].position, PositionDodge)

    def test_position_dict(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point", "position": {"type": "jitter", "width": 0.2}}],
        }
        plot = from_spec(spec, data=sample_df)
        from plotten.positions._jitter import PositionJitter

        assert isinstance(plot.layers[0].position, PositionJitter)

    def test_recipe(self, sample_df):
        df = pd.DataFrame({"cat": ["a", "b", "c"], "val": [10, -5, 3]})
        spec = {"recipe": "plot_waterfall", "x": "cat", "y": "val"}
        plot = from_spec(spec, data=df)
        assert isinstance(plot, Plot)

    def test_empty_spec(self, sample_df):
        spec = {}
        plot = from_spec(spec, data=sample_df)
        assert isinstance(plot, Plot)

    def test_unknown_geom_raises(self, sample_df):
        spec = {"layers": [{"geom": "nonexistent"}]}
        with pytest.raises(SpecError, match="Unknown geom"):
            from_spec(spec, data=sample_df)

    def test_missing_geom_key_raises(self, sample_df):
        spec = {"layers": [{"color": "red"}]}
        with pytest.raises(SpecError, match="must have a 'geom' key"):
            from_spec(spec, data=sample_df)

    def test_unknown_scale_raises(self, sample_df):
        spec = {"scales": [{"fn": "scale_nonexistent"}]}
        with pytest.raises(SpecError, match="Unknown scale"):
            from_spec(spec, data=sample_df)

    def test_unknown_coord_raises(self, sample_df):
        spec = {"coord": {"fn": "coord_nonexistent"}}
        with pytest.raises(SpecError, match="Unknown coord"):
            from_spec(spec, data=sample_df)

    def test_unknown_theme_raises(self, sample_df):
        spec = {"theme": {"base": "nonexistent"}}
        with pytest.raises(SpecError, match="Unknown theme"):
            from_spec(spec, data=sample_df)

    def test_unknown_recipe_raises(self, sample_df):
        spec = {"recipe": "nonexistent"}
        with pytest.raises(SpecError, match="Unknown recipe"):
            from_spec(spec, data=sample_df)


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------


class TestJSON:
    def test_from_json(self, sample_df):
        json_str = json.dumps(
            {
                "mapping": {"x": "x", "y": "y"},
                "layers": [{"geom": "point"}],
            }
        )
        plot = from_spec_json(json_str, data=sample_df)
        assert isinstance(plot, Plot)

    def test_from_json_with_labs(self, sample_df):
        json_str = json.dumps(
            {
                "mapping": {"x": "x", "y": "y"},
                "layers": [{"geom": "point"}],
                "labs": {"title": "Test"},
            }
        )
        plot = from_spec_json(json_str, data=sample_df)
        assert plot.labs.title == "Test"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_multiple_scales(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "scales": [{"fn": "scale_x_log10"}, {"fn": "scale_y_log10"}],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.scales) == 2

    def test_stat_geom_aliases(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "stat_ecdf", "mapping": {"x": "x"}}],
        }
        plot = from_spec(spec, data=sample_df)
        assert len(plot.layers) == 1

    def test_theme_only_overrides(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "theme": {"overrides": {"title_size": 20}},
        }
        plot = from_spec(spec, data=sample_df)
        assert plot.theme.title_size == 20

    def test_theme_only_base(self, sample_df):
        spec = {
            "mapping": {"x": "x", "y": "y"},
            "layers": [{"geom": "point"}],
            "theme": {"base": "dark"},
        }
        plot = from_spec(spec, data=sample_df)
        assert isinstance(plot, Plot)

    def test_all_geom_names_valid(self):
        """Ensure every registered geom name produces a callable."""
        from plotten._spec import _GEOM_REGISTRY, _build_registries

        _build_registries()
        for name, factory in _GEOM_REGISTRY.items():
            assert callable(factory), f"{name} is not callable"


# ---------------------------------------------------------------------------
# spec_schema
# ---------------------------------------------------------------------------


class TestSpecSchema:
    def test_returns_dict(self):
        schema = spec_schema()
        assert isinstance(schema, dict)

    def test_has_json_schema_meta(self):
        schema = spec_schema()
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert "title" in schema

    def test_top_level_properties(self):
        schema = spec_schema()
        props = set(schema["properties"])
        assert props == {
            "mapping",
            "layers",
            "scales",
            "coord",
            "facet",
            "theme",
            "labs",
            "guides",
            "annotations",
            "recipe",
        }

    def test_geom_enum_populated(self):
        schema = spec_schema()
        geom_enum = schema["properties"]["layers"]["items"]["properties"]["geom"]["enum"]
        assert "point" in geom_enum
        assert "line" in geom_enum
        assert "histogram" in geom_enum
        assert "smooth" in geom_enum
        assert geom_enum == sorted(geom_enum), "geom enum should be sorted"

    def test_scale_enum_populated(self):
        schema = spec_schema()
        scale_enum = schema["properties"]["scales"]["items"]["properties"]["fn"]["enum"]
        assert "scale_x_log10" in scale_enum
        assert "scale_color_manual" in scale_enum

    def test_coord_enum_populated(self):
        schema = spec_schema()
        coord_enum = schema["properties"]["coord"]["properties"]["fn"]["enum"]
        assert "coord_flip" in coord_enum
        assert "coord_polar" in coord_enum

    def test_position_enum_populated(self):
        schema = spec_schema()
        layer_props = schema["properties"]["layers"]["items"]["properties"]
        # position can be a string enum or a dict
        pos_one_of = layer_props["position"]["oneOf"]
        string_enum = pos_one_of[0]["enum"]
        assert "dodge" in string_enum
        assert "jitter" in string_enum

    def test_theme_enum_populated(self):
        schema = spec_schema()
        theme_enum = schema["properties"]["theme"]["properties"]["base"]["enum"]
        assert "minimal" in theme_enum
        assert "dark" in theme_enum

    def test_recipe_enum_populated(self):
        schema = spec_schema()
        recipe_enum = schema["properties"]["recipe"]["enum"]
        assert "plot_waterfall" in recipe_enum

    def test_json_serializable(self):
        """Schema must be JSON-serializable so it can be embedded in prompts."""
        schema = spec_schema()
        json_str = json.dumps(schema)
        roundtripped = json.loads(json_str)
        assert roundtripped == schema

    def test_no_additional_top_level_properties(self):
        schema = spec_schema()
        assert schema.get("additionalProperties") is False
