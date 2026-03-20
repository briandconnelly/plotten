"""Binning continuous variables with cut_width(), cut_interval(), and cut_number()."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    cut_interval,
    cut_number,
    cut_width,
    geom_bar,
    ggplot,
    labs,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)
income = np.abs(rng.normal(50, 20, 200)).tolist()

df_width = pl.DataFrame({"bin": cut_width(income, 15)})
df_interval = pl.DataFrame({"bin": cut_interval(income, 5)})
df_number = pl.DataFrame({"bin": cut_number(income, 5)})

p1 = (
    ggplot(df_width, aes(x="bin"))
    + geom_bar(fill="steelblue", alpha=0.7)
    + labs(title="cut_width(x, 15)", subtitle="Fixed-width bins of 15 units", x="")
    + theme_minimal()
    + theme(axis_text_x_rotation=50, axis_text_x_size=8)
)

p2 = (
    ggplot(df_interval, aes(x="bin"))
    + geom_bar(fill="coral", alpha=0.7)
    + labs(title="cut_interval(x, 5)", subtitle="5 bins of equal range", x="")
    + theme_minimal()
    + theme(axis_text_x_rotation=50, axis_text_x_size=8)
)

p3 = (
    ggplot(df_number, aes(x="bin"))
    + geom_bar(fill="seagreen", alpha=0.7)
    + labs(title="cut_number(x, 5)", subtitle="5 bins with ~equal counts", x="")
    + theme_minimal()
    + theme(axis_text_x_rotation=50, axis_text_x_size=8)
)

grid = p1 | p2 | p3
grid.save("examples/output/cut_functions.png", dpi=200, width=14, height=5)
