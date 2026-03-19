"""Custom labeller functions for facet strip labels."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    facet_wrap,
    geom_point,
    ggplot,
    labeller_both,
    labs,
    theme_minimal,
)

rng = np.random.default_rng(42)
df = pd.DataFrame(
    {
        "weight": np.concatenate(
            [rng.normal(50, 10, 40), rng.normal(70, 15, 40), rng.normal(90, 12, 40)]
        ),
        "height": np.concatenate(
            [rng.normal(160, 8, 40), rng.normal(170, 10, 40), rng.normal(180, 7, 40)]
        ),
        "diet": ["Low carb"] * 40 + ["Mediterranean"] * 40 + ["Standard"] * 40,
    }
)

p = (
    ggplot(df, aes(x="weight", y="height"))
    + geom_point(alpha=0.5)
    + facet_wrap("diet", labeller=labeller_both("Diet"))
    + labs(
        title="Custom Facet Labels",
        subtitle="labeller_both() adds variable name to strip text",
        x="Weight (kg)",
        y="Height (cm)",
    )
    + theme_minimal()
)

p.save("examples/output/custom_labellers.png", width=10, height=4)
