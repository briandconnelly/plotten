"""Grouped bar chart with dodged positions, exported as Vega-Lite HTML."""

import polars as pl

from plotten import (
    aes,
    geom_col,
    ggplot,
    labs,
    position_dodge,
    scale_fill_manual,
    theme_minimal,
    to_html,
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
    + theme_minimal()
    + labs(
        title="Quarterly Revenue by Region",
        subtitle="Dodged bar chart — interactive Vega-Lite",
        x="Quarter",
        y="Revenue ($K)",
        fill="Region",
    )
)

html = to_html(plot)
with open("examples/output/vegalite_bar_dodged.html", "w") as f:
    f.write(html)

print("Wrote examples/output/vegalite_bar_dodged.html")
