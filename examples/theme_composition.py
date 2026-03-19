"""Demonstrate theme() incremental overrides with multiple compositions."""

import polars as pl

from plotten import (
    aes,
    element_blank,
    element_line,
    element_text,
    geom_point,
    ggplot,
    labs,
    theme,
    theme_bw,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [3, 7, 4, 8, 5, 9, 6, 10],
    }
)

# Start with theme_minimal, override title styling and rotation
p1 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#2171B5")
    + theme_minimal()
    + theme(title_size=18, title_color="#2171B5", axis_text_x_rotation=45)
    + labs(title="Minimal + Overrides", x="X Axis", y="Y Axis")
)

# Stack multiple theme() calls — each layer adds more customization
p2 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#E6550D")
    + theme_bw()
    + theme(panel_background="#FFF5EB", grid_color="#FDDBC7")
    + theme(title_size=18, title_color="#E6550D")
    + theme(
        plot_title=element_text(size=20, color="#E6550D", weight="bold"),
        panel_grid_minor=element_blank(),
    )
    + labs(title="BW + Layered Themes", x="X Axis", y="Y Axis")
)

# Combine element overrides with flat theme properties
p3 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#31A354")
    + theme(
        background="#F0F7F0",
        panel_background="#E5F5E0",
        panel_grid_major=element_line(color="#A1D99B", size=0.5),
        panel_grid_minor=element_blank(),
        plot_title=element_text(size=20, color="#31A354"),
        axis_text_x_rotation=30,
    )
    + labs(title="Custom Green Theme", x="X Axis", y="Y Axis")
)

# Dark mode via theme()
p4 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#FFD700")
    + theme(
        background="#1a1a2e",
        panel_background="#16213e",
        grid_color="#0f3460",
        title_color="#e0e0e0",
        title_size=18,
        axis_line_x=False,
        axis_line_y=False,
    )
    + labs(title="Dark Mode via theme()", x="X Axis", y="Y Axis")
)

grid = (p1 | p2) / (p3 | p4)
grid.save("examples/output/theme_composition.png", dpi=200)
