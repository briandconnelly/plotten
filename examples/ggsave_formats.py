"""Demonstrate ggsave() with format inference and sizing options."""

import numpy as np
import pandas as pd

from plotten import aes, geom_point, geom_smooth, ggplot, ggsave, labs, theme_minimal

rng = np.random.default_rng(42)
df = pd.DataFrame({"x": rng.normal(0, 1, 200), "y": rng.normal(0, 1, 200)})

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5)
    + geom_smooth(method="loess")
    + labs(title="Publication-Ready Export", subtitle="ggsave() with 300 DPI default")
    + theme_minimal()
)

# Save with ggsave — format inferred from extension
ggsave(p, "examples/output/ggsave_formats.png", width=6, height=4)
