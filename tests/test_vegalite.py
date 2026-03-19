"""Tests for Vega-Lite export."""

from __future__ import annotations

import json
import warnings

import polars as pl
import pytest

from plotten import (
    Plot,
    PlottenError,
    PlottenWarning,
    aes,
    labs,
    to_html,
    to_vegalite,
)
from plotten._computed import AfterStat
from plotten._layer import Layer
from plotten.coords import (
    CoordCartesian,
    CoordEqual,
    CoordFlip,
    CoordPolar,
    CoordTrans,
)
from plotten.facets._grid import FacetGrid
from plotten.facets._wrap import FacetWrap
from plotten.geoms._bar import GeomBar
from plotten.geoms._boxplot import GeomBoxplot
from plotten.geoms._col import GeomCol
from plotten.geoms._contour import GeomContour
from plotten.geoms._density import GeomDensity
from plotten.geoms._errorbar import GeomErrorbar
from plotten.geoms._freqpoly import GeomFreqpoly
from plotten.geoms._histogram import GeomHistogram
from plotten.geoms._line import GeomLine
from plotten.geoms._point import GeomPoint
from plotten.geoms._rect import GeomRect
from plotten.geoms._refline import GeomHLine, GeomVLine
from plotten.geoms._ribbon import GeomRibbon
from plotten.geoms._segment import GeomSegment
from plotten.geoms._smooth import GeomSmooth
from plotten.geoms._step import GeomStep
from plotten.geoms._text import GeomText
from plotten.geoms._tile import GeomTile
from plotten.positions._dodge import PositionDodge
from plotten.positions._fill import PositionFill
from plotten.positions._jitter import PositionJitter
from plotten.positions._stack import PositionStack
from plotten.scales._brewer import ScaleBrewerDiscrete
from plotten.scales._color import ScaleColorDiscrete
from plotten.scales._date import ScaleDateContinuous
from plotten.scales._gradient import ScaleGradient, ScaleGradient2
from plotten.scales._log import ScaleLog
from plotten.scales._position import ScaleContinuous
from plotten.scales._reverse import ScaleReverse
from plotten.scales._sqrt import ScaleSqrt
from plotten.stats._count import StatCount
from plotten.stats._identity import StatIdentity
from plotten.themes._elements import ElementBlank
from plotten.themes._theme import Theme as ThemeClass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sample_df() -> pl.DataFrame:
    return pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "g": ["a", "b", "a"]})


def _scatter_plot() -> Plot:
    return Plot(
        data=_sample_df(),
        mapping=aes(x="x", y="y"),
        layers=(Layer(geom=GeomPoint()),),
    )


def _line_plot() -> Plot:
    return Plot(
        data=_sample_df(),
        mapping=aes(x="x", y="y"),
        layers=(Layer(geom=GeomLine()),),
    )


def _bar_plot() -> Plot:
    return Plot(
        data=_sample_df(),
        mapping=aes(x="g", y="y"),
        layers=(Layer(geom=GeomBar(), stat=StatCount()),),
    )


# ===========================================================================
# Phase 1: Skeleton — Point, Line, Bar
# ===========================================================================


class TestDataSerialization:
    def test_polars_dataframe(self) -> None:
        spec = to_vegalite(_scatter_plot())
        assert "data" in spec
        assert len(spec["data"]["values"]) == 3
        assert spec["data"]["values"][0] == {"x": 1, "y": 4, "g": "a"}

    def test_pandas_dataframe(self) -> None:
        pdf = _sample_df().to_pandas()
        p = Plot(data=pdf, mapping=aes(x="x", y="y"), layers=(Layer(geom=GeomPoint()),))
        spec = to_vegalite(p)
        assert len(spec["data"]["values"]) == 3

    def test_datetime_serialization(self) -> None:
        from datetime import date

        df = pl.DataFrame({"d": [date(2024, 1, 1)], "y": [1]})
        p = Plot(data=df, mapping=aes(x="d", y="y"), layers=(Layer(geom=GeomPoint()),))
        spec = to_vegalite(p)
        assert spec["data"]["values"][0]["d"].startswith("2024-01-01")


class TestBasicMarks:
    def test_scatter_produces_point_mark(self) -> None:
        spec = to_vegalite(_scatter_plot())
        assert spec["mark"]["type"] == "point"

    def test_line_produces_line_mark(self) -> None:
        spec = to_vegalite(_line_plot())
        assert spec["mark"]["type"] == "line"

    def test_bar_produces_bar_mark(self) -> None:
        spec = to_vegalite(_bar_plot())
        assert spec["mark"]["type"] == "bar"

    def test_col_produces_bar_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g", y="y"),
            layers=(Layer(geom=GeomCol()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "bar"

    def test_step_produces_line_with_interpolate(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomStep()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "line"
        assert spec["mark"]["interpolate"] == "step-after"

    def test_text_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", label="g"),
            layers=(Layer(geom=GeomText()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "text"
        assert spec["encoding"]["text"]["field"] == "g"

    def test_rect_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomRect()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "rect"

    def test_tile_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomTile()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "rect"

    def test_boxplot_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g", y="y"),
            layers=(Layer(geom=GeomBoxplot()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "boxplot"


class TestEncoding:
    def test_x_y_encoding(self) -> None:
        spec = to_vegalite(_scatter_plot())
        assert spec["encoding"]["x"]["field"] == "x"
        assert spec["encoding"]["y"]["field"] == "y"

    def test_color_encoding(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="g"),
            layers=(Layer(geom=GeomPoint()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["color"]["field"] == "g"

    def test_size_encoding(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", size="y"),
            layers=(Layer(geom=GeomPoint()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["size"]["field"] == "y"

    def test_alpha_maps_to_opacity(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", alpha="y"),
            layers=(Layer(geom=GeomPoint()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["opacity"]["field"] == "y"

    def test_shape_encoding(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", shape="g"),
            layers=(Layer(geom=GeomPoint()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["shape"]["field"] == "g"

    def test_group_maps_to_detail(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", group="g"),
            layers=(Layer(geom=GeomLine()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["detail"]["field"] == "g"


class TestMultiLayer:
    def test_multi_layer_produces_layer_array(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()), Layer(geom=GeomLine())),
        )
        spec = to_vegalite(p)
        assert "layer" in spec
        assert len(spec["layer"]) == 2
        assert spec["layer"][0]["mark"]["type"] == "point"
        assert spec["layer"][1]["mark"]["type"] == "line"

    def test_layer_data_override(self) -> None:
        df2 = pl.DataFrame({"x": [10], "y": [20]})
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()), Layer(geom=GeomLine(), data=df2)),
        )
        spec = to_vegalite(p)
        assert "data" not in spec["layer"][0]
        assert spec["layer"][1]["data"]["values"] == [{"x": 10, "y": 20}]


class TestUnsupported:
    def test_unsupported_geom_raises(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomContour()),),
        )
        with pytest.raises(PlottenError, match="GeomContour is not supported"):
            to_vegalite(p)

    def test_after_stat_raises(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y=AfterStat("count")),
            layers=(Layer(geom=GeomPoint()),),
        )
        with pytest.raises(PlottenError, match="AfterStat"):
            to_vegalite(p)


class TestVegaliteSchema:
    def test_has_schema_field(self) -> None:
        spec = to_vegalite(_scatter_plot())
        assert spec["$schema"] == "https://vega.github.io/schema/vega-lite/v5.json"

    def test_spec_is_json_serializable(self) -> None:
        spec = to_vegalite(_scatter_plot())
        json.dumps(spec)  # Should not raise


# ===========================================================================
# Phase 2: Stats + Positions + Tier 2 Geoms
# ===========================================================================


class TestStats:
    def test_stat_count(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g"),
            layers=(Layer(geom=GeomBar(), stat=StatCount()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"]["aggregate"] == "count"

    def test_stat_bin_histogram(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x"),
            layers=(Layer(geom=GeomHistogram()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"].get("bin") is not None
        assert spec["encoding"]["y"]["aggregate"] == "count"

    def test_stat_smooth_loess(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomSmooth()),),
        )
        spec = to_vegalite(p)
        assert any("loess" in str(t) for t in spec.get("transform", []))

    def test_stat_smooth_lm(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomSmooth(method="lm")),),
        )
        spec = to_vegalite(p)
        assert any("regression" in str(t) for t in spec.get("transform", []))

    def test_stat_density(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x"),
            layers=(Layer(geom=GeomDensity()),),
        )
        spec = to_vegalite(p)
        assert any("density" in str(t) for t in spec.get("transform", []))

    def test_stat_identity_no_transform(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint(), stat=StatIdentity()),),
        )
        spec = to_vegalite(p)
        assert "transform" not in spec


class TestPositions:
    def test_position_stack(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g", y="y", color="g"),
            layers=(Layer(geom=GeomBar(), stat=StatCount(), position=PositionStack()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"].get("stack") is True

    def test_position_fill(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g", y="y", color="g"),
            layers=(Layer(geom=GeomBar(), stat=StatCount(), position=PositionFill()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"].get("stack") == "normalize"

    def test_position_dodge(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="g", y="y", color="g"),
            layers=(Layer(geom=GeomBar(), stat=StatCount(), position=PositionDodge()),),
        )
        spec = to_vegalite(p)
        assert "xOffset" in spec["encoding"]

    def test_position_jitter_warns(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint(), position=PositionJitter()),),
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            to_vegalite(p)
            assert any(issubclass(x.category, PlottenWarning) for x in w)


class TestTier2Geoms:
    def test_hline(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(
                Layer(geom=GeomPoint()),
                Layer(geom=GeomHLine(yintercept=5.0)),
            ),
        )
        spec = to_vegalite(p)
        hline_layer = spec["layer"][1]
        assert hline_layer["mark"]["type"] == "rule"
        assert hline_layer["encoding"]["y"]["datum"] == 5.0

    def test_vline(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(
                Layer(geom=GeomPoint()),
                Layer(geom=GeomVLine(xintercept=2.0)),
            ),
        )
        spec = to_vegalite(p)
        vline_layer = spec["layer"][1]
        assert vline_layer["mark"]["type"] == "rule"
        assert vline_layer["encoding"]["x"]["datum"] == 2.0

    def test_ribbon(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", ymin="y", ymax="y"),
            layers=(Layer(geom=GeomRibbon()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "area"

    def test_segment(self) -> None:
        df = pl.DataFrame({"x": [1], "y": [2], "xend": [3], "yend": [4]})
        p = Plot(
            data=df,
            mapping=aes(x="x", y="y", xend="xend", yend="yend"),
            layers=(Layer(geom=GeomSegment()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "rule"
        assert "x2" in spec["encoding"]
        assert "y2" in spec["encoding"]

    def test_errorbar(self) -> None:
        df = pl.DataFrame({"x": [1], "ymin": [2], "ymax": [4]})
        p = Plot(
            data=df,
            mapping=aes(x="x", ymin="ymin", ymax="ymax"),
            layers=(Layer(geom=GeomErrorbar()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "rule"

    def test_freqpoly(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x"),
            layers=(Layer(geom=GeomFreqpoly()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "line"

    def test_density_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x"),
            layers=(Layer(geom=GeomDensity()),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["type"] == "area"


# ===========================================================================
# Phase 3: Scales + Coords + Labs
# ===========================================================================


class TestScales:
    def test_continuous_limits(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleContinuous(aesthetic="x", limits=(0, 10)),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["scale"]["domain"] == [0, 10]

    def test_scale_log(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleLog(aesthetic="y"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"]["scale"]["type"] == "log"

    def test_scale_sqrt(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleSqrt(aesthetic="y"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"]["scale"]["type"] == "sqrt"

    def test_scale_reverse(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleReverse(aesthetic="y"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["y"]["sort"] == "descending"

    def test_brewer_scheme(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="g"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleBrewerDiscrete(palette="Set2"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["color"]["scale"]["scheme"] == "Set2"

    def test_gradient(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleGradient(aesthetic="color", low="#ff0000", high="#0000ff"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["color"]["scale"]["range"] == ["#ff0000", "#0000ff"]

    def test_gradient2_midpoint(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleGradient2(aesthetic="color"),),
        )
        spec = to_vegalite(p)
        cs = spec["encoding"]["color"]["scale"]
        assert len(cs["range"]) == 3
        assert "domainMid" in cs

    def test_color_discrete_values(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="g"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleColorDiscrete(values={"a": "red", "b": "blue"}),),
        )
        spec = to_vegalite(p)
        cs = spec["encoding"]["color"]["scale"]
        assert cs["domain"] == ["a", "b"]
        assert cs["range"] == ["red", "blue"]

    def test_continuous_breaks(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleContinuous(aesthetic="x", breaks=[1, 2, 3]),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["axis"]["values"] == [1, 2, 3]

    def test_type_inference_from_scale(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleContinuous(aesthetic="x"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["type"] == "quantitative"

    def test_date_scale_temporal_type(self) -> None:
        from datetime import date

        df = pl.DataFrame({"d": [date(2024, 1, 1)], "y": [1]})
        p = Plot(
            data=df,
            mapping=aes(x="d", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleDateContinuous(aesthetic="x"),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["type"] == "temporal"


class TestCoords:
    def test_coord_cartesian_limits(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordCartesian(xlim=(0, 5), ylim=(0, 10)),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["scale"]["domain"] == [0, 5]
        assert spec["encoding"]["y"]["scale"]["domain"] == [0, 10]

    def test_coord_flip_swaps_xy(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordFlip(),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["field"] == "y"
        assert spec["encoding"]["y"]["field"] == "x"

    def test_coord_polar_raises(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordPolar(),
        )
        with pytest.raises(PlottenError, match="CoordPolar"):
            to_vegalite(p)

    def test_coord_equal_warns(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordEqual(),
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            to_vegalite(p)
            assert any(issubclass(x.category, PlottenWarning) for x in w)

    def test_coord_trans_identity_ok(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordTrans(x="identity", y="identity"),
        )
        to_vegalite(p)  # Should not raise

    def test_coord_trans_non_identity_raises(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordTrans(x="log10", y="identity"),
        )
        with pytest.raises(PlottenError, match="CoordTrans"):
            to_vegalite(p)


class TestLabs:
    def test_title(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(title="My Plot"),
        )
        spec = to_vegalite(p)
        assert spec["title"] == "My Plot"

    def test_title_subtitle(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(title="Title", subtitle="Subtitle"),
        )
        spec = to_vegalite(p)
        assert spec["title"]["text"] == "Title"
        assert spec["title"]["subtitle"] == "Subtitle"

    def test_axis_labels(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(x="X Axis", y="Y Axis"),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["x"]["title"] == "X Axis"
        assert spec["encoding"]["y"]["title"] == "Y Axis"

    def test_color_label(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", color="g"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(color="Group"),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["color"]["title"] == "Group"

    def test_caption_no_crash(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(caption="Source: test"),
        )
        spec = to_vegalite(p)
        # Caption has no VL equivalent, just verify no crash
        assert "$schema" in spec


# ===========================================================================
# Phase 4: Facets + Theme + HTML
# ===========================================================================


class TestFacets:
    def test_facet_wrap(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            facet=FacetWrap(facets="g", ncol=2),
        )
        spec = to_vegalite(p)
        assert spec["facet"]["field"] == "g"
        assert spec["columns"] == 2
        assert "spec" in spec

    def test_facet_grid(self) -> None:
        df = pl.DataFrame({"x": [1, 2], "y": [3, 4], "r": ["r1", "r2"], "c": ["c1", "c2"]})
        p = Plot(
            data=df,
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            facet=FacetGrid(rows="r", cols="c"),
        )
        spec = to_vegalite(p)
        assert "row" in spec["facet"]
        assert "column" in spec["facet"]
        assert spec["facet"]["row"]["field"] == "r"
        assert spec["facet"]["column"]["field"] == "c"

    def test_facet_free_scales(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            facet=FacetWrap(facets="g", scales="free"),
        )
        spec = to_vegalite(p)
        assert spec["resolve"]["scale"]["x"] == "independent"
        assert spec["resolve"]["scale"]["y"] == "independent"

    def test_facet_free_x(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            facet=FacetWrap(facets="g", scales="free_x"),
        )
        spec = to_vegalite(p)
        assert spec["resolve"]["scale"]["x"] == "independent"
        assert "y" not in spec["resolve"]["scale"]


class TestTheme:
    def test_background(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(background="#f0f0f0"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["background"] == "#f0f0f0"

    def test_font_family(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(font_family="Arial"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["font"] == "Arial"

    def test_legend_none_disables(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(legend_position="none"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["legend"]["disable"] is True

    def test_legend_position(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(legend_position="bottom"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["legend"]["orient"] == "bottom"

    def test_element_blank_disables_grid(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(panel_grid_major=ElementBlank()),
        )
        spec = to_vegalite(p)
        assert spec["config"]["axis"]["grid"] is False

    def test_panel_background(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(panel_background="#ffffff"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["view"]["fill"] == "#ffffff"

    def test_title_config(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            theme=ThemeClass(title_size=20, title_color="#333333"),
        )
        spec = to_vegalite(p)
        assert spec["config"]["title"]["fontSize"] == 20
        assert spec["config"]["title"]["color"] == "#333333"


class TestHTML:
    def test_html_contains_vega_embed(self) -> None:
        html = to_html(_scatter_plot())
        assert "vegaEmbed" in html
        assert "vega-embed@6" in html

    def test_html_contains_spec(self) -> None:
        html = to_html(_scatter_plot())
        assert '"$schema"' in html
        assert '"mark"' in html

    def test_html_is_valid_structure(self) -> None:
        html = to_html(_scatter_plot())
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_html_spec_is_valid_json(self) -> None:
        html = to_html(_scatter_plot())
        # Extract the JSON spec from the script tag
        start = html.index("vegaEmbed('#vis', ") + len("vegaEmbed('#vis', ")
        end = html.index(");</script>")
        spec_str = html[start:end]
        spec = json.loads(spec_str)
        assert spec["$schema"] == "https://vega.github.io/schema/vega-lite/v5.json"


class TestMarkParams:
    def test_alpha_param(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint(), params={"alpha": 0.5}),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["opacity"] == 0.5

    def test_color_param(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint(), params={"color": "red"}),),
        )
        spec = to_vegalite(p)
        assert spec["mark"]["color"] == "red"


# ===========================================================================
# Robustness + Edge Cases
# ===========================================================================


class TestRobustness:
    def test_no_internal_labs_key_in_spec(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            labs=labs(x="X", y="Y"),
        )
        spec = to_vegalite(p)
        assert "_labs" not in spec

    def test_nan_serialized_as_null(self) -> None:
        df = pl.DataFrame({"x": [1.0, float("nan")], "y": [2.0, 3.0]})
        p = Plot(
            data=df,
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
        )
        spec = to_vegalite(p)
        assert spec["data"]["values"][1]["x"] is None
        # Must be JSON-serializable (NaN would crash json.dumps)
        json.dumps(spec)

    def test_html_escapes_script_closing_tag(self) -> None:
        df = pl.DataFrame({"x": [1], "y": [1], "label": ["</script><script>"]})
        p = Plot(
            data=df,
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
        )
        html = to_html(p)
        assert "</script><script>" not in html
        assert "<\\/script>" in html

    def test_multi_layer_faceted(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()), Layer(geom=GeomLine())),
            facet=FacetWrap(facets="g"),
        )
        spec = to_vegalite(p)
        assert "spec" in spec
        assert "layer" in spec["spec"]
        assert len(spec["spec"]["layer"]) == 2

    def test_needs_precompute_native_stats(self) -> None:
        from plotten._vegalite._stats import needs_precompute
        from plotten.stats._bin import StatBin
        from plotten.stats._smooth import StatSmooth

        assert needs_precompute(None) is False
        assert needs_precompute(StatIdentity()) is False
        assert needs_precompute(StatCount()) is False
        assert needs_precompute(StatBin()) is False
        assert needs_precompute(StatSmooth()) is False

    def test_needs_precompute_unsupported_stat(self) -> None:
        from plotten._vegalite._stats import needs_precompute
        from plotten.stats._ecdf import StatECDF

        assert needs_precompute(StatECDF()) is True

    def test_interaction_maps_to_detail(self) -> None:
        from plotten._interaction import Interaction

        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y", group=Interaction(columns=("g",))),
            layers=(Layer(geom=GeomLine()),),
        )
        spec = to_vegalite(p)
        assert spec["encoding"]["detail"]["field"] == "g"

    def test_scale_on_unmapped_channel_ignored(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            scales=(ScaleColorDiscrete(values={"a": "red"}),),
        )
        spec = to_vegalite(p)
        assert "color" not in spec["encoding"]

    def test_coord_flip_with_limits(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(Layer(geom=GeomPoint()),),
            coord=CoordFlip(xlim=(0, 5)),
        )
        spec = to_vegalite(p)
        # After flip, original x becomes y, and xlim applies to the new y
        assert spec["encoding"]["x"]["field"] == "y"
        assert spec["encoding"]["y"]["field"] == "x"

    def test_hline_style_params_on_mark(self) -> None:
        p = Plot(
            data=_sample_df(),
            mapping=aes(x="x", y="y"),
            layers=(
                Layer(geom=GeomPoint()),
                Layer(geom=GeomHLine(yintercept=3.0, color="red", alpha=0.5)),
            ),
        )
        spec = to_vegalite(p)
        hline_mark = spec["layer"][1]["mark"]
        assert hline_mark["color"] == "red"
        assert hline_mark["opacity"] == 0.5
