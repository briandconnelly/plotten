# plotten

A grammar-of-graphics plotting library for Python, inspired by ggplot2.

## Installation

```bash
pip install plotten
```

## Quick Start

```python
import pandas as pd
from plotten import aes, geom_point, geom_smooth, ggplot, labs, theme_minimal

df = pd.DataFrame({"x": range(50), "y": [v**2 + v for v in range(50)]})

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.6)
    + geom_smooth(method="ols")
    + labs(title="Quick Start", x="X", y="Y")
    + theme_minimal()
)
p.save("plot.png")
```

## Features

### Geoms

35 geometry layers including point, line, bar, histogram, density, boxplot, violin, ribbon, area, tile, hex, contour, segment, curve, spoke, dotplot, errorbar, crossbar, pointrange, polygon, rug, step, text, label, raster, refline, col, freqpoly, errorbarh, density ridges, and more.

### Stats

22 statistical transformations: bin, density, smooth (OLS/LOESS/polynomial), boxplot, violin, count, ecdf, QQ, summary, summary_bin, contour, density2d, function overlay, dotplot, ellipse, poly_eq, correlation, count_overlap, density_ridges, bin2d, and identity.

### Scales

40+ scales across color, fill, size, shape, alpha, linetype, position, and date aesthetics.
Includes manual, identity, grey, viridis, Brewer, gradient, log, sqrt, reverse, binned, and discrete variants.

### Coordinates

Cartesian, polar, flipped, equal, and arbitrary transformations via `coord_trans()`.

### Facets

`facet_wrap()` and `facet_grid()` with free/fixed scales, custom labellers, and configurable strip position.

### Themes

Built-in themes (grey, bw, minimal, classic, dark, void, light) with full customization via `theme()`.
Global theme management with `theme_set()`, `theme_get()`, `theme_update()`.

### Composition

Combine plots with `|` (side by side) and `/` (stacked).
Grid layouts via `plot_grid()` with collected legends and shared annotations.
Inset plots via `inset_element()`.

### Annotations

Text, segment, curve, rect, hline, vline, abline, and bracket annotations with configurable arrow styles.

### Output

Save to any format via `ggsave()` with publication-quality defaults.
Jupyter notebook integration via `_repr_png_()`.

## Dependencies

- **narwhals** — dataframe abstraction (works with pandas, polars, and other backends)
- **matplotlib** >= 3.8
- **numpy** >= 1.24
- **scipy** (optional) — for smooth geoms, confidence ellipses, and correlation p-values

## License

MIT
