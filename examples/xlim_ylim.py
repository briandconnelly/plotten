"""Quick axis limits with xlim() and ylim() convenience functions."""

import numpy as np
import polars as pl

from plotten import aes, geom_point, ggplot, labs, theme_minimal, xlim, ylim

rng = np.random.default_rng(7)
df = pl.DataFrame(
    {
        "x": rng.normal(50, 15, 60).tolist(),
        "y": rng.normal(50, 15, 60).tolist(),
    }
)

# Default: axes fit to data
default = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.6)
    + labs(title="Default Limits", subtitle="Axes fit to the data range")
    + theme_minimal()
)

# xlim/ylim: quick way to fix axes to 0-100
fixed = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.6)
    + xlim(0, 100)
    + ylim(0, 100)
    + labs(title="xlim(0, 100) + ylim(0, 100)", subtitle="Axes fixed to a known range")
    + theme_minimal()
)

# Zoom in with xlim/ylim
zoomed = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.6)
    + xlim(30, 70)
    + ylim(30, 70)
    + labs(title="Zoomed In", subtitle="xlim(30, 70) + ylim(30, 70)")
    + theme_minimal()
)

grid = default | fixed | zoomed
grid.save("examples/output/xlim_ylim.png", dpi=200)
