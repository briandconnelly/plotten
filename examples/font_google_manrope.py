"""Example using Google Font 'Manrope'."""

import polars as pl

from plotten import (
    aes,
    element_text,
    geom_point,
    geom_smooth,
    ggplot,
    ggsave,
    labs,
    register_google_font,
    theme,
    theme_minimal,
)

family = register_google_font("Manrope")
print(f"Registered: {family}")

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [2, 4, 3, 7, 5, 9, 6, 10],
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    }
)

p = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=3)
    + geom_smooth()
    + labs(
        title="Manrope from Google Fonts",
        subtitle="Downloaded and registered automatically",
        caption="plotten + register_google_font()",
        x="Predictor",
        y="Response",
    )
    + theme_minimal()
    + theme(
        font_family=family,
        plot_title=element_text(size=20, weight="bold"),
        plot_subtitle=element_text(size=12, color="#666666"),
        plot_caption=element_text(size=8, color="#999999", style="italic"),
        axis_title=element_text(size=13, weight="bold"),
    )
)
ggsave(p, "examples/font_google_manrope.png", width=8, height=5)
print("Saved font_google_manrope.png")
