"""Label repulsion — automatic collision avoidance for text labels."""

import polars as pl

from plotten import (
    aes,
    geom_label_repel,
    geom_point,
    geom_text_repel,
    ggplot,
    labs,
    theme_minimal,
)

# Scatter data with overlapping points
df = pl.DataFrame(
    {
        "x": [1.0, 1.2, 1.1, 3.0, 3.1, 5.0, 5.2, 5.1, 7.0, 7.1],
        "y": [2.0, 2.1, 1.9, 4.0, 4.2, 3.0, 3.1, 2.8, 5.0, 5.1],
        "name": [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
        ],
    }
)

# --- geom_text_repel: plain text labels pushed apart ---
plot1 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=30, color="#2c3e50")
    + geom_text_repel(label="name", color="#e74c3c", size=9)
    + theme_minimal()
    + labs(
        title="geom_text_repel — labels avoid overlap",
        x="X",
        y="Y",
    )
)
plot1.save("examples/output/text_repel.png", dpi=200)

# --- geom_label_repel: boxed labels with connectors ---
plot2 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=30, color="#2c3e50")
    + geom_label_repel(
        label="name",
        fill="lightyellow",
        color="#34495e",
        size=8,
        segment_color="#95a5a6",
    )
    + theme_minimal()
    + labs(
        title="geom_label_repel — boxed labels with connectors",
        x="X",
        y="Y",
    )
)
plot2.save("examples/output/label_repel.png", dpi=200)

print("Saved examples/output/text_repel.png")
print("Saved examples/output/label_repel.png")
