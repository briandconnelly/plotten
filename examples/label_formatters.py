"""Label formatters for scale customization."""

import polars as pl

from plotten import (
    aes,
    geom_col,
    ggplot,
    label_comma,
    label_dollar,
    labs,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

products = ["Widget", "Gadget", "Gizmo", "Doohickey", "Thingamajig"]

df = pl.DataFrame(
    {
        "product": products,
        "revenue": [125000, 98000, 215000, 67000, 182000],
    }
)

p1 = (
    ggplot(df, aes(x="product", y="revenue"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_dollar())
    + labs(title="Revenue (Dollar Format)", x="Product", y="Revenue")
    + theme_minimal()
)

p2 = (
    ggplot(df, aes(x="product", y="revenue"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_y_continuous(labels=label_comma())
    + labs(title="Revenue (Comma Format)", x="Product", y="Revenue")
    + theme_minimal()
)

grid = plot_grid(p1, p2)
grid.save("examples/output/label_formatters.png", dpi=200)
