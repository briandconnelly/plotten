"""Examples showcasing plotten's font support features."""

import polars as pl

from plotten import (
    aes,
    available_fonts,
    element_text,
    facet_wrap,
    geom_point,
    geom_smooth,
    ggplot,
    ggsave,
    labs,
    theme,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [2, 4, 3, 7, 5, 9, 6, 10],
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    }
)

# --- Example 1: Bold italic title with custom subtitle styling ---

p1 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=3)
    + geom_smooth()
    + labs(
        title="Bold Italic Title",
        subtitle="Lighter subtitle in serif font",
        caption="Data source: example",
        x="Measurement",
        y="Response",
    )
    + theme_minimal()
    + theme(
        plot_title=element_text(weight="bold", style="italic", size=18),
        plot_subtitle=element_text(family="serif", color="#666666", size=12),
        plot_caption=element_text(size=8, color="#999999", style="italic"),
    )
)
ggsave(p1, "examples/font_title_styling.png", width=8, height=5)
print("Saved font_title_styling.png")

# --- Example 2: Monospace axis labels with bold axis titles ---

p2 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=3)
    + labs(title="Monospace Ticks, Bold Axes", x="X Axis", y="Y Axis")
    + theme_minimal()
    + theme(
        axis_title=element_text(weight="bold", size=14, color="#333333"),
        axis_text=element_text(family="monospace", size=9, color="#555555"),
        plot_title=element_text(size=16, weight="bold"),
    )
)
ggsave(p2, "examples/font_axis_styling.png", width=8, height=5)
print("Saved font_axis_styling.png")

# --- Example 3: Faceted plot with bold strip labels and italic legend ---

p3 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=3)
    + facet_wrap("group")
    + labs(title="Faceted with Styled Strips", x="X", y="Y")
    + theme_minimal()
    + theme(
        strip_text=element_text(weight="bold", size=12, color="#2c3e50"),
        legend_title_element=element_text(style="italic", size=11),
        legend_text_element=element_text(color="#7f8c8d", size=9),
        plot_title=element_text(weight="bold", size=16),
    )
)
ggsave(p3, "examples/font_facet_legend.png", width=10, height=5)
print("Saved font_facet_legend.png")

# --- Example 4: All-serif theme ---

p4 = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=3)
    + geom_smooth()
    + labs(
        title="An All-Serif Plot",
        subtitle="Every text element uses serif fonts",
        x="Predictor",
        y="Outcome",
    )
    + theme_minimal()
    + theme(
        font_family="serif",
        plot_title=element_text(size=18, weight="bold"),
        plot_subtitle=element_text(size=11, style="italic"),
        axis_title=element_text(size=13),
    )
)
ggsave(p4, "examples/font_all_serif.png", width=8, height=5)
print("Saved font_all_serif.png")

# --- Print available fonts ---

fonts = available_fonts()
print(f"\n{len(fonts)} fonts available. First 20:")
for f in fonts[:20]:
    print(f"  {f}")
