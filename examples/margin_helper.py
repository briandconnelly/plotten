"""Plot margins with the margin() helper and unit conversion."""

import polars as pl

from plotten import aes, geom_point, ggplot, labs, margin, theme, theme_bw

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 3, 5, 4],
    }
)

# No margin — plot fills the figure
no_margin = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=3, color="steelblue")
    + labs(title="Default")
    + theme_bw()
    + theme(plot_background={"fill": "#f0f0f0"})
)

# NPC margin: 8% on all sides (normalized 0-1 coordinates)
npc = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=3, color="steelblue")
    + labs(title="margin(0.08, unit='npc')")
    + theme_bw()
    + theme(
        plot_margin=margin(0.08, 0.08, 0.08, 0.08, unit="npc"),
        plot_background={"fill": "#f0f0f0"},
    )
)

# Inch margin: 0.6 inches on all sides
inch = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=3, color="steelblue")
    + labs(title="margin(0.6, unit='in')")
    + theme_bw()
    + theme(
        plot_margin=margin(0.6, 0.6, 0.6, 0.6, unit="in"),
        plot_background={"fill": "#f0f0f0"},
    )
)

# Centimetre margin: 2 cm on all sides
cm = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=3, color="steelblue")
    + labs(title="margin(2, unit='cm')")
    + theme_bw()
    + theme(
        plot_margin=margin(2, 2, 2, 2, unit="cm"),
        plot_background={"fill": "#f0f0f0"},
    )
)

grid = (no_margin | npc) / (inch | cm)
grid.save("examples/output/margin_helper.png", dpi=200)
