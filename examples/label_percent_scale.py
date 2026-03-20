"""Improved label_percent with scale parameter."""

import polars as pl

from plotten import (
    aes,
    geom_col,
    ggplot,
    label_percent,
    labs,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# Data in 0-1 range (proportions)
df_prop = pl.DataFrame(
    {
        "browser": ["Chrome", "Safari", "Firefox", "Edge", "Other"],
        "share": [0.65, 0.19, 0.04, 0.05, 0.07],
    }
)

p_01 = (
    ggplot(df_prop, aes(x="browser", y="share"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_percent())
    + labs(
        title="label_percent()",
        subtitle="Data in 0-1 range (default scale=100)",
        x="Browser",
        y="Market Share",
    )
    + theme_minimal()
)

# Data already in 0-100 range (survey results, test scores)
df_pct = pl.DataFrame(
    {
        "subject": ["Math", "Science", "English", "History", "Art"],
        "pass_rate": [78, 85, 92, 71, 95],
    }
)

p_100 = (
    ggplot(df_pct, aes(x="subject", y="pass_rate"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_y_continuous(labels=label_percent(scale=1))
    + labs(
        title="label_percent(scale=1)",
        subtitle="Data already in 0-100 range",
        x="Subject",
        y="Pass Rate",
    )
    + theme_minimal()
)

# Without scale=1, the 0-100 data would show "7800.0%"
p_wrong = (
    ggplot(df_pct, aes(x="subject", y="pass_rate"))
    + geom_col(fill="#636363", alpha=0.8)
    + scale_y_continuous(labels=label_percent())
    + labs(
        title="label_percent() on 0-100 data",
        subtitle="Without scale=1: 7800%, 8500%, ...",
        x="Subject",
        y="Pass Rate",
    )
    + theme_minimal()
)

# Combining with accuracy
p_precise = (
    ggplot(df_prop, aes(x="browser", y="share"))
    + geom_col(fill="#31A354", alpha=0.8)
    + scale_y_continuous(labels=label_percent(accuracy=0))
    + labs(
        title="label_percent(accuracy=0)",
        subtitle="No decimal places",
        x="Browser",
        y="Market Share",
    )
    + theme_minimal()
)

grid = plot_grid(p_01, p_100, p_wrong, p_precise, ncol=2)
grid.save("examples/output/label_percent_scale.png", dpi=200)
