"""New label formatters: bytes, ordinals, and text wrapping."""

import polars as pl

from plotten import (
    aes,
    breaks_width,
    geom_col,
    ggplot,
    label_bytes,
    label_ordinal,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- label_bytes: auto-scaling byte sizes ---

df_bytes = pl.DataFrame(
    {
        "service": ["API", "Cache", "DB", "Logs", "Static"],
        "usage": [3_500_000_000, 512_000_000, 8_200_000_000, 1_100_000_000, 250_000_000],
    }
)

p_bytes = (
    ggplot(df_bytes, aes(x="service", y="usage"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_bytes())
    + labs(title="label_bytes()", subtitle="Auto-scaled byte units", x="Service", y="Storage")
    + theme_minimal()
)

# --- label_bytes with fixed unit ---

df_transfer = pl.DataFrame(
    {
        "endpoint": ["/api/data", "/api/users", "/api/search", "/healthz"],
        "bytes_out": [45_000_000, 12_000_000, 88_000_000, 500_000],
    }
)

p_bytes_fixed = (
    ggplot(df_transfer, aes(x="endpoint", y="bytes_out"))
    + geom_col(fill="#31A354", alpha=0.8)
    + scale_y_continuous(labels=label_bytes(units="MB"))
    + labs(title='label_bytes(units="MB")', subtitle="Fixed MB unit", x="Endpoint", y="Transfer")
    + theme_minimal()
)

# --- label_ordinal: English ordinal suffixes ---

df_race = pl.DataFrame(
    {
        "position": [1, 2, 3, 4, 5, 6, 7, 8],
        "points": [25, 18, 15, 12, 10, 8, 6, 4],
    }
)

p_ordinal = (
    ggplot(df_race, aes(x="position", y="points"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_x_continuous(breaks=breaks_width(1), labels=label_ordinal())
    + labs(title="label_ordinal()", subtitle="1st, 2nd, 3rd, ...", x="Finish", y="Points")
    + theme_minimal()
)

# --- Combining formatters: ordinal x + bytes y ---

df_servers = pl.DataFrame(
    {
        "rank": [1, 2, 3, 4, 5],
        "memory": [68_719_476_736, 34_359_738_368, 17_179_869_184, 8_589_934_592, 4_294_967_296],
    }
)

p_combo = (
    ggplot(df_servers, aes(x="rank", y="memory"))
    + geom_col(fill="#756BB1", alpha=0.8)
    + scale_x_continuous(breaks=breaks_width(1), labels=label_ordinal())
    + scale_y_continuous(labels=label_bytes())
    + labs(
        title="Combined Formatters",
        subtitle="Ordinal ranks + byte sizes",
        x="Server Rank",
        y="RAM",
    )
    + theme_minimal()
)

grid = plot_grid(p_bytes, p_bytes_fixed, p_ordinal, p_combo, ncol=2)
grid.save("examples/output/label_formats.png", dpi=200)
