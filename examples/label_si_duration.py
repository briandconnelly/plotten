"""SI prefixes and duration formatting for numeric axes."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_pretty,
    geom_col,
    geom_point,
    ggplot,
    label_duration,
    label_si,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- label_si: SI metric prefixes (k, M, G, T) ---

df_traffic = pl.DataFrame(
    {
        "page": ["Home", "Docs", "Blog", "API", "Pricing"],
        "views": [2_800_000, 1_200_000, 950_000, 3_500_000, 420_000],
    }
)

p_si = (
    ggplot(df_traffic, aes(x="page", y="views"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_si())
    + labs(title="label_si()", subtitle="2.8M, 1.2M, 950k, ...", x="Page", y="Views")
    + theme_minimal()
)

# SI with higher accuracy
p_si2 = (
    ggplot(df_traffic, aes(x="page", y="views"))
    + geom_col(fill="#31A354", alpha=0.8)
    + scale_y_continuous(labels=label_si(accuracy=2))
    + labs(
        title="label_si(accuracy=2)",
        subtitle="Two decimal places",
        x="Page",
        y="Views",
    )
    + theme_minimal()
)

# --- label_duration: human-readable time formatting ---

df_latency = pl.DataFrame(
    {
        "endpoint": ["/api/data", "/api/users", "/api/search", "/healthz", "/api/export"],
        "p99_ms": [0.045, 0.12, 1.8, 0.008, 45.0],
    }
)

# Convert to seconds for display
df_latency_s = df_latency.with_columns((pl.col("p99_ms") * 1000).alias("p99_s"))

df_jobs = pl.DataFrame(
    {
        "job": ["ETL", "Backup", "Index", "Report", "Deploy"],
        "duration": [7200, 1800, 300, 90, 45],
    }
)

p_dur = (
    ggplot(df_jobs, aes(x="job", y="duration"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_y_continuous(labels=label_duration())
    + labs(
        title="label_duration()",
        subtitle="2h 0m, 30m 0s, 5m 0s, ...",
        x="Job",
        y="Duration",
    )
    + theme_minimal()
)

# Scatter with SI axes
rng = np.random.default_rng(42)
df_perf = pl.DataFrame(
    {
        "requests": (rng.uniform(100_000, 5_000_000, 40)).tolist(),
        "latency": (rng.uniform(10, 7200, 40)).tolist(),
    }
)

p_both = (
    ggplot(df_perf, aes(x="requests", y="latency"))
    + geom_point(alpha=0.6, color="#756BB1")
    + scale_x_continuous(labels=label_si(), breaks=breaks_pretty(5))
    + scale_y_continuous(labels=label_duration())
    + labs(
        title="SI + Duration Together",
        subtitle="Requests (SI) vs response time (duration)",
        x="Requests",
        y="Response Time",
    )
    + theme_minimal()
)

grid = plot_grid(p_si, p_si2, p_dur, p_both, ncol=2)
grid.save("examples/output/label_si_duration.png", dpi=200)
