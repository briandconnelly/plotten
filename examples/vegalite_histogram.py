"""Histogram exported as interactive Vega-Lite HTML."""

import numpy as np
import polars as pl

from plotten import aes, geom_histogram, ggplot, labs, theme_minimal, to_html

rng = np.random.default_rng(42)
values = np.concatenate([rng.normal(170, 8, 200), rng.normal(185, 10, 150)])

df = pl.DataFrame({"height": values.tolist()})

plot = (
    ggplot(df, aes(x="height"))
    + geom_histogram(bins=25, alpha=0.7, color="#3F51B5")
    + theme_minimal()
    + labs(
        title="Distribution of Heights",
        subtitle="Bimodal distribution — interactive histogram",
        x="Height (cm)",
        y="Count",
    )
)

html = to_html(plot)
with open("examples/output/vegalite_histogram.html", "w") as f:
    f.write(html)

print("Wrote examples/output/vegalite_histogram.html")
