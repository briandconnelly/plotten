"""Shared legend across multiple plots in a grid."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    plot_annotation,
    plot_grid,
    scale_color_brewer,
)

rng = np.random.default_rng(42)
df = pd.DataFrame(
    {
        "x": rng.normal(0, 1, 120),
        "y": rng.normal(0, 1, 120),
        "group": ["Alpha"] * 40 + ["Beta"] * 40 + ["Gamma"] * 40,
    }
)

p1 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point()
    + scale_color_brewer(palette="Set2")
    + labs(title="Scatter")
)

p2 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(alpha=0.3)
    + scale_color_brewer(palette="Set2")
    + labs(title="With transparency")
)

grid = plot_grid(p1, p2, ncol=2, guides="collect") + plot_annotation(
    title="Shared Legend Across Panels"
)
grid.save("examples/output/shared_legend.png", width=12, height=5)
