"""plotten — a grammar-of-graphics plotting library for Python."""

from plotten._aes import Aes, aes
from plotten._labs import Labs, labs
from plotten._plot import Plot, ggplot
from plotten.coords import CoordCartesian, CoordFlip, coord_flip
from plotten.facets import FacetGrid, FacetWrap, facet_grid, facet_wrap
from plotten.geoms import (
    geom_bar,
    geom_boxplot,
    geom_histogram,
    geom_label,
    geom_line,
    geom_point,
    geom_smooth,
    geom_text,
)
from plotten.scales import (
    ScaleColorContinuous,
    ScaleColorDiscrete,
    ScaleContinuous,
    ScaleDiscrete,
    ScaleLog,
    scale_color_continuous,
    scale_color_discrete,
    scale_x_log10,
    scale_y_log10,
)
from plotten.themes import Theme, theme_dark, theme_default, theme_minimal

__all__ = [
    "Aes",
    "CoordCartesian",
    "CoordFlip",
    "FacetGrid",
    "FacetWrap",
    "Labs",
    "Plot",
    "ScaleColorContinuous",
    "ScaleColorDiscrete",
    "ScaleContinuous",
    "ScaleDiscrete",
    "ScaleLog",
    "Theme",
    "aes",
    "coord_flip",
    "facet_grid",
    "facet_wrap",
    "geom_bar",
    "geom_boxplot",
    "geom_histogram",
    "geom_label",
    "geom_line",
    "geom_point",
    "geom_smooth",
    "geom_text",
    "ggplot",
    "labs",
    "scale_color_continuous",
    "scale_color_discrete",
    "scale_x_log10",
    "scale_y_log10",
    "theme_dark",
    "theme_default",
    "theme_minimal",
]
