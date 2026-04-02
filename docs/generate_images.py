"""Generate ALL example images for the documentation site.

Run from the project root:
    uv run python docs/generate_images.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import polars as pl

from plotten import (
    aes,
    coord_cartesian,
    coord_equal,
    coord_flip,
    coord_polar,
    coord_trans,
    facet_grid,
    facet_wrap,
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
    geom_signif,
    geom_smooth,
    geom_spoke,
    geom_step,
    geom_text,
    geom_text_repel,
    geom_tile,
    geom_violin,
    geom_vline,
    ggplot,
    labeller_both,
    labs,
    position_beeswarm,
    position_dodge,
    position_fill,
    position_jitter,
    position_jitterdodge,
    position_nudge,
    position_stack,
    scale_alpha_continuous,
    scale_color_brewer,
    scale_color_continuous,
    scale_color_discrete,
    scale_color_gradient,
    scale_color_gradient2,
    scale_color_grey,
    scale_color_manual,
    scale_color_viridis,
    scale_fill_brewer,
    scale_fill_gradient,
    scale_fill_gradient2,
    scale_fill_viridis,
    scale_hatch_discrete,
    scale_linetype_discrete,
    scale_shape_discrete,
    scale_size_area,
    scale_size_continuous,
    scale_x_binned,
    scale_x_continuous,
    scale_x_date,
    scale_x_log10,
    scale_x_reverse,
    scale_x_sqrt,
    scale_y_continuous,
    stat_cor,
    stat_density_2d,
    stat_ecdf,
    stat_ellipse,
    stat_function,
    stat_poly_eq,
    stat_summary,
    stat_summary_bin,
    stat_unique,
    theme_538,
    theme_bw,
    theme_classic,
    theme_dark,
    theme_default,
    theme_economist,
    theme_grey,
    theme_light,
    theme_linedraw,
    theme_minimal,
    theme_seaborn,
    theme_tufte,
    theme_void,
)
from plotten.datasets import load_dataset
from plotten.recipes import (
    plot_dumbbell,
    plot_forest,
    plot_lollipop,
    plot_slope,
    plot_waffle,
    plot_waterfall,
)
from plotten.scales import (
    breaks_integer,
    breaks_log,
    breaks_pretty,
    breaks_quantile,
    breaks_width,
    label_comma,
    label_dollar,
    label_percent,
    label_scientific,
    label_si,
)

# ── Output directories ──────────────────────────────────────────────────────

BASE = Path("docs/images/generated")
SUBDIRS = [
    "geoms",
    "scales",
    "stats",
    "positions",
    "coords",
    "themes",
    "facets",
    "gallery",
    "recipes",
]

for subdir in SUBDIRS:
    (BASE / subdir).mkdir(parents=True, exist_ok=True)

DPI = 150
W, H = 6, 4  # default width/height


def save(plot, subdir: str, name: str, width: float = W, height: float = H) -> None:
    path = f"{BASE}/{subdir}/{name}.png"
    plot.save(path, width=width, height=height, dpi=DPI)
    print(f"  Saved {path}")


# ── Load datasets ───────────────────────────────────────────────────────────

mpg = load_dataset("mpg")
# diamonds has x/y/z dimension columns that conflict with aes(x=, y=) — drop them
diamonds = load_dataset("diamonds").drop("x", "y", "z")
tips = load_dataset("tips")
penguins = load_dataset("penguins")
faithful = load_dataset("faithful")

rng = np.random.default_rng(42)

# ═══════════════════════════════════════════════════════════════════════════════
# GEOMS
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating geom images...")

# ── geom_point ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + labs(title="geom_point", x="Displacement (L)", y="Highway MPG"),
    "geoms",
    "point",
)

# ── geom_jitter ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="drv", y="hwy"))
    + geom_jitter(width=0.2, alpha=0.6)
    + labs(title="geom_jitter", x="Drive train", y="Highway MPG"),
    "geoms",
    "jitter",
)

# ── geom_count ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="cyl", y="drv"))
    + geom_count(alpha=0.6)
    + labs(title="geom_count", x="Cylinders", y="Drive train"),
    "geoms",
    "count",
)

# ── geom_line ────────────────────────────────────────────────────────────────

economics = pl.DataFrame(
    {
        "year": list(range(2000, 2021)),
        "value": [
            100,
            103,
            101,
            105,
            110,
            108,
            115,
            120,
            112,
            105,
            110,
            115,
            118,
            122,
            128,
            135,
            140,
            138,
            145,
            150,
            155,
        ],
    }
)

save(
    ggplot(economics, aes(x="year", y="value"))
    + geom_line(color="#2c3e50", linewidth=1)
    + labs(title="geom_line", x="Year", y="Value"),
    "geoms",
    "line",
)

# ── geom_path ────────────────────────────────────────────────────────────────

t = np.linspace(0, 2 * np.pi, 50)
spiral = pl.DataFrame({"x": (t * np.cos(t)).tolist(), "y": (t * np.sin(t)).tolist()})

save(
    ggplot(spiral, aes(x="x", y="y"))
    + geom_path(color="#8e44ad", linewidth=0.8)
    + labs(title="geom_path"),
    "geoms",
    "path",
)

# ── geom_step ────────────────────────────────────────────────────────────────

step_df = pl.DataFrame({"x": list(range(10)), "y": [1, 3, 2, 5, 4, 7, 6, 8, 9, 7]})

save(
    ggplot(step_df, aes(x="x", y="y"))
    + geom_step(color="#e74c3c", linewidth=1)
    + labs(title="geom_step", x="X", y="Y"),
    "geoms",
    "step",
)

# ── geom_segment ─────────────────────────────────────────────────────────────

seg_df = pl.DataFrame(
    {
        "x": [1.0, 2.0, 3.0, 4.0],
        "y": [1.0, 3.0, 2.0, 4.0],
        "xend": [2.0, 3.0, 4.0, 5.0],
        "yend": [3.0, 2.0, 4.0, 3.0],
    }
)

save(
    ggplot(seg_df, aes(x="x", y="y", xend="xend", yend="yend"))
    + geom_segment(linewidth=1, color="#2980b9")
    + labs(title="geom_segment"),
    "geoms",
    "segment",
)

# ── geom_curve ───────────────────────────────────────────────────────────────

save(
    ggplot(seg_df, aes(x="x", y="y", xend="xend", yend="yend"))
    + geom_curve(linewidth=1, color="#27ae60", curvature=0.3)
    + labs(title="geom_curve"),
    "geoms",
    "curve",
)

# ── geom_spoke ───────────────────────────────────────────────────────────────

angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
spoke_df = pl.DataFrame(
    {
        "x": [0.0] * 12,
        "y": [0.0] * 12,
        "angle": angles.tolist(),
        "radius": [1.0] * 12,
    }
)

save(
    ggplot(spoke_df, aes(x="x", y="y", angle="angle", radius="radius"))
    + geom_spoke(linewidth=0.8, color="#e67e22")
    + coord_equal()
    + labs(title="geom_spoke"),
    "geoms",
    "spoke",
)

# ── geom_area ────────────────────────────────────────────────────────────────

area_df = pl.DataFrame({"x": list(range(20)), "y": rng.uniform(2, 8, 20).tolist()})

save(
    ggplot(area_df, aes(x="x", y="y"))
    + geom_area(alpha=0.6, fill="#3498db")
    + labs(title="geom_area", x="X", y="Y"),
    "geoms",
    "area",
)

# ── geom_ribbon ──────────────────────────────────────────────────────────────

x_vals = list(range(20))
y_mid = rng.uniform(3, 7, 20)
ribbon_df = pl.DataFrame(
    {
        "x": x_vals,
        "ymin": (y_mid - rng.uniform(0.5, 1.5, 20)).tolist(),
        "ymax": (y_mid + rng.uniform(0.5, 1.5, 20)).tolist(),
        "y": y_mid.tolist(),
    }
)

save(
    ggplot(ribbon_df, aes(x="x", ymin="ymin", ymax="ymax"))
    + geom_ribbon(alpha=0.4, fill="#9b59b6")
    + geom_line(mapping=aes(y="y"), color="#8e44ad")
    + labs(title="geom_ribbon", x="X", y="Y"),
    "geoms",
    "ribbon",
)

# ── geom_bar ─────────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="#3498db", alpha=0.8)
    + labs(title="geom_bar", x="Vehicle class", y="Count"),
    "geoms",
    "bar",
)

# ── geom_col ─────────────────────────────────────────────────────────────────

col_df = pl.DataFrame({"category": ["A", "B", "C", "D", "E"], "value": [23, 45, 12, 67, 34]})

save(
    ggplot(col_df, aes(x="category", y="value"))
    + geom_col(fill="#e74c3c", alpha=0.8)
    + labs(title="geom_col", x="Category", y="Value"),
    "geoms",
    "col",
)

# ── geom_histogram ───────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(bins=20, fill="#2ecc71", alpha=0.8)
    + labs(title="geom_histogram", x="Highway MPG", y="Count"),
    "geoms",
    "histogram",
)

# ── geom_density ─────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", fill="drv"))
    + geom_density(alpha=0.5)
    + labs(title="geom_density", x="Highway MPG", y="Density"),
    "geoms",
    "density",
)

# ── geom_freqpoly ───────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", color="drv"))
    + geom_freqpoly(bins=20, linewidth=1)
    + labs(title="geom_freqpoly", x="Highway MPG", y="Count"),
    "geoms",
    "freqpoly",
)

# ── geom_dotplot ─────────────────────────────────────────────────────────────

save(
    ggplot(faithful, aes(x="eruptions"))
    + geom_dotplot(fill="#f39c12", alpha=0.8)
    + labs(title="geom_dotplot", x="Eruption duration (min)"),
    "geoms",
    "dotplot",
)

# ── geom_boxplot ─────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_boxplot(fill="#3498db", alpha=0.7)
    + labs(title="geom_boxplot", x="Vehicle class", y="Highway MPG"),
    "geoms",
    "boxplot",
    width=7,
)

# ── geom_violin ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_violin(fill="#9b59b6", alpha=0.7)
    + labs(title="geom_violin", x="Vehicle class", y="Highway MPG"),
    "geoms",
    "violin",
    width=7,
)

# ── geom_density_ridges ──────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", y="class"))
    + geom_density_ridges(alpha=0.7)
    + labs(title="geom_density_ridges", x="Highway MPG"),
    "geoms",
    "density_ridges",
    width=7,
    height=5,
)

# ── geom_qq / geom_qq_line (scipy-dependent) ────────────────────────────────

qq_data = pl.DataFrame({"x": rng.standard_normal(200).tolist()})

try:
    save(
        ggplot(qq_data, aes(x="x"))
        + geom_qq(alpha=0.6)
        + geom_qq_line(color="#e74c3c")
        + labs(title="geom_qq + geom_qq_line"),
        "geoms",
        "qq",
    )

    save(
        ggplot(qq_data, aes(x="x"))
        + geom_qq_line(color="#e74c3c")
        + geom_qq(alpha=0.6)
        + labs(title="geom_qq_line"),
        "geoms",
        "qq_line",
    )
except (ImportError, Exception) as exc:
    print(f"  Skipping geom_qq/geom_qq_line ({exc})")

# ── geom_quantile (scipy-dependent) ─────────────────────────────────────────

try:
    save(
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_quantile()
        + geom_point(alpha=0.3)
        + labs(title="geom_quantile", x="Displacement (L)", y="Highway MPG"),
        "geoms",
        "quantile",
    )
except ImportError:
    print("  Skipping geom_quantile (scipy not available)")

# ── geom_bin2d ───────────────────────────────────────────────────────────────

save(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_bin2d(bins=30, alpha=0.9)
    + labs(title="geom_bin2d", x="Carat", y="Price"),
    "geoms",
    "bin2d",
)

# ── geom_hex ─────────────────────────────────────────────────────────────────

save(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_hex(bins=25)
    + labs(title="geom_hex", x="Carat", y="Price"),
    "geoms",
    "hex",
)

# ── geom_contour (scipy-dependent) ──────────────────────────────────────────

grid_x, grid_y = np.meshgrid(np.linspace(-3, 3, 50), np.linspace(-3, 3, 50))
grid_z = np.exp(-(grid_x**2 + grid_y**2) / 2)
contour_df = pl.DataFrame(
    {
        "x": grid_x.ravel().tolist(),
        "y": grid_y.ravel().tolist(),
        "z": grid_z.ravel().tolist(),
    }
)

try:
    save(
        ggplot(contour_df, aes(x="x", y="y", z="z"))
        + geom_contour(color="#2c3e50")
        + labs(title="geom_contour"),
        "geoms",
        "contour",
    )
except (ImportError, Exception) as exc:
    print(f"  Skipping geom_contour ({exc})")

# ── geom_contour_filled (scipy-dependent) ───────────────────────────────────

try:
    save(
        ggplot(contour_df, aes(x="x", y="y", z="z"))
        + geom_contour_filled(alpha=0.8)
        + labs(title="geom_contour_filled"),
        "geoms",
        "contour_filled",
    )
except (ImportError, Exception) as exc:
    print(f"  Skipping geom_contour_filled ({exc})")

# ── geom_raster ──────────────────────────────────────────────────────────────

raster_x, raster_y = np.meshgrid(np.linspace(-2, 2, 40), np.linspace(-2, 2, 40))
raster_z = np.sin(raster_x) * np.cos(raster_y)
raster_df = pl.DataFrame(
    {
        "x": raster_x.ravel().tolist(),
        "y": raster_y.ravel().tolist(),
        "z": raster_z.ravel().tolist(),
    }
)

save(
    ggplot(raster_df, aes(x="x", y="y", z="z")) + geom_raster() + labs(title="geom_raster"),
    "geoms",
    "raster",
)

# ── geom_tile ────────────────────────────────────────────────────────────────

tile_df = pl.DataFrame(
    {
        "x": ["A", "B", "C", "D"] * 4,
        "y": [v for v in ["W", "X", "Y", "Z"] for _ in range(4)],
        "fill": rng.uniform(0, 10, 16).tolist(),
    }
)

save(
    ggplot(tile_df, aes(x="x", y="y", fill="fill"))
    + geom_tile()
    + scale_fill_viridis()
    + labs(title="geom_tile"),
    "geoms",
    "tile",
)

# ── geom_errorbar ────────────────────────────────────────────────────────────

err_df = pl.DataFrame(
    {
        "x": ["A", "B", "C", "D"],
        "y": [3.2, 4.5, 2.8, 5.1],
        "ymin": [2.7, 3.9, 2.2, 4.5],
        "ymax": [3.7, 5.1, 3.4, 5.7],
    }
)

save(
    ggplot(err_df, aes(x="x", y="y", ymin="ymin", ymax="ymax"))
    + geom_errorbar(width=0.2)
    + geom_point(size=30)
    + labs(title="geom_errorbar", x="Group", y="Value"),
    "geoms",
    "errorbar",
)

# ── geom_errorbarh ───────────────────────────────────────────────────────────

errh_df = pl.DataFrame(
    {
        "y": ["A", "B", "C", "D"],
        "x": [3.2, 4.5, 2.8, 5.1],
        "xmin": [2.7, 3.9, 2.2, 4.5],
        "xmax": [3.7, 5.1, 3.4, 5.7],
    }
)

save(
    ggplot(errh_df, aes(y="y", x="x", xmin="xmin", xmax="xmax"))
    + geom_errorbarh(height=0.2)
    + geom_point(size=30)
    + labs(title="geom_errorbarh", x="Value", y="Group"),
    "geoms",
    "errorbarh",
)

# ── geom_crossbar ────────────────────────────────────────────────────────────

save(
    ggplot(err_df, aes(x="x", y="y", ymin="ymin", ymax="ymax"))
    + geom_crossbar(width=0.4, fill="#3498db", alpha=0.5)
    + labs(title="geom_crossbar", x="Group", y="Value"),
    "geoms",
    "crossbar",
)

# ── geom_pointrange ──────────────────────────────────────────────────────────

save(
    ggplot(err_df, aes(x="x", y="y", ymin="ymin", ymax="ymax"))
    + geom_pointrange(color="#e74c3c")
    + labs(title="geom_pointrange", x="Group", y="Value"),
    "geoms",
    "pointrange",
)

# ── geom_linerange ───────────────────────────────────────────────────────────

save(
    ggplot(err_df, aes(x="x", y="y", ymin="ymin", ymax="ymax"))
    + geom_linerange(color="#2ecc71", linewidth=1.5)
    + labs(title="geom_linerange", x="Group", y="Value"),
    "geoms",
    "linerange",
)

# ── geom_text ────────────────────────────────────────────────────────────────

text_df = pl.DataFrame(
    {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [2.0, 4.0, 3.0, 5.0, 1.0],
        "label": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    }
)

save(
    ggplot(text_df, aes(x="x", y="y", label="label"))
    + geom_point(size=20)
    + geom_text(va="bottom")
    + labs(title="geom_text"),
    "geoms",
    "text",
)

# ── geom_label ───────────────────────────────────────────────────────────────

save(
    ggplot(text_df, aes(x="x", y="y", label="label"))
    + geom_point(size=20)
    + geom_label(va="bottom")
    + labs(title="geom_label"),
    "geoms",
    "label",
)

# ── geom_text_repel ──────────────────────────────────────────────────────────

repel_df = pl.DataFrame(
    {
        "x": [1.0, 1.2, 1.1, 3.0, 3.1, 5.0, 5.2, 5.1, 7.0, 7.1],
        "y": [2.0, 2.1, 1.9, 4.0, 4.2, 3.0, 3.1, 2.8, 5.0, 5.1],
        "name": [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
        ],
    }
)

save(
    ggplot(repel_df, aes(x="x", y="y", label="name"))
    + geom_point(size=30, color="#2c3e50")
    + geom_text_repel()
    + labs(title="geom_text_repel"),
    "geoms",
    "text_repel",
)

# ── geom_label_repel ─────────────────────────────────────────────────────────

save(
    ggplot(repel_df, aes(x="x", y="y", label="name"))
    + geom_point(size=30, color="#2c3e50")
    + geom_label_repel()
    + labs(title="geom_label_repel"),
    "geoms",
    "label_repel",
)

# ── geom_hline ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_hline(yintercept=25, color="#e74c3c", linewidth=1, linetype="dashed")
    + labs(title="geom_hline", x="Displacement (L)", y="Highway MPG"),
    "geoms",
    "hline",
)

# ── geom_vline ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_vline(xintercept=4, color="#2980b9", linewidth=1, linetype="dashed")
    + labs(title="geom_vline", x="Displacement (L)", y="Highway MPG"),
    "geoms",
    "vline",
)

# ── geom_abline ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_abline(intercept=35, slope=-3.5, color="#e67e22", linewidth=1)
    + labs(title="geom_abline", x="Displacement (L)", y="Highway MPG"),
    "geoms",
    "abline",
)

# ── geom_rect ────────────────────────────────────────────────────────────────

rect_df = pl.DataFrame(
    {
        "xmin": [1.0, 3.0, 5.0],
        "xmax": [2.5, 4.5, 7.0],
        "ymin": [1.0, 2.0, 0.5],
        "ymax": [3.0, 5.0, 2.5],
        "group": ["A", "B", "C"],
    }
)

save(
    ggplot(rect_df, aes(xmin="xmin", xmax="xmax", ymin="ymin", ymax="ymax", fill="group"))
    + geom_rect(alpha=0.6)
    + labs(title="geom_rect"),
    "geoms",
    "rect",
)

# ── geom_polygon ─────────────────────────────────────────────────────────────

# Star shape
star_angles = np.linspace(0, 2 * np.pi, 11)[:-1]
star_r = [2.0, 1.0] * 5
star_x = [r * math.cos(a - math.pi / 2) for r, a in zip(star_r, star_angles, strict=True)]
star_y = [r * math.sin(a - math.pi / 2) for r, a in zip(star_r, star_angles, strict=True)]
poly_df = pl.DataFrame({"x": star_x, "y": star_y})

save(
    ggplot(poly_df, aes(x="x", y="y"))
    + geom_polygon(fill="#f1c40f", color="#f39c12")
    + coord_equal()
    + labs(title="geom_polygon"),
    "geoms",
    "polygon",
)

# ── geom_rug ─────────────────────────────────────────────────────────────────

save(
    ggplot(faithful, aes(x="eruptions", y="waiting"))
    + geom_point(alpha=0.4)
    + geom_rug(alpha=0.3)
    + labs(title="geom_rug", x="Eruption duration (min)", y="Waiting time (min)"),
    "geoms",
    "rug",
)

# ── geom_smooth ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="ols", color="#e74c3c")
    + labs(title="geom_smooth (OLS)", x="Displacement (L)", y="Highway MPG"),
    "geoms",
    "smooth",
)

# ── geom_blank ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_blank()
    + labs(
        title="geom_blank (sets up axes with no data drawn)", x="Displacement", y="Highway MPG"
    ),
    "geoms",
    "blank",
)

# ── geom_signif ──────────────────────────────────────────────────────────────

signif_df = pl.DataFrame(
    {
        "group": ["Control"] * 30 + ["Treatment"] * 30,
        "value": rng.normal(5, 1, 30).tolist() + rng.normal(7, 1.2, 30).tolist(),
    }
)

save(
    ggplot(signif_df, aes(x="group", y="value"))
    + geom_boxplot(fill="#3498db", alpha=0.6)
    + geom_signif(comparisons=[("Control", "Treatment")])
    + labs(title="geom_signif", x="Group", y="Value"),
    "geoms",
    "signif",
)


# ═══════════════════════════════════════════════════════════════════════════════
# SCALES
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating scale images...")

# ── Position scales ──────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + scale_x_continuous(breaks=breaks_pretty(n=6))
    + labs(title="scale_x_continuous", x="Displacement (L)", y="Highway MPG"),
    "scales",
    "x_continuous",
)

save(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_point(alpha=0.1, size=5)
    + scale_x_log10()
    + labs(title="scale_x_log10", x="Carat (log10)", y="Price"),
    "scales",
    "x_log10",
)

save(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_point(alpha=0.1, size=5)
    + scale_x_sqrt()
    + labs(title="scale_x_sqrt", x="Carat (sqrt)", y="Price"),
    "scales",
    "x_sqrt",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + scale_x_reverse()
    + labs(title="scale_x_reverse", x="Displacement (L, reversed)", y="Highway MPG"),
    "scales",
    "x_reverse",
)

# scale_x_date
date_df = pl.DataFrame(
    {
        "date": [f"2024-{m:02d}-01" for m in range(1, 13)],
        "value": rng.uniform(50, 150, 12).tolist(),
    }
).with_columns(pl.col("date").str.to_date())

save(
    ggplot(date_df, aes(x="date", y="value"))
    + geom_line(color="#2c3e50", linewidth=1)
    + geom_point(size=20)
    + scale_x_date()
    + labs(title="scale_x_date", x="Date", y="Value"),
    "scales",
    "x_date",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + scale_x_binned()
    + labs(title="scale_x_binned", x="Displacement (binned)", y="Highway MPG"),
    "scales",
    "x_binned",
)

# ── Color scales ─────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_continuous()
    + labs(title="scale_color_continuous"),
    "scales",
    "color_continuous",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_discrete()
    + labs(title="scale_color_discrete"),
    "scales",
    "color_discrete",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_manual(values={"4": "#e74c3c", "f": "#2ecc71", "r": "#3498db"})
    + labs(title="scale_color_manual"),
    "scales",
    "color_manual",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_brewer(palette="Set2")
    + labs(title="scale_color_brewer (Set2)"),
    "scales",
    "color_brewer",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_viridis()
    + labs(title="scale_color_viridis"),
    "scales",
    "color_viridis",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_gradient(low="#ffffcc", high="#006837")
    + labs(title="scale_color_gradient"),
    "scales",
    "color_gradient",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_gradient2(low="#2166ac", mid="#f7f7f7", high="#b2182b", midpoint=20)
    + labs(title="scale_color_gradient2"),
    "scales",
    "color_gradient2",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(size=20, alpha=0.7)
    + scale_color_grey()
    + labs(title="scale_color_grey"),
    "scales",
    "color_grey",
)

# ── Fill scales ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", fill="drv"))
    + geom_bar(alpha=0.8)
    + scale_fill_brewer(palette="Pastel1")
    + labs(title="scale_fill_brewer (Pastel1)", x="Vehicle class", y="Count"),
    "scales",
    "fill_brewer",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_bin2d(bins=15)
    + scale_fill_viridis()
    + labs(title="scale_fill_viridis", x="Displacement (L)", y="Highway MPG"),
    "scales",
    "fill_viridis",
)

save(
    ggplot(raster_df, aes(x="x", y="y", fill="fill"))
    + geom_raster()
    + scale_fill_gradient(low="#f7fbff", high="#08306b")
    + labs(title="scale_fill_gradient"),
    "scales",
    "fill_gradient",
)

# ── Size scales ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", size="cty"))
    + geom_point(alpha=0.5)
    + scale_size_continuous()
    + labs(title="scale_size_continuous"),
    "scales",
    "size_continuous",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy", size="cty"))
    + geom_point(alpha=0.5)
    + scale_size_area(max_size=15)
    + labs(title="scale_size_area"),
    "scales",
    "size_area",
)

# ── Alpha scale ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", alpha="cty"))
    + geom_point(size=20, color="#2c3e50")
    + scale_alpha_continuous()
    + labs(title="scale_alpha_continuous"),
    "scales",
    "alpha_continuous",
)

# ── Shape scale ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", shape="drv"))
    + geom_point(size=20, alpha=0.7)
    + scale_shape_discrete()
    + labs(title="scale_shape_discrete"),
    "scales",
    "shape_discrete",
)

# ── Linetype scale ───────────────────────────────────────────────────────────

line_df = pl.DataFrame(
    {
        "x": list(range(10)) * 3,
        "y": [v + i * 2 for i in range(3) for v in rng.uniform(0, 5, 10).tolist()],
        "group": [g for g in ["A", "B", "C"] for _ in range(10)],
    }
)

save(
    ggplot(line_df, aes(x="x", y="y", linetype="group"))
    + geom_line(linewidth=1)
    + scale_linetype_discrete()
    + labs(title="scale_linetype_discrete"),
    "scales",
    "linetype_discrete",
)

# ── Hatch scale ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", hatch="drv"))
    + geom_bar(alpha=0.7)
    + scale_hatch_discrete()
    + labs(title="scale_hatch_discrete", x="Vehicle class", y="Count"),
    "scales",
    "hatch_discrete",
)

# ── Breaks ───────────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + scale_x_continuous(breaks=breaks_pretty(n=10))
    + labs(title="breaks_pretty(n=10)"),
    "scales",
    "breaks_pretty",
)

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + scale_x_continuous(breaks=breaks_width(0.5))
    + labs(title="breaks_width(0.5)"),
    "scales",
    "breaks_width",
)

save(
    ggplot(mpg, aes(x="cyl", y="hwy"))
    + geom_jitter(width=0.2, alpha=0.4)
    + scale_x_continuous(breaks=breaks_integer())
    + labs(title="breaks_integer()"),
    "scales",
    "breaks_integer",
)

log_df = pl.DataFrame(
    {"x": np.logspace(0, 4, 100).tolist(), "y": rng.uniform(1, 10, 100).tolist()}
)

save(
    ggplot(log_df, aes(x="x", y="y"))
    + geom_point(alpha=0.5)
    + scale_x_continuous(breaks=breaks_log())
    + labs(title="breaks_log()"),
    "scales",
    "breaks_log",
)

# breaks_quantile needs the data upfront
mpg_native = mpg.to_native()
hwy_vals = mpg_native["hwy"].to_list()

save(
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(bins=20, alpha=0.7)
    + scale_x_continuous(breaks=breaks_quantile(hwy_vals))
    + labs(title="breaks_quantile()"),
    "scales",
    "breaks_quantile",
)

# ── Labels ───────────────────────────────────────────────────────────────────

price_df = pl.DataFrame(
    {"item": ["A", "B", "C", "D"], "revenue": [1_250_000, 850_000, 2_100_000, 430_000]}
)

save(
    ggplot(price_df, aes(x="item", y="revenue"))
    + geom_col(fill="#3498db", alpha=0.8)
    + scale_y_continuous(labels=label_comma())
    + labs(title="label_comma", y="Revenue"),
    "scales",
    "label_comma",
)

pct_df = pl.DataFrame({"group": ["A", "B", "C", "D"], "rate": [0.15, 0.42, 0.73, 0.28]})

save(
    ggplot(pct_df, aes(x="group", y="rate"))
    + geom_col(fill="#2ecc71", alpha=0.8)
    + scale_y_continuous(labels=label_percent())
    + labs(title="label_percent", y="Rate"),
    "scales",
    "label_percent",
)

save(
    ggplot(price_df, aes(x="item", y="revenue"))
    + geom_col(fill="#e67e22", alpha=0.8)
    + scale_y_continuous(labels=label_dollar())
    + labs(title="label_dollar", y="Revenue"),
    "scales",
    "label_dollar",
)

sci_df = pl.DataFrame({"x": ["A", "B", "C", "D"], "y": [2.5e6, 1.3e4, 8.7e5, 4.1e3]})

save(
    ggplot(sci_df, aes(x="x", y="y"))
    + geom_col(fill="#9b59b6", alpha=0.8)
    + scale_y_continuous(labels=label_scientific())
    + labs(title="label_scientific"),
    "scales",
    "label_scientific",
)

save(
    ggplot(sci_df, aes(x="x", y="y"))
    + geom_col(fill="#1abc9c", alpha=0.8)
    + scale_y_continuous(labels=label_si())
    + labs(title="label_si"),
    "scales",
    "label_si",
)


# ═══════════════════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating stat images...")

# ── stat_ecdf ────────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", color="drv"))
    + stat_ecdf()
    + labs(title="stat_ecdf", x="Highway MPG", y="ECDF"),
    "stats",
    "ecdf",
)

# ── stat_summary ─────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", y="hwy"))
    + stat_summary()
    + labs(title="stat_summary (mean +/- SE)", x="Vehicle class", y="Highway MPG"),
    "stats",
    "summary",
    width=7,
)

# ── stat_summary_bin ─────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + stat_summary_bin(bins=8)
    + labs(title="stat_summary_bin", x="Displacement (L)", y="Highway MPG"),
    "stats",
    "summary_bin",
)

# ── stat_function ────────────────────────────────────────────────────────────

save(
    ggplot()
    + stat_function(fun=np.sin, xlim=(-2 * np.pi, 2 * np.pi), color="#e74c3c")
    + stat_function(fun=np.cos, xlim=(-2 * np.pi, 2 * np.pi), color="#3498db")
    + labs(title="stat_function (sin & cos)", x="x", y="y"),
    "stats",
    "function",
)

# ── stat_density_2d (scipy-dependent) ────────────────────────────────────────

try:
    save(
        ggplot(faithful, aes(x="eruptions", y="waiting"))
        + geom_point(alpha=0.3)
        + stat_density_2d(color="#2c3e50")
        + labs(
            title="stat_density_2d",
            x="Eruption duration (min)",
            y="Waiting time (min)",
        ),
        "stats",
        "density_2d",
    )
except (ImportError, Exception) as exc:
    print(f"  Skipping stat_density_2d ({exc})")

# ── stat_ellipse (scipy-dependent) ───────────────────────────────────────────

try:
    save(
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point(alpha=0.5)
        + stat_ellipse()
        + labs(title="stat_ellipse", x="Displacement (L)", y="Highway MPG"),
        "stats",
        "ellipse",
    )
except (ImportError, Exception) as exc:
    print(f"  Skipping stat_ellipse ({exc})")

# ── stat_cor ─────────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + stat_cor()
    + labs(title="stat_cor", x="Displacement (L)", y="Highway MPG"),
    "stats",
    "cor",
)

# ── stat_poly_eq ─────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="ols")
    + stat_poly_eq()
    + labs(title="stat_poly_eq", x="Displacement (L)", y="Highway MPG"),
    "stats",
    "poly_eq",
)

# ── stat_unique ──────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + stat_unique(alpha=0.6)
    + labs(title="stat_unique (deduplicated points)", x="Displacement (L)", y="Highway MPG"),
    "stats",
    "unique",
)


# ═══════════════════════════════════════════════════════════════════════════════
# POSITIONS
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating position images...")

# ── position_dodge ───────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", fill="drv"))
    + geom_bar(position=position_dodge(), alpha=0.8)
    + labs(title="position_dodge", x="Vehicle class", y="Count"),
    "positions",
    "dodge",
    width=7,
)

# ── position_jitter ──────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="drv", y="hwy"))
    + geom_point(position=position_jitter(width=0.2), alpha=0.5)
    + labs(title="position_jitter", x="Drive train", y="Highway MPG"),
    "positions",
    "jitter",
)

# ── position_stack ───────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", fill="drv"))
    + geom_bar(position=position_stack(), alpha=0.8)
    + labs(title="position_stack", x="Vehicle class", y="Count"),
    "positions",
    "stack",
    width=7,
)

# ── position_fill ────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", fill="drv"))
    + geom_bar(position=position_fill(), alpha=0.8)
    + labs(title="position_fill", x="Vehicle class", y="Proportion"),
    "positions",
    "fill",
    width=7,
)

# ── position_nudge ───────────────────────────────────────────────────────────

nudge_df = pl.DataFrame(
    {
        "x": [1.0, 2.0, 3.0, 4.0],
        "y": [3.0, 5.0, 4.0, 6.0],
        "label": ["A", "B", "C", "D"],
    }
)

save(
    ggplot(nudge_df, aes(x="x", y="y", label="label"))
    + geom_point(size=30)
    + geom_text(position=position_nudge(x=0.2, y=0.3))
    + labs(title="position_nudge"),
    "positions",
    "nudge",
)

# ── position_beeswarm ───────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="drv", y="hwy"))
    + geom_point(position=position_beeswarm(), alpha=0.6, size=10)
    + labs(title="position_beeswarm", x="Drive train", y="Highway MPG"),
    "positions",
    "beeswarm",
)

# ── position_jitterdodge ─────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", y="hwy", color="drv"))
    + geom_point(position=position_jitterdodge(jitter_width=0.15), alpha=0.5, size=10)
    + labs(title="position_jitterdodge", x="Vehicle class", y="Highway MPG"),
    "positions",
    "jitterdodge",
    width=7,
)


# ═══════════════════════════════════════════════════════════════════════════════
# COORDS
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating coord images...")

# ── coord_cartesian (with limits) ────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + coord_cartesian(xlim=(2, 5), ylim=(15, 35))
    + labs(title="coord_cartesian (zoomed)", x="Displacement (L)", y="Highway MPG"),
    "coords",
    "cartesian",
)

# ── coord_flip ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="#3498db", alpha=0.8)
    + coord_flip()
    + labs(title="coord_flip", x="Vehicle class", y="Count"),
    "coords",
    "flip",
)

# ── coord_polar ──────────────────────────────────────────────────────────────

wind_df = pl.DataFrame(
    {
        "direction": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        "speed": [12, 8, 15, 6, 10, 14, 9, 11],
    }
)

save(
    ggplot(wind_df, aes(x="direction", y="speed"))
    + geom_col(fill="#2980b9", alpha=0.8)
    + coord_polar()
    + labs(title="coord_polar"),
    "coords",
    "polar",
)

# ── coord_equal ──────────────────────────────────────────────────────────────

circle_t = np.linspace(0, 2 * np.pi, 100)
circle_df = pl.DataFrame({"x": np.cos(circle_t).tolist(), "y": np.sin(circle_t).tolist()})

save(
    ggplot(circle_df, aes(x="x", y="y"))
    + geom_path(linewidth=1, color="#e74c3c")
    + coord_equal()
    + labs(title="coord_equal"),
    "coords",
    "equal",
)

# ── coord_trans ──────────────────────────────────────────────────────────────

save(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_point(alpha=0.05, size=3)
    + coord_trans(x="sqrt", y="log10")
    + labs(title="coord_trans (sqrt x, log10 y)", x="Carat", y="Price"),
    "coords",
    "trans",
)


# ═══════════════════════════════════════════════════════════════════════════════
# FACETS
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating facet images...")

# ── facet_wrap ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("drv")
    + labs(title="facet_wrap", x="Displacement (L)", y="Highway MPG"),
    "facets",
    "wrap",
    width=8,
    height=4,
)

# ── facet_grid ───────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_grid(rows="drv", cols="cyl")
    + labs(title="facet_grid (drv ~ cyl)", x="Displacement (L)", y="Highway MPG"),
    "facets",
    "grid",
    width=9,
    height=6,
)

# ── labeller_both ────────────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("drv", labeller=labeller_both("drv"))
    + labs(title="labeller_both", x="Displacement (L)", y="Highway MPG"),
    "facets",
    "labeller_both",
    width=8,
    height=4,
)


# ═══════════════════════════════════════════════════════════════════════════════
# THEMES
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating theme images...")

# Base plot used for all themes
theme_base = (
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + labs(x="Displacement (L)", y="Highway MPG")
)

themes = {
    "default": theme_default(),
    "grey": theme_grey(),
    "bw": theme_bw(),
    "minimal": theme_minimal(),
    "classic": theme_classic(),
    "dark": theme_dark(),
    "light": theme_light(),
    "linedraw": theme_linedraw(),
    "void": theme_void(),
    "tufte": theme_tufte(),
    "economist": theme_economist(),
    "538": theme_538(),
    "seaborn": theme_seaborn(),
}

for name, t in themes.items():
    save(
        theme_base + t + labs(title=f"theme_{name}"),
        "themes",
        name,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GALLERY
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating gallery images...")

# ── Gallery: Scatter with smooth and facets ──────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(alpha=0.6)
    + geom_smooth(method="ols")
    + facet_wrap("drv")
    + labs(
        title="Displacement vs. MPG by drive train",
        x="Displacement (L)",
        y="Highway MPG",
    ),
    "gallery",
    "scatter_smooth_facet",
    width=9,
    height=4,
)

# ── Gallery: Layered distributions ───────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", fill="drv"))
    + geom_histogram(bins=20, alpha=0.5, position=position_stack())
    + labs(
        title="Stacked highway MPG by drive train",
        x="Highway MPG",
        y="Count",
    ),
    "gallery",
    "stacked_histogram",
)

# ── Gallery: Box + violin ────────────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_violin(fill="#dfe6e9", alpha=0.7)
    + geom_boxplot(width=0.2, fill="#74b9ff", alpha=0.8)
    + labs(
        title="Highway MPG by vehicle class",
        subtitle="Violin + boxplot overlay",
        x="Vehicle class",
        y="Highway MPG",
    ),
    "gallery",
    "violin_boxplot",
    width=8,
    height=5,
)

# ── Gallery: Heatmap with tiles ──────────────────────────────────────────────

# Correlation-like heatmap
vars_list = ["displ", "cyl", "cty", "hwy"]
heat_rows = []
for v1 in vars_list:
    for v2 in vars_list:
        heat_rows.append({"x": v1, "y": v2, "r": round(rng.uniform(-1, 1), 2)})
heat_df = pl.DataFrame(heat_rows)

save(
    ggplot(heat_df, aes(x="x", y="y", fill="r"))
    + geom_tile()
    + scale_fill_gradient2(low="#2166ac", mid="#f7f7f7", high="#b2182b", midpoint=0)
    + labs(title="Heatmap with geom_tile + scale_fill_gradient2"),
    "gallery",
    "heatmap",
)

# ── Gallery: Ridge plot with viridis ─────────────────────────────────────────

save(
    ggplot(mpg, aes(x="hwy", y="class"))
    + geom_density_ridges(alpha=0.8)
    + labs(
        title="Highway MPG density ridges",
        x="Highway MPG",
    ),
    "gallery",
    "ridge_plot",
    width=8,
    height=5,
)

# ── Gallery: Annotated scatter ───────────────────────────────────────────────

save(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(mapping=aes(color="class"), alpha=0.6)
    + geom_smooth(method="ols", color="#2c3e50")
    + stat_cor()
    + geom_hline(yintercept=25, linetype="dashed", color="#e74c3c", alpha=0.6)
    + labs(
        title="Annotated scatter: smooth + correlation + reference line",
        x="Displacement (L)",
        y="Highway MPG",
    ),
    "gallery",
    "annotated_scatter",
    width=8,
    height=5,
)

# ═══════════════════════════════════════════════════════════════════════════════
# RECIPES
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating recipe images...")

# ── plot_waterfall ─────────────────────────────────────────────────────────

waterfall_df = pl.DataFrame(
    {
        "item": ["Revenue", "COGS", "Gross Profit", "OpEx", "Tax", "Net Income"],
        "amount": [500, -200, 300, -150, -45, 105],
    }
)

save(
    plot_waterfall(waterfall_df, x="item", y="amount", title="Waterfall chart"),
    "recipes",
    "waterfall",
)

# ── plot_dumbbell ──────────────────────────────────────────────────────────

dumbbell_df = pl.DataFrame(
    {
        "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
        "jan": [33, 58, 26, 52, 55],
        "jul": [77, 75, 73, 84, 95],
    }
)

save(
    plot_dumbbell(
        dumbbell_df,
        y="city",
        x_start="jan",
        x_end="jul",
        title="Average temperature: January vs. July",
    ),
    "recipes",
    "dumbbell",
)

# ── plot_lollipop ──────────────────────────────────────────────────────────

lollipop_df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "value": [23, 17, 35, 29, 12],
    }
)

save(
    plot_lollipop(lollipop_df, x="x", y="value", title="Lollipop chart"),
    "recipes",
    "lollipop",
)

# ── plot_slope ─────────────────────────────────────────────────────────────

slope_df = pl.DataFrame(
    {
        "year": ["2020", "2020", "2020", "2025", "2025", "2025"],
        "region": ["East", "West", "South", "East", "West", "South"],
        "sales": [100, 80, 60, 120, 110, 90],
    }
)

save(
    plot_slope(slope_df, x="year", y="sales", group="region", title="Regional sales trend"),
    "recipes",
    "slope",
)

# ── plot_forest ────────────────────────────────────────────────────────────

forest_df = pl.DataFrame(
    {
        "study": ["Study A", "Study B", "Study C", "Study D", "Study E"],
        "estimate": [0.5, 0.8, 0.3, 0.6, 0.1],
        "ci_low": [0.2, 0.5, -0.1, 0.3, -0.2],
        "ci_high": [0.8, 1.1, 0.7, 0.9, 0.4],
    }
)

save(
    plot_forest(
        forest_df,
        y="study",
        x="estimate",
        xmin="ci_low",
        xmax="ci_high",
        title="Forest plot",
    ),
    "recipes",
    "forest",
)

# ── plot_waffle ────────────────────────────────────────────────────────────

waffle_df = pl.DataFrame(
    {
        "fuel": ["Regular", "Premium", "Diesel", "Electric"],
        "count": [45, 25, 15, 15],
    }
)

save(
    plot_waffle(waffle_df, category="fuel", value="count", title="Fuel type breakdown"),
    "recipes",
    "waffle",
)

print("\nDone! All images saved to docs/images/generated/")
