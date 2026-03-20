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

45 geometry layers including point, line, bar, histogram, density, boxplot, violin, ribbon, area, tile, hex, contour, segment, curve, spoke, dotplot, errorbar, crossbar, pointrange, polygon, rug, step, text, label, raster, refline, col, freqpoly, errorbarh, density ridges, QQ, quantile, bin2d, jitter, count, and more.
10 stat layers: `stat_ecdf`, `stat_summary`, `stat_summary_bin`, `stat_function`, `stat_density_2d`, `stat_ellipse`, `stat_cor`, `stat_poly_eq`, and more.

### Repel Geoms

`geom_text_repel()` and `geom_label_repel()` automatically reposition overlapping labels with connector segments.

### Scales

50+ scales across color, fill, size, shape, alpha, linetype, position, and date aesthetics.
Includes manual, identity, grey, viridis, Brewer, gradient, log, sqrt, reverse, binned, and discrete variants.
Secondary axes via `sec_axis()` and `dup_axis()`.

### Coordinates

Cartesian, polar, flipped, equal, fixed, and arbitrary transformations via `coord_trans()`.

### Positions

9 position adjustments: identity, dodge, dodge2, stack, fill, jitter, jitterdodge, nudge, and beeswarm.

### Facets

`facet_wrap()` and `facet_grid()` with free/fixed scales, custom labellers, and configurable strip position.

### Themes

Built-in themes (grey, bw, minimal, classic, dark, void, light) with full customization via `theme()`.
Global theme management with `theme_set()`, `theme_get()`, `theme_update()`.

### Font Support

Register custom or Google Fonts with `register_font()` and `register_google_font()`.
List available fonts with `available_fonts()`.

### Plot Recipes

High-level chart types built on the grammar: `plot_waterfall()`, `plot_dumbbell()`, `plot_lollipop()`, `plot_slope()`, `plot_forest()`.

### Composition

Combine plots with `|` (side by side) and `/` (stacked).
Grid layouts via `plot_grid()` with collected legends and shared annotations.
Inset plots via `inset_element()`.

### Annotations

Text, segment, curve, rect, hline, vline, abline, and bracket annotations with configurable arrow styles.

### Built-in Datasets

7 classic datasets available via `load_dataset()`: diamonds, mtcars, iris, faithful, tips, mpg, and penguins.

### Accessibility

`accessibility_report()` audits a plot for colorblind safety, contrast ratios, and font sizes.

### Vega-Lite Export

Convert plots to Vega-Lite specs with `to_vegalite()` or self-contained HTML with `to_html()`.

### Output

Save to any format via `Plot.save()` with publication-quality defaults.
Jupyter notebook integration via `_repr_png_()`.

## Dependencies

- **narwhals** — dataframe abstraction (works with pandas, polars, and other backends)
- **matplotlib** >= 3.8
- **numpy** >= 1.24
- **scipy** (optional) — for smooth geoms, confidence ellipses, and correlation p-values

## License

MIT
