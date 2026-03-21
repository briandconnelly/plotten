"""Theme showcase — exercises most theme-able elements in a single plot.

Produces a 2x2 faceted plot with:
  • title, subtitle, caption
  • axis titles, axis text (with rotation on x)
  • major + minor grid lines
  • panel border, panel background
  • strip labels (facet headers)
  • discrete color legend with multiple entries
  • smooth trend line (geom_smooth)
  • points with mapped color + size
  • rug marks on axes
"""

from __future__ import annotations

import pandas as pd

from plotten import (
    aes,
    element_blank,
    element_line,
    element_text,
    facet_wrap,
    geom_point,
    geom_rug,
    geom_smooth,
    ggplot,
    ggsave,
    labs,
    margin,
    scale_color_brewer,
    theme,
)

# --- Data ---
df = pd.DataFrame(
    {
        "year": [2018, 2019, 2020, 2021, 2022, 2023] * 4,
        "value": [
            12,
            15,
            14,
            18,
            22,
            25,
            8,
            10,
            13,
            15,
            17,
            20,
            20,
            22,
            19,
            24,
            28,
            32,
            5,
            7,
            9,
            11,
            14,
            16,
        ],
        "region": (["North"] * 6 + ["South"] * 6 + ["East"] * 6 + ["West"] * 6),
        "category": (["A", "B"] * 3) * 4,
    }
)

# --- Plot ---
p = (
    ggplot(df, aes(x="year", y="value", color="category"))
    + geom_point(alpha=0.8)
    + geom_smooth(method="ols", se=False, linetype="--", size=0.8)
    + geom_rug(alpha=0.3, sides="bl")
    + facet_wrap("region", ncol=2)
    + scale_color_brewer(palette="Set1")
    + labs(
        title="Regional Growth Trends",
        subtitle="Annual values by category across four regions, 2018-2023",
        caption="Source: example data  •  plotten theme showcase",
        x="Year",
        y="Value",
        color="Category",
    )
    + theme(
        # Text hierarchy
        title_size=16,
        subtitle_size=11,
        label_size=11,
        tick_size=9,
        font_family="sans-serif",
        # Title/caption alignment
        plot_title_position="plot",
        plot_caption_position="panel",
        plot_title=element_text(weight="bold"),
        plot_subtitle=element_text(color="#555555"),
        plot_caption=element_text(color="#999999", size=8),
        # Panel
        panel_background="#ffffff",
        panel_border=element_blank(),
        panel_ontop=False,
        # Grid
        grid_color="#cccccc",
        grid_line_width=0.4,
        panel_grid_minor=element_blank(),
        # Axes
        axis_line_element=element_line(color="#666666", size=0.4),
        axis_ticks=element_line(color="#999999", size=0.3),
        # Strip (facet headers)
        strip_background="none",
        strip_text=element_text(size=10, weight="bold", color="#333333"),
        # Legend
        legend_position="top",
        legend_direction="horizontal",
        legend_background="#ffffff",
        legend_title_element=element_text(size=10, weight="bold"),
        legend_text_element=element_text(size=9),
        # Plot-level
        background="#ffffff",
        plot_margin=margin(0.04, 0.04, 0.02, 0.04),
        # Spacing
        panel_spacing=0.12,
    )
)

ggsave(p, "examples/theme_showcase.png", width=9, height=7, dpi=150)
print("Saved examples/theme_showcase.png")
