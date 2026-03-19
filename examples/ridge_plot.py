"""Ridge plot — stacked density distributions by group."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_density_ridges,
    ggplot,
    labs,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)
months = ["January", "February", "March", "April", "May", "June"]
data = []
for i, month in enumerate(months):
    temps = rng.normal(loc=5 + i * 3, scale=3 + i * 0.3, size=200)
    data.extend({"month": month, "temperature": t} for t in temps)

df = pd.DataFrame(data)

p = (
    ggplot(df, aes(x="temperature", y="month"))
    + geom_density_ridges(alpha=0.7)
    + labs(
        title="Temperature Distributions by Month",
        subtitle="Ridge plot showing seasonal warming trend",
        x="Temperature (\u00b0C)",
    )
    + theme_minimal()
    + theme(axis_text_y_size=11)
)

p.save("examples/output/ridge_plot.png", width=9, height=6)
