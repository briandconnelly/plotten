"""Grouped bar chart with dodged positions and custom fill colors."""

import polars as pl

from plotten import (
    aes,
    geom_col,
    ggplot,
    guide_legend,
    guides,
    labs,
    position_dodge,
    scale_fill_manual,
    theme,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "quarter": ["Q1", "Q1", "Q2", "Q2", "Q3", "Q3", "Q4", "Q4"],
        "revenue": [120, 95, 145, 110, 160, 130, 180, 155],
        "region": ["North", "South", "North", "South", "North", "South", "North", "South"],
    }
)

plot = (
    ggplot(df, aes(x="quarter", y="revenue", fill="region"))
    + geom_col(position=position_dodge())
    + scale_fill_manual(values={"North": "#2196F3", "South": "#FF9800"})
    + labs(
        title="Quarterly Revenue by Region",
        caption="Source: internal sales data, FY2025",
        x="Quarter",
        y="Revenue ($K)",
        fill="Region",
    )
    + theme_minimal()
    + theme(title_size=16)
    + guides(fill=guide_legend(ncol=2))
)

plot.save("examples/output/grouped_bar.png", dpi=200)
