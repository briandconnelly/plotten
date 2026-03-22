"""Legend key showcase — demonstrates geom-aware legend swatches.

In ggplot2, legend swatches match the geom that uses the aesthetic:
  - geom_point() produces point (scatter) swatches
  - geom_line() produces line swatches
  - geom_col() produces rectangle swatches

This example shows all three side by side, plus a combined plot
demonstrating that the first layer determines the swatch type.
"""

from __future__ import annotations

import pandas as pd

from plotten import (
    aes,
    element_text,
    geom_col,
    geom_line,
    geom_point,
    geom_smooth,
    geom_step,
    ggplot,
    ggsave,
    labs,
    scale_color_brewer,
    scale_fill_brewer,
    theme,
)

# --- Shared data ---
df = pd.DataFrame(
    {
        "year": [2019, 2020, 2021, 2022, 2023] * 3,
        "sales": [
            10,
            14,
            18,
            22,
            28,
            8,
            11,
            15,
            19,
            24,
            5,
            9,
            12,
            16,
            21,
        ],
        "region": ["North"] * 5 + ["South"] * 5 + ["West"] * 5,
    }
)

shared_theme = theme(
    title_size=13,
    label_size=10,
    tick_size=9,
    font_family="sans-serif",
    plot_title=element_text(weight="bold"),
    legend_title_element=element_text(size=9, weight="bold"),
    legend_text_element=element_text(size=8),
    panel_background="#fafafa",
)

# --- 1. Point legend ---
p_point = (
    ggplot(df, aes(x="year", y="sales", color="region"))
    + geom_point(size=60, alpha=0.8)
    + scale_color_brewer(palette="Set2")
    + labs(title="Point swatches", x="Year", y="Sales", color="Region")
    + shared_theme
)

# --- 2. Line legend ---
p_line = (
    ggplot(df, aes(x="year", y="sales", color="region"))
    + geom_line(size=1.2)
    + scale_color_brewer(palette="Set2")
    + labs(title="Line swatches", x="Year", y="Sales", color="Region")
    + shared_theme
)

# --- 3. Rectangle legend (bar/col) ---
df_bar = pd.DataFrame(
    {
        "category": ["Q1", "Q2", "Q3", "Q4"] * 3,
        "revenue": [30, 45, 38, 52, 25, 40, 35, 48, 20, 32, 28, 42],
        "product": ["Widget"] * 4 + ["Gadget"] * 4 + ["Gizmo"] * 4,
    }
)

p_rect = (
    ggplot(df_bar, aes(x="category", y="revenue", fill="product"))
    + geom_col()
    + scale_fill_brewer(palette="Pastel1")
    + labs(title="Rectangle swatches", x="Quarter", y="Revenue", fill="Product")
    + shared_theme
)

# --- 4. Combined: first geom wins ---
p_combined = (
    ggplot(df, aes(x="year", y="sales", color="region"))
    + geom_line(size=1.0, alpha=0.4)
    + geom_point(size=50, alpha=0.9)
    + scale_color_brewer(palette="Set2")
    + labs(
        title="First layer wins",
        subtitle="geom_line() added first, so legend shows line swatches",
        x="Year",
        y="Sales",
        color="Region",
    )
    + shared_theme
    + theme(plot_subtitle=element_text(color="#666666", size=9))
)

# --- Save individually ---
ggsave(p_point, "examples/legend_keys_point.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_point.png")

ggsave(p_line, "examples/legend_keys_line.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_line.png")

ggsave(p_rect, "examples/legend_keys_rect.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_rect.png")

ggsave(p_combined, "examples/legend_keys_first_wins.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_first_wins.png")

# --- 5. Step geom also gets line swatches ---
p_step = (
    ggplot(df, aes(x="year", y="sales", color="region"))
    + geom_step(size=1.2)
    + scale_color_brewer(palette="Dark2")
    + labs(title="Step geom uses line swatches", x="Year", y="Sales", color="Region")
    + shared_theme
)
ggsave(p_step, "examples/legend_keys_step.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_step.png")

# --- 6. Point + smooth overlay (first layer = point, so point swatches) ---
p_point_smooth = (
    ggplot(df, aes(x="year", y="sales", color="region"))
    + geom_point(size=50, alpha=0.7)
    + geom_smooth(method="ols", se=False, linetype="--", size=0.8)
    + scale_color_brewer(palette="Set1")
    + labs(
        title="Point + smooth overlay",
        subtitle="geom_point() is first layer, legend shows point swatches",
        x="Year",
        y="Sales",
        color="Region",
    )
    + shared_theme
    + theme(plot_subtitle=element_text(color="#666666", size=9))
)
ggsave(p_point_smooth, "examples/legend_keys_overlay.png", width=6, height=4, dpi=150)
print("Saved examples/legend_keys_overlay.png")
