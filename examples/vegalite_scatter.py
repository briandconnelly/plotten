"""Interactive scatter plot exported as Vega-Lite HTML."""

import json

import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_brewer,
    theme_minimal,
    to_html,
    to_vegalite,
)

df = pl.DataFrame(
    {
        "engine_size": [1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 5.7, 6.2, 2.0, 2.4, 3.6, 4.6, 1.8],
        "horsepower": [130, 155, 182, 220, 268, 300, 390, 420, 460, 148, 175, 260, 345, 140],
        "category": [
            "Compact",
            "Compact",
            "Sedan",
            "Sedan",
            "SUV",
            "SUV",
            "Truck",
            "Truck",
            "Truck",
            "Compact",
            "Sedan",
            "SUV",
            "Truck",
            "Compact",
        ],
    }
)

plot = (
    ggplot(df, aes(x="engine_size", y="horsepower", color="category"))
    + geom_point(size=80, alpha=0.8)
    + scale_color_brewer(palette="Set2")
    + theme_minimal()
    + labs(
        title="Engine Size vs Horsepower",
        subtitle="Interactive Vega-Lite export — hover for tooltips",
        x="Engine Displacement (L)",
        y="Horsepower",
        color="Category",
    )
)

# Export as HTML file
html = to_html(plot)
with open("examples/output/vegalite_scatter.html", "w") as f:
    f.write(html)

# Also dump the raw spec for inspection
spec = to_vegalite(plot)
print(json.dumps(spec, indent=2))
