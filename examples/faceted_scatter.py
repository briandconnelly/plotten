"""Faceted scatter plot showing subgroups in separate panels."""

import polars as pl

from plotten import aes, facet_wrap, geom_point, geom_smooth, ggplot, labs

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
        "subject": [
            "Math",
            "Math",
            "Math",
            "Math",
            "Math",
            "Math",
            "Math",
            "Math",
            "Science",
            "Science",
            "Science",
            "Science",
            "Science",
            "Science",
            "Science",
            "Science",
            "English",
            "English",
            "English",
            "English",
            "English",
            "English",
            "English",
            "English",
        ],
    }
)

plot = (
    ggplot(df, aes(x="study_hours", y="score"))
    + geom_point(size=40, alpha=0.7)
    + geom_smooth(method="ols", se=True)
    + facet_wrap("subject", ncol=3)
    + labs(
        title="Study Hours vs Test Scores",
        x="Hours Studied per Day",
        y="Test Score",
    )
)

plot.save("examples/output/faceted_scatter.png", dpi=200)
