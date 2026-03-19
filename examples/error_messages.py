"""Demonstrate plotten's helpful error messages (non-visual example)."""

import polars as pl

from plotten import PlottenError, aes, geom_point, ggplot, theme

df = pl.DataFrame(
    {
        "height": [1.7, 1.8, 1.6, 1.75],
        "weight": [70, 85, 60, 78],
    }
)

# --- (a) Column name typo suggestion ---
print("=== Column typo suggestion ===")
try:
    plot = ggplot(df, aes(x="heigth", y="weight")) + geom_point()
    plot.save("/dev/null")
except PlottenError as exc:
    print(exc)

print()

# --- (b) Theme property typo suggestion ---
print("=== Theme property typo suggestion ===")
try:
    _ = theme(titel_size=16)
except TypeError as exc:
    print(exc)
