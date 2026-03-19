"""Faceted scatter plot with clean shared edge labels."""

import polars as pl

from plotten import aes, facet_wrap, geom_point, geom_smooth, ggplot, labs, theme, theme_minimal

df = pl.DataFrame(
    {
        "study_hours": [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8],
        "score": [
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

# Smart facet labels: only bottom row gets x-labels, only left column gets y-labels
# Use theme() to fine-tune the faceted plot appearance
plot = (
    ggplot(df, aes(x="study_hours", y="score"))
    + geom_point(size=40, alpha=0.7)
    + geom_smooth(method="ols", se=True)
    + facet_wrap("subject", ncol=3)
    + theme_minimal()
    + theme(
        title_size=16,
        strip_text_size=12,
        strip_background="#E8EAF6",
        strip_text_color="#283593",
    )
    + labs(
        title="Study Hours vs Test Scores",
        subtitle="Shared axis labels — only edge panels show labels",
        caption="Data: 8 students per subject",
        x="Hours Studied per Day",
        y="Test Score",
    )
)

plot.save("examples/output/faceted_scatter.png", dpi=200)
