"""Fixed-width breaks and logarithmic breaks."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_width,
    geom_col,
    geom_point,
    ggplot,
    label_comma,
    labs,
    scale_x_continuous,
    scale_x_log10,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- Fixed-width breaks ---

df_monthly = pl.DataFrame(
    {
        "month": list(range(1, 13)),
        "sales": [12, 19, 14, 25, 30, 28, 35, 33, 27, 22, 18, 15],
    }
)

width_quarterly = (
    ggplot(df_monthly, aes(x="month", y="sales"))
    + geom_col(fill="#4292C6", alpha=0.8)
    + scale_x_continuous(breaks=breaks_width(3, offset=1))
    + labs(title="breaks_width(3, offset=1)", subtitle="Quarterly ticks", x="Month", y="Sales")
    + theme_minimal()
)

width_bimonthly = (
    ggplot(df_monthly, aes(x="month", y="sales"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_x_continuous(breaks=breaks_width(2))
    + labs(title="breaks_width(2)", subtitle="Every two months", x="Month", y="Sales")
    + theme_minimal()
)

# --- Log breaks with 1-2-5 subdivision ---

rng = np.random.default_rng(7)
df_log = pl.DataFrame(
    {
        "size": (10 ** rng.uniform(0, 4, 60)).tolist(),
        "speed": (10 ** rng.uniform(0, 3, 60)).tolist(),
    }
)

# breaks_log gives 1-2-5 subdivisions per decade on a log scale
log_breaks = (
    ggplot(df_log, aes(x="size", y="speed"))
    + geom_point(alpha=0.5, color="#756BB1")
    + scale_x_log10()
    + scale_y_continuous(labels=label_comma())
    + labs(title="scale_x_log10()", subtitle="Log-scaled x-axis", x="Size", y="Speed")
    + theme_minimal()
)

# label_log formats powers of 10 with superscript notation
log_labels = (
    ggplot(df_log, aes(x="size", y="speed"))
    + geom_point(alpha=0.5, color="#E6550D")
    + scale_x_log10()
    + scale_y_continuous(labels=label_comma())
    + labs(
        title="label_log(10)",
        subtitle="Superscript notation: 10\u2070, 10\u00b9, 10\u00b2, ...",
        x="Size",
        y="Speed",
    )
    + theme_minimal()
)

grid = plot_grid(width_quarterly, width_bimonthly, log_breaks, log_labels, ncol=2)
grid.save("examples/output/breaks_width_log.png", dpi=200)
