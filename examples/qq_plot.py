"""QQ plot to check normality of a distribution."""

import numpy as np
import polars as pl

from plotten import aes, geom_qq, geom_qq_line, ggplot, labs, theme_bw

np.random.seed(42)

df = pl.DataFrame({"values": np.random.normal(100, 15, 200).tolist()})

plot = (
    ggplot(df, aes(x="values"))
    + geom_qq(alpha=0.5)
    + geom_qq_line(color="red", size=1.5)
    + labs(
        title="Normal QQ Plot",
        subtitle="Points close to the line suggest normality",
        x="Theoretical Quantiles",
        y="Sample Quantiles",
    )
    + theme_bw()
)

plot.save("examples/output/qq_plot.png", dpi=200)
