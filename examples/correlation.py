"""Scatter plot with stat_cor annotation showing correlation coefficient."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    stat_cor,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

n = 80
study_hours = rng.uniform(1, 10, n)
exam_score = 40 + 5.5 * study_hours + rng.normal(0, 6, n)

df = pl.DataFrame(
    {
        "study_hours": study_hours.tolist(),
        "exam_score": exam_score.tolist(),
    }
)

plot = (
    ggplot(df, aes(x="study_hours", y="exam_score"))
    + geom_point(size=40, alpha=0.6, color="#5C6BC0")
    + geom_smooth(method="ols", color="#E53935", alpha=0.15)
    + stat_cor(method="pearson", label_x=0.05, label_y=0.95, digits=3)
    + labs(
        title="Study Hours vs Exam Score",
        subtitle="Pearson correlation with linear regression line",
        x="Study Hours per Day",
        y="Exam Score",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/correlation.png", dpi=200)
