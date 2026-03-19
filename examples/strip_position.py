"""Facet strip labels at the bottom of panels."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    facet_wrap,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    theme_bw,
)

rng = np.random.default_rng(42)
data = []
for region in ["North", "South", "East", "West"]:
    n = 50
    x = rng.uniform(0, 10, n)
    y = 2 * x + rng.normal(0, 3, n)
    data.extend({"x": xi, "y": yi, "region": region} for xi, yi in zip(x, y, strict=True))

df = pd.DataFrame(data)

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="ols")
    + facet_wrap("region", ncol=4, strip_position="bottom")
    + labs(
        title="Strip Labels at Bottom",
        x="Predictor",
        y="Response",
    )
    + theme_bw()
)

p.save("examples/output/strip_position.png", width=12, height=4)
