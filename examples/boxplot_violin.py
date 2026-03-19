"""Side-by-side boxplot and violin plot showing distributions."""

import numpy as np
import polars as pl

from plotten import aes, geom_boxplot, ggplot, labs, theme_minimal

rng = np.random.default_rng(42)

species = []
values = []
for name, mu, sigma in [("Setosa", 5.0, 0.35), ("Versicolor", 5.9, 0.5), ("Virginica", 6.6, 0.6)]:
    n = 50
    species.extend([name] * n)
    values.extend(rng.normal(mu, sigma, n).tolist())

df = pl.DataFrame({"species": species, "sepal_length": values})

plot = (
    ggplot(df, aes(x="species", y="sepal_length"))
    + geom_boxplot(fill="#7E57C2", alpha=0.6)
    + labs(
        title="Sepal Length by Species",
        x="Species",
        y="Sepal Length (cm)",
    )
    + theme_minimal()
)

plot.save("examples/output/boxplot.png", dpi=200)
