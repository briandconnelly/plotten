"""Confidence ellipses for grouped bivariate data."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_brewer,
    stat_ellipse,
    theme_minimal,
)

rng = np.random.default_rng(42)
n = 80
df = pd.DataFrame(
    {
        "x": np.concatenate([rng.normal(0, 1, n), rng.normal(3, 1.5, n), rng.normal(6, 0.8, n)]),
        "y": np.concatenate([rng.normal(0, 1, n), rng.normal(2, 1, n), rng.normal(0, 1.2, n)]),
        "species": ["Setosa"] * n + ["Versicolor"] * n + ["Virginica"] * n,
    }
)

p = (
    ggplot(df, aes(x="x", y="y", color="species"))
    + geom_point(alpha=0.5)
    + stat_ellipse(level=0.95)
    + scale_color_brewer(palette="Set1")
    + labs(
        title="95% Confidence Ellipses",
        subtitle="Bivariate normal confidence regions by group",
        x="Principal Component 1",
        y="Principal Component 2",
    )
    + theme_minimal()
)

p.save("examples/output/confidence_ellipse.png", width=8, height=6)
