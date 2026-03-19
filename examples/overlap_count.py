"""Count overlapping points — bubble size = frequency."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_count,
    ggplot,
    labs,
    theme_minimal,
)

rng = np.random.default_rng(42)
# Discrete grid with repeated observations
x = rng.choice([1, 2, 3, 4, 5], size=300)
y = rng.choice([1, 2, 3, 4, 5], size=300)
df = pd.DataFrame({"x": x, "y": y})

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_count(alpha=0.6, color="steelblue")
    + labs(
        title="Overlap Count",
        subtitle="Point size proportional to observation count",
        x="X",
        y="Y",
    )
    + theme_minimal()
)

p.save("examples/output/overlap_count.png", width=7, height=6)
