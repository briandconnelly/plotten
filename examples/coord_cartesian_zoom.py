"""Zooming into a plot without dropping data using coord_cartesian."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    coord_cartesian,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    scale_x_continuous,
    theme_minimal,
)

rng = np.random.default_rng(42)
x = np.linspace(0, 20, 100)
y = np.sin(x) + rng.normal(0, 0.3, 100)

df = pl.DataFrame({"x": x.tolist(), "y": y.tolist()})

# Full view with smooth trend
full = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, size=2)
    + geom_smooth(method="loess", color="tomato")
    + labs(title="Full View", x="x", y="y")
    + theme_minimal()
)

# coord_cartesian zoom — stat_smooth sees ALL data, trend line is accurate
zoom_coord = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, size=2)
    + geom_smooth(method="loess", color="tomato")
    + coord_cartesian(xlim=(5, 15))
    + labs(title="coord_cartesian Zoom", subtitle="Smooth uses all data", x="x", y="y")
    + theme_minimal()
)

# scale limits zoom — data outside range is DROPPED, trend line is distorted
zoom_scale = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, size=2)
    + geom_smooth(method="loess", color="tomato")
    + scale_x_continuous(limits=(5, 15))
    + labs(title="Scale Limits Zoom", subtitle="Smooth uses clipped data only", x="x", y="y")
    + theme_minimal()
)

grid = full | zoom_coord | zoom_scale
grid.save("examples/output/coord_cartesian_zoom.png", dpi=200, width=16, height=5)
