"""Binned position scales: discretizing continuous axes into bins."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_x_binned,
    theme_minimal,
)

rng = np.random.default_rng(99)
df = pl.DataFrame(
    {
        "age": rng.uniform(18, 80, 200).tolist(),
        "income": (rng.normal(50, 15, 200) + rng.uniform(18, 80, 200) * 0.5).tolist(),
    }
)

# Without binning: continuous scatter
continuous = (
    ggplot(df, aes(x="age", y="income"))
    + geom_point(alpha=0.4, size=2)
    + labs(title="Continuous X", subtitle="Raw scatter")
    + theme_minimal()
)

# With binned x: values snap to bin centers
binned = (
    ggplot(df, aes(x="age", y="income"))
    + geom_point(alpha=0.4, size=2)
    + scale_x_binned(n_bins=6)
    + labs(title="scale_x_binned(n_bins=6)", subtitle="Age snapped to 6 bin centers")
    + theme_minimal()
)

grid = continuous | binned
grid.save("examples/output/binned_position.png", dpi=200)
