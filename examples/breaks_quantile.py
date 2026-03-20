"""Quantile-based breaks for skewed distributions."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_pretty,
    breaks_quantile,
    geom_point,
    ggplot,
    label_si,
    labs,
    scale_x_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# Heavily right-skewed data (income-like distribution)
rng = np.random.default_rng(42)
incomes = (rng.lognormal(mean=10.5, sigma=1.0, size=200)).tolist()

df = pl.DataFrame(
    {
        "income": incomes,
        "satisfaction": (rng.normal(60, 15, 200)).tolist(),
    }
)

# Even spacing: most data crammed into left side
p_even = (
    ggplot(df, aes(x="income", y="satisfaction"))
    + geom_point(alpha=0.4, color="#636363")
    + scale_x_continuous(breaks=breaks_pretty(6), labels=label_si())
    + labs(
        title="breaks_pretty(6)",
        subtitle="Even spacing wastes axis on empty tail",
        x="Income",
        y="Satisfaction",
    )
    + theme_minimal()
)

# Quantile spacing: ticks where the data actually is
p_quantile = (
    ggplot(df, aes(x="income", y="satisfaction"))
    + geom_point(alpha=0.4, color="#2171B5")
    + scale_x_continuous(breaks=breaks_quantile(incomes, n=6), labels=label_si())
    + labs(
        title="breaks_quantile(n=6)",
        subtitle="Ticks placed at data quantiles",
        x="Income",
        y="Satisfaction",
    )
    + theme_minimal()
)

# Another example: response times (exponential distribution)
latencies = (rng.exponential(scale=50, size=200)).tolist()
df_lat = pl.DataFrame(
    {
        "latency_ms": latencies,
        "throughput": (rng.uniform(100, 1000, 200)).tolist(),
    }
)

p_lat_even = (
    ggplot(df_lat, aes(x="latency_ms", y="throughput"))
    + geom_point(alpha=0.4, color="#636363")
    + scale_x_continuous(breaks=breaks_pretty(6))
    + labs(title="Even Breaks", subtitle="Long tail dominates", x="Latency (ms)", y="Throughput")
    + theme_minimal()
)

p_lat_quantile = (
    ggplot(df_lat, aes(x="latency_ms", y="throughput"))
    + geom_point(alpha=0.4, color="#E6550D")
    + scale_x_continuous(breaks=breaks_quantile(latencies, n=6))
    + labs(
        title="Quantile Breaks",
        subtitle="Equal data density between ticks",
        x="Latency (ms)",
        y="Throughput",
    )
    + theme_minimal()
)

grid = plot_grid(p_even, p_quantile, p_lat_even, p_lat_quantile, ncol=2)
grid.save("examples/output/breaks_quantile.png", dpi=200)
