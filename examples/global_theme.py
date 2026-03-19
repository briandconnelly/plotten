"""Global theme — set once, apply everywhere."""

import pandas as pd

from plotten import (
    Theme,
    aes,
    geom_col,
    geom_point,
    ggplot,
    labs,
    plot_grid,
    theme,
    theme_dark,
    theme_set,
)

# Set a global dark theme
theme_set(theme_dark() + theme(title_size=16))

df1 = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 5, 4]})
df2 = pd.DataFrame({"x": ["A", "B", "C"], "y": [10, 25, 15]})

p1 = ggplot(df1, aes(x="x", y="y")) + geom_point(size=40) + labs(title="Scatter Plot")

p2 = ggplot(df2, aes(x="x", y="y")) + geom_col() + labs(title="Bar Chart")

grid = plot_grid(p1, p2, ncol=2)
grid.save("examples/output/global_theme.png", width=12, height=5)

# Reset global theme
theme_set(Theme())
