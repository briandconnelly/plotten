"""Binned color scale demonstrating scale_color_steps on a scatter plot."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_steps,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

n = 150
latitude = rng.uniform(-60, 70, n)
longitude = rng.uniform(-180, 180, n)
temperature = 30 - 0.5 * np.abs(latitude) + rng.normal(0, 4, n)

df = pl.DataFrame(
    {
        "longitude": longitude.tolist(),
        "latitude": latitude.tolist(),
        "temperature": temperature.tolist(),
    }
)

plot = (
    ggplot(df, aes(x="longitude", y="latitude", color="temperature"))
    + geom_point(size=50, alpha=0.8)
    + scale_color_steps(n=6, cmap="RdYlBu_r")
    + labs(
        title="Global Temperature Observations",
        subtitle="Binned color scale groups continuous values into discrete steps",
        x="Longitude",
        y="Latitude",
        color="Temp (C)",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/binned_scales.png", dpi=200)
