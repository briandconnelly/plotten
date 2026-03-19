"""Show all built-in themes side by side using plot composition."""

import polars as pl

from plotten import (
    aes,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    theme_538,
    theme_bw,
    theme_classic,
    theme_dark,
    theme_default,
    theme_economist,
    theme_minimal,
    theme_seaborn,
    theme_tufte,
    theme_void,
)

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [3, 7, 4, 8, 5, 9, 6, 10],
    }
)


def make_plot(theme_fn, name):
    return (
        ggplot(df, aes(x="x", y="y"))
        + geom_point(size=40, alpha=0.8)
        + geom_smooth(method="ols", se=True)
        + theme_fn()
        + labs(title=name, x="X", y="Y")
    )


p_default = make_plot(theme_default, "theme_default")
p_bw = make_plot(theme_bw, "theme_bw")
p_minimal = make_plot(theme_minimal, "theme_minimal")
p_classic = make_plot(theme_classic, "theme_classic")
p_dark = make_plot(theme_dark, "theme_dark")
p_void = make_plot(theme_void, "theme_void")
p_538 = make_plot(theme_538, "theme_538")
p_economist = make_plot(theme_economist, "theme_economist")
p_tufte = make_plot(theme_tufte, "theme_tufte")
p_seaborn = make_plot(theme_seaborn, "theme_seaborn")

# Arrange in a 2x5 grid using | and /
row1 = p_default | p_bw | p_minimal | p_classic | p_dark
row2 = p_void | p_538 | p_economist | p_tufte | p_seaborn
grid = row1 / row2

grid.save("examples/output/theme_gallery.png", dpi=150, width=20, height=8)
