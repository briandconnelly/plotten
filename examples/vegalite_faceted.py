"""Faceted scatter plot exported as Vega-Lite HTML."""

import polars as pl

from plotten import aes, facet_wrap, geom_point, ggplot, labs, theme_minimal, to_html

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8],
        "y": [
            45,
            52,
            58,
            65,
            70,
            78,
            82,
            90,
            50,
            55,
            62,
            68,
            75,
            80,
            88,
            95,
            40,
            48,
            55,
            60,
            64,
            72,
            76,
            85,
        ],
        "subject": ["Math"] * 8 + ["Science"] * 8 + ["English"] * 8,
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=40, alpha=0.7)
    + facet_wrap("subject", ncol=3)
    + theme_minimal()
    + labs(
        title="Scores by Subject",
        subtitle="Faceted into separate panels",
        x="Study Hours",
        y="Test Score",
    )
)

html = to_html(plot)
with open("examples/output/vegalite_faceted.html", "w") as f:
    f.write(html)

print("Wrote examples/output/vegalite_faceted.html")
