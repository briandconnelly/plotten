"""Identity scales — use data values directly as aesthetics."""

import pandas as pd

from plotten import aes, geom_point, ggplot, labs, scale_color_identity, theme_minimal

df = pd.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6],
        "y": [3, 1, 4, 1, 5, 9],
        "color": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"],
        "label": ["Red", "Blue", "Green", "Purple", "Orange", "Brown"],
    }
)

p = (
    ggplot(df, aes(x="x", y="y", color="color"))
    + geom_point(size=80)
    + scale_color_identity()
    + labs(
        title="Identity Scale",
        subtitle="Data column contains literal color values",
        x="X",
        y="Y",
    )
    + theme_minimal()
)

p.save("examples/output/identity_scales.png", width=7, height=5)
