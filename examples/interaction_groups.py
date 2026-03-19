"""Scatter plot colored by interaction of two grouping variables."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    interaction,
    labs,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

species_list = ["Adelie", "Chinstrap", "Gentoo"]
sex_list = ["Female", "Male"]

records: dict[str, list] = {"species": [], "sex": [], "bill_length": [], "bill_depth": []}

for species in species_list:
    base_length = {"Adelie": 38, "Chinstrap": 49, "Gentoo": 47}[species]
    base_depth = {"Adelie": 18, "Chinstrap": 18, "Gentoo": 15}[species]
    for sex in sex_list:
        n = 30
        offset = 2.0 if sex == "Male" else -1.5
        records["species"].extend([species] * n)
        records["sex"].extend([sex] * n)
        records["bill_length"].extend(rng.normal(base_length + offset, 2.0, n).tolist())
        records["bill_depth"].extend(rng.normal(base_depth + offset * 0.3, 1.0, n).tolist())

df = pl.DataFrame(records)

plot = (
    ggplot(df, aes(x="bill_length", y="bill_depth", color=interaction("species", "sex")))
    + geom_point(size=35, alpha=0.7)
    + labs(
        title="Bill Dimensions by Species and Sex",
        subtitle="Color encodes interaction(species, sex) — six distinct groups",
        x="Bill Length (mm)",
        y="Bill Depth (mm)",
        color="Species.Sex",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/interaction_groups.png", dpi=200)
