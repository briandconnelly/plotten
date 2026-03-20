"""Bubble chart with area-proportional sizing via scale_size_area()."""

import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_size_area,
    theme,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "country": ["US", "China", "India", "Germany", "Brazil", "Japan", "UK", "France"],
        "gdp_per_capita": [63, 12, 2, 46, 9, 40, 42, 39],
        "life_expectancy": [78, 77, 70, 81, 76, 84, 81, 83],
        "population_m": [331, 1412, 1408, 84, 214, 125, 67, 68],
    }
)

plot = (
    ggplot(df, aes(x="gdp_per_capita", y="life_expectancy", size="population_m"))
    + geom_point(alpha=0.5, color="steelblue")
    + scale_size_area(max_size=400)
    + labs(
        title="GDP vs Life Expectancy",
        subtitle="Bubble area proportional to population — China & India dominate",
        x="GDP per Capita (k USD)",
        y="Life Expectancy (years)",
    )
    + theme_minimal()
    + theme(title_size=15, legend_position="none")
)

plot.save("examples/output/scale_size_area.png", dpi=200)
