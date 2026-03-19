"""Legend positioned inside the plot area."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_brewer,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)
df = pd.DataFrame(
    {
        "engine_size": np.concatenate(
            [rng.normal(2.0, 0.5, 50), rng.normal(3.5, 0.8, 50), rng.normal(5.0, 0.6, 50)]
        ),
        "mpg": np.concatenate(
            [rng.normal(30, 3, 50), rng.normal(22, 4, 50), rng.normal(15, 2, 50)]
        ),
        "type": ["Compact"] * 50 + ["Sedan"] * 50 + ["SUV"] * 50,
    }
)

p = (
    ggplot(df, aes(x="engine_size", y="mpg", color="type"))
    + geom_point(alpha=0.6)
    + scale_color_brewer(palette="Dark2")
    + labs(
        title="Legend Inside Plot",
        subtitle="Positioned at (0.8, 0.85) in figure coordinates",
        x="Engine Size (L)",
        y="Miles per Gallon",
    )
    + theme_minimal()
    + theme(legend_position=(0.8, 0.85))
)

p.save("examples/output/legend_inside.png", width=8, height=6)
