"""Example showing the updated default title/caption alignment.

Titles and subtitles are now left-aligned by default (plot_title_position="plot"),
matching ggplot2 >= 3.5.0 behavior.
"""

import pandas as pd

from plotten import aes, geom_point, ggplot, labs

df = pd.DataFrame(
    {
        "displ": [1.8, 1.8, 2.0, 2.0, 2.8, 2.8, 3.1, 3.1, 3.8, 4.6, 5.3, 5.7, 6.2],
        "hwy": [29, 29, 31, 30, 26, 26, 27, 25, 22, 17, 20, 15, 17],
        "class": [
            "compact",
            "compact",
            "compact",
            "compact",
            "midsize",
            "midsize",
            "midsize",
            "midsize",
            "suv",
            "suv",
            "suv",
            "suv",
            "suv",
        ],
    }
)

p = (
    ggplot(df, aes(x="displ", y="hwy", color="class"))
    + geom_point(size=3)
    + labs(
        title="Fuel economy by engine size",
        subtitle="Highway MPG decreases with displacement",
        caption="Source: EPA fuel economy data",
    )
)

p.save("examples/title_position_default.png", width=7, height=5, dpi=150)
