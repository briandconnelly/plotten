"""Crossbar and pointrange geoms for interval estimates."""

import polars as pl

from plotten import aes, geom_crossbar, geom_pointrange, ggplot, labs, theme_bw
from plotten._composition import plot_grid

treatments = ["Control", "Drug A", "Drug B", "Drug C"]

df = pl.DataFrame(
    {
        "treatment": treatments,
        "mean": [5.2, 7.8, 6.5, 9.1],
        "lo": [4.0, 6.5, 5.0, 7.8],
        "hi": [6.4, 9.1, 8.0, 10.4],
    }
)

p1 = (
    ggplot(df, aes(x="treatment", y="mean", ymin="lo", ymax="hi"))
    + geom_crossbar(fill="#B3CDE3", color="#2171B5", width=0.4)
    + labs(title="Crossbar", x="Treatment", y="Response")
    + theme_bw()
)

p2 = (
    ggplot(df, aes(x="treatment", y="mean", ymin="lo", ymax="hi"))
    + geom_pointrange(color="#E6550D", size=60, linewidth=2)
    + labs(title="Pointrange", x="Treatment", y="Response")
    + theme_bw()
)

grid = plot_grid(p1, p2)
grid.save("examples/output/crossbar_pointrange.png", dpi=200)
