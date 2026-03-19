"""Multi-layer plot with smooth trend line, exported as Vega-Lite HTML."""

import polars as pl

from plotten import aes, geom_point, geom_smooth, ggplot, labs, theme_minimal, to_html

df = pl.DataFrame(
    {
        "study_hours": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 1.5, 2.5, 3.5, 5.5, 6.5, 7.5],
        "score": [
            45.0,
            52.0,
            58.0,
            65.0,
            70.0,
            78.0,
            82.0,
            90.0,
            48.0,
            55.0,
            60.0,
            73.0,
            80.0,
            87.0,
        ],
    }
)

plot = (
    ggplot(df, aes(x="study_hours", y="score"))
    + geom_point(alpha=0.7, size=60)
    + geom_smooth(method="lm")
    + theme_minimal()
    + labs(
        title="Study Hours vs Test Scores",
        subtitle="Points with linear regression trend line",
        x="Hours Studied per Day",
        y="Test Score",
    )
)

html = to_html(plot)
with open("examples/output/vegalite_multi_layer.html", "w") as f:
    f.write(html)

print("Wrote examples/output/vegalite_multi_layer.html")
