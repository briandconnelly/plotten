"""P-value formatting and flexible currency labels."""

import polars as pl

from plotten import (
    aes,
    geom_col,
    ggplot,
    label_currency,
    label_pvalue,
    labs,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- label_pvalue: conventional p-value display ---

df_pvals = pl.DataFrame(
    {
        "test": ["Age", "BMI", "Glucose", "Insulin", "HbA1c"],
        "pvalue": [0.042, 0.0003, 0.85, 0.0001, 0.015],
    }
)

p_pval = (
    ggplot(df_pvals, aes(x="test", y="pvalue"))
    + geom_col(fill="#E6550D", alpha=0.8)
    + scale_y_continuous(labels=label_pvalue())
    + labs(
        title="label_pvalue()",
        subtitle="Values < 0.001 shown as '< 0.001'",
        x="Variable",
        y="P-value",
    )
    + theme_minimal()
)

# Custom threshold
p_pval2 = (
    ggplot(df_pvals, aes(x="test", y="pvalue"))
    + geom_col(fill="#756BB1", alpha=0.8)
    + scale_y_continuous(labels=label_pvalue(threshold=0.01))
    + labs(
        title="label_pvalue(threshold=0.01)",
        subtitle="Stricter threshold",
        x="Variable",
        y="P-value",
    )
    + theme_minimal()
)

# --- label_currency: flexible currency formatting ---

df_revenue = pl.DataFrame(
    {
        "region": ["US", "EU", "UK", "Japan", "Brazil"],
        "revenue_usd": [125_000, 98_000, 215_000, 67_000, 182_000],
    }
)

p_dollar = (
    ggplot(df_revenue, aes(x="region", y="revenue_usd"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_currency())
    + labs(title="label_currency()", subtitle='Default: "$" prefix', x="Region", y="Revenue")
    + theme_minimal()
)

p_euro = (
    ggplot(df_revenue, aes(x="region", y="revenue_usd"))
    + geom_col(fill="#31A354", alpha=0.8)
    + scale_y_continuous(labels=label_currency(prefix="", suffix=" EUR", accuracy=0))
    + labs(
        title='label_currency(suffix=" EUR")',
        subtitle="Suffix-style, no decimals",
        x="Region",
        y="Revenue",
    )
    + theme_minimal()
)

grid = plot_grid(p_pval, p_pval2, p_dollar, p_euro, ncol=2)
grid.save("examples/output/label_pvalue_currency.png", dpi=200)
