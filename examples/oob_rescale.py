"""Out-of-bounds handling and rescaling utilities."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_pretty,
    censor,
    geom_col,
    geom_point,
    ggplot,
    labs,
    rescale,
    scale_y_continuous,
    squish,
    theme,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- rescale: normalize values to a target range ---

raw = [10, 30, 50, 70, 90]
normalized = rescale(raw, to=(0, 1))

df_rescale = pl.DataFrame(
    {
        "item": ["A", "B", "C", "D", "E"],
        "raw": raw,
        "normalized": normalized,
    }
)

p_raw = (
    ggplot(df_rescale, aes(x="item", y="raw"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + labs(title="Raw Values", subtitle="Range: 10-90", y="Value")
    + theme_minimal()
)

p_norm = (
    ggplot(df_rescale, aes(x="item", y="normalized"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_y_continuous(breaks=breaks_pretty(5))
    + labs(title="rescale(to=(0, 1))", subtitle="Normalized to 0-1", y="Value")
    + theme_minimal()
)

# --- squish vs censor: two strategies for out-of-bounds data ---

rng = np.random.default_rng(42)
values = rng.normal(50, 25, 30).tolist()
squished = squish(values, range=(20, 80))
censored = censor(values, range=(20, 80))

df_oob = pl.DataFrame(
    {
        "index": list(range(len(values))),
        "original": values,
        "squished": squished,
    }
)

p_squish = (
    ggplot(df_oob, aes(x="index", y="squished"))
    + geom_point(color="#756BB1", size=40, alpha=0.7)
    + scale_y_continuous(breaks=breaks_pretty(5))
    + labs(
        title="squish(range=(20, 80))",
        subtitle="Out-of-bounds values clamped to limits",
        x="Index",
        y="Value",
    )
    + theme_minimal()
    + theme(title_size=11)
)

# For censor, filter out None values
censored_clean = [(i, v) for i, v in enumerate(censored) if v is not None]
df_censor = pl.DataFrame(
    {
        "index": [c[0] for c in censored_clean],
        "censored": [c[1] for c in censored_clean],
    }
)

p_censor = (
    ggplot(df_censor, aes(x="index", y="censored"))
    + geom_point(color="#E6550D", size=40, alpha=0.7)
    + scale_y_continuous(breaks=breaks_pretty(5))
    + labs(
        title="censor(range=(20, 80))",
        subtitle="Out-of-bounds values removed (None)",
        x="Index",
        y="Value",
    )
    + theme_minimal()
    + theme(title_size=11)
)

grid = plot_grid(p_raw, p_norm, p_squish, p_censor, ncol=2)
grid.save("examples/output/oob_rescale.png", dpi=200)
