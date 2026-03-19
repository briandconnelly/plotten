"""Custom break functions for axis ticks."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)

rng = np.random.default_rng(42)
df = pd.DataFrame(
    {
        "x": rng.exponential(50, 200),
        "y": rng.exponential(1000, 200),
    }
)

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + scale_x_continuous(breaks=lambda lim: np.arange(0, lim[1], 25).tolist())
    + scale_y_continuous(
        breaks=lambda lim: np.arange(0, lim[1], 500).tolist(),
        labels=lambda v: f"${v / 1000:.1f}k",
    )
    + labs(
        title="Callable Breaks & Labels",
        subtitle="Dynamic tick positions and formatted labels",
        x="Duration (seconds)",
        y="Revenue",
    )
    + theme_minimal()
)

p.save("examples/output/callable_breaks.png", width=8, height=5)
