"""Contour and 2D density plots for scientific visualization."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_contour,
    geom_point,
    geom_raster,
    ggplot,
    labs,
    stat_density_2d,
    stat_density_2d_filled,
    theme_minimal,
)

# 2D density estimation from bivariate normal scatter
rng = np.random.default_rng(42)
n = 500
x1 = rng.normal(0, 1, n)
y1 = rng.normal(0, 1, n)
x2 = rng.normal(3, 0.7, n // 2)
y2 = rng.normal(2, 0.7, n // 2)
scatter = pl.DataFrame(
    {
        "x": np.concatenate([x1, x2]).tolist(),
        "y": np.concatenate([y1, y2]).tolist(),
    }
)

density_lines = (
    ggplot(scatter, aes(x="x", y="y"))
    + geom_point(alpha=0.15, size=1)
    + stat_density_2d(color="navy", linewidth=0.8)
    + labs(title="2D Density Contours", x="x", y="y")
    + theme_minimal()
)

density_filled = (
    ggplot(scatter, aes(x="x", y="y"))
    + stat_density_2d_filled(cmap="magma", alpha=0.8)
    + geom_point(alpha=0.2, size=0.5, color="white")
    + labs(title="Filled 2D Density", x="x", y="y")
    + theme_minimal()
)

# Gridded contour from an analytic function — use a Gaussian mixture
# that decays to zero well within the grid boundaries
x = np.linspace(-4, 4, 80)
y = np.linspace(-4, 4, 80)
xx, yy = np.meshgrid(x, y)
zz = np.exp(-((xx - 1) ** 2 + (yy - 1) ** 2)) + 0.7 * np.exp(-((xx + 1) ** 2 + (yy + 1) ** 2))

grid_df = pl.DataFrame(
    {
        "x": xx.ravel().tolist(),
        "y": yy.ravel().tolist(),
        "z": zz.ravel().tolist(),
    }
)

contour_lines = (
    ggplot(grid_df, aes(x="x", y="y", z="z"))
    + geom_contour(bins=12)
    + labs(title="Contour Lines", subtitle="Gaussian mixture", x="x", y="y")
    + theme_minimal()
)

raster = (
    ggplot(grid_df, aes(x="x", y="y", z="z"))
    + geom_raster(cmap="coolwarm")
    + labs(title="Raster Heatmap", subtitle="Same function as pcolormesh", x="x", y="y")
    + theme_minimal()
)

grid = (density_lines | density_filled) / (contour_lines | raster)
grid.save("examples/output/contour_density2d.png", dpi=200, width=14, height=12)
