"""Greyscale palettes for print-friendly output."""

import pandas as pd

from plotten import aes, geom_col, ggplot, labs, position_dodge, scale_fill_grey, theme_bw

df = pd.DataFrame(
    {
        "category": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"] * 2,
        "group": ["Control"] * 5 + ["Treatment"] * 5,
        "value": [23, 45, 12, 67, 34, 31, 52, 18, 72, 41],
    }
)

p = (
    ggplot(df, aes(x="category", y="value", fill="group"))
    + geom_col(position=position_dodge())
    + scale_fill_grey(start=0.3, end=0.7)
    + labs(
        title="Print-Friendly Greyscale",
        subtitle="scale_fill_grey() for black-and-white publications",
        x="Category",
        y="Value",
    )
    + theme_bw()
)

p.save("examples/output/grey_scales.png", width=8, height=5)
