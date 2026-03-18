"""Computed aesthetics with after_stat for density histograms and proportions."""

import random

import polars as pl

from plotten import (
    Aes,
    after_stat,
    geom_bar,
    geom_histogram,
    ggplot,
    labs,
    plot_annotation,
)

random.seed(42)
values = [random.gauss(0, 1) for _ in range(500)]
hist_df = pl.DataFrame({"x": values})

density_plot = (
    ggplot(hist_df, Aes(x="x", y=after_stat("density")))
    + geom_histogram(bins=25)
    + labs(
        title="Density Histogram",
        subtitle="Using after_stat('density') for normalized y-axis",
        x="Value",
        y="Density",
    )
)

density_plot.save("examples/output/density_histogram.png", dpi=200)

# Proportion bar chart using after_stat("prop")
survey_df = pl.DataFrame(
    {
        "response": (
            ["Strongly Agree"] * 45
            + ["Agree"] * 30
            + ["Neutral"] * 15
            + ["Disagree"] * 7
            + ["Strongly Disagree"] * 3
        ),
    }
)

prop_plot = (
    ggplot(survey_df, Aes(x="response", y=after_stat("prop")))
    + geom_bar()
    + labs(
        title="Survey Responses",
        subtitle="Using after_stat('prop') for proportions",
        x="Response",
        y="Proportion",
    )
)

prop_plot.save("examples/output/proportion_bar.png", dpi=200)

# Side-by-side comparison
grid = density_plot | prop_plot
grid = grid + plot_annotation(
    title="Computed Aesthetics Demo",
    tag_levels="A",
)
grid.save("examples/output/computed_aesthetics_grid.png", dpi=200)
