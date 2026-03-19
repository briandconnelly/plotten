"""Embed a zoomed-in inset plot within a main scatter plot."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    ggplot,
    inset_element,
    labs,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)
n = 200
df = pd.DataFrame(
    {
        "x": np.concatenate([rng.normal(5, 2, n), rng.normal(15, 1, 30)]),
        "y": np.concatenate([rng.normal(5, 2, n), rng.normal(15, 1, 30)]),
    }
)

main = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + labs(title="Main View with Inset", x="X", y="Y")
    + theme_minimal()
)

# Zoomed inset on the cluster
cluster = df[(df["x"] > 12) & (df["y"] > 12)]
inset = (
    ggplot(cluster, aes(x="x", y="y"))
    + geom_point(color="red", alpha=0.7)
    + theme_minimal()
    + theme(title_size=9, label_size=8, tick_size=7)
)

p = main + inset_element(inset, left=0.15, bottom=0.55, width=0.35, height=0.35)
p.save("examples/output/inset_plot.png", width=8, height=6)
