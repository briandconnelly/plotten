# plotten

**A grammar-of-graphics plotting library for Python — ggplot2's API, Python's ecosystem.**

If you've used ggplot2 in R, plotten will feel immediately familiar.
If you haven't, the grammar of graphics is a composable, layered approach to building charts: you describe *what* your data is and *how* it should be encoded visually, and the library handles the rest.

```python
from plotten import ggplot, aes, geom_point, geom_smooth, labs, theme_minimal
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + geom_smooth(method="ols")
    + labs(title="Engine displacement vs. highway MPG", x="Displacement (L)", y="Highway MPG")
    + theme_minimal()
)
```

## Installation

```bash
pip install plotten
```

## Why plotten?

### For R/ggplot2 users

plotten is a faithful Python port of the ggplot2 mental model.
The same layered grammar, the same `aes()` mappings, the same `+` composition, and many of the same function names (`geom_point`, `facet_wrap`, `scale_color_brewer`, `theme_minimal`, `ggsave`, ...).
You can also use `colour=` as an alias for `color=` everywhere.

### For data analysts

plotten works with both **pandas** and **polars** out of the box via [narwhals](https://github.com/narwhals-dev/narwhals) — no conversion needed.
Fifty-plus scales, nine position adjustments, and a full faceting system cover the long tail of real-world chart types without reaching for matplotlib directly.

### For scientists and publication authors

`ggsave()` defaults to **300 DPI** and accepts `width`/`height` in inches, centimeters, or millimeters.
The accessibility auditor (`accessibility_report()`) checks colorblind safety, contrast ratios, and font sizes before you submit.
Custom and Google Fonts are supported out of the box via `register_font()` / `register_google_font()`.

---

## Features

### 45+ Geometry layers

Point, line, bar, col, histogram, density, boxplot, violin, ribbon, area, tile, hex, bin2d, contour, segment, curve, spoke, dotplot, errorbar, errorbarh, crossbar, pointrange, linerange, polygon, rug, step, text, label, raster, refline, freqpoly, density ridges, QQ, quantile, jitter, count, and more.

### Automatic label repelling

`geom_text_repel()` and `geom_label_repel()` automatically reposition overlapping labels and draw connector segments — no manual nudging.

```python
from plotten import geom_text_repel

ggplot(df, aes(x="x", y="y", label="name")) + geom_text_repel()
```

### 10 statistical layers

`stat_ecdf`, `stat_summary`, `stat_summary_bin`, `stat_function`, `stat_density_2d`, `stat_ellipse`, `stat_cor`, `stat_poly_eq`, `stat_sum`, `stat_unique` — computed on the fly from your raw data.

### Computed aesthetics

Map aesthetics to values computed *after* statistics (`after_stat`) or *after* scale mapping (`after_scale`), just like ggplot2:

```python
from plotten import ggplot, aes, geom_histogram, after_stat
from plotten.datasets import load_dataset

diamonds = load_dataset("diamonds")

# Fill histogram bars by their density instead of count
ggplot(diamonds, aes(x="carat", y=after_stat("density"))) + geom_histogram()
```

### 50+ scales

Color, fill, size, shape, alpha, linetype, linewidth, hatch, and position scales.
Includes manual, identity, grey, viridis, Brewer, gradient, log, sqrt, reverse, binned, and discrete variants.
Secondary axes via `sec_axis()` and `dup_axis()`.

### Full faceting

`facet_wrap()` and `facet_grid()` with free/fixed scales, custom labellers (`labeller_both`, `labeller_wrap`), and configurable strip position.

### Themes

Built-in themes for every taste: `theme_grey`, `theme_bw`, `theme_minimal`, `theme_classic`, `theme_dark`, `theme_void`, `theme_linedraw`, `theme_light`, `theme_tufte`, `theme_economist`, `theme_538`, `theme_seaborn`.
Customise any element with `theme()` and manage global defaults with `theme_set()` / `theme_get()` / `theme_update()`.

### Plot composition

Combine plots with `|` (side by side) and `/` (stacked), or use `plot_grid()` for arbitrary grids with collected legends and shared annotations.
Embed one plot inside another with `inset_element()`.

```python
(scatter | histogram) / residuals
```

### Plot recipes

High-level constructors for common patterns: `plot_waterfall()`, `plot_dumbbell()`, `plot_lollipop()`, `plot_slope()`, `plot_forest()`, `plot_waffle()`.

### Declarative spec API

Build plots from plain Python dicts (or JSON) with `from_spec()`.
A JSON Schema is available via `spec_schema()` — useful for validating specs programmatically or feeding into AI agents:

```python
import json
from plotten import spec_schema, from_spec

# Validate before rendering
schema = spec_schema()   # full enum lists for geoms, scales, themes, …
plot = from_spec({"geom": "point", "mapping": {"x": "hp", "y": "mpg"}}, data=df)
```

### Vega-Lite export

Convert any plot to a Vega-Lite specification or a self-contained HTML file:

```python
vl_spec = plot.to_vegalite()
plot.to_html("chart.html")
```

### Accessibility auditing

```python
report = accessibility_report(plot)
print(report)
# Accessibility Report — ISSUES FOUND (1 item(s))
#   [WARN] [colorblind] Palette may be indistinguishable under deuteranopia
#          Suggestion: use scale_color_viridis() or a colorblind-safe Brewer palette
```

### Helpful error messages

plotten raises domain-specific errors (`ValidationError`, `DataError`, `ScaleError`, `RenderError`, …) with typo suggestions for geom parameters, column names, theme properties, and color names.
Turn all warnings into errors for CI and AI agents with `set_strict(True)`.

```python
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")
ggplot(mpg, aes(x="displcement", y="hwy"))
# DataError: column 'displcement' not found. Did you mean 'displ'?
```

### Font support

```python
from plotten import register_google_font, available_fonts

register_google_font("Lato")
available_fonts()  # lists all registered fonts
```

### Built-in datasets

Seven classic datasets via `load_dataset()`: `diamonds`, `mtcars`, `iris`, `faithful`, `tips`, `mpg`, `penguins`.

---

## Quick examples

**Scatter with smooth + facets**

```python
from plotten import ggplot, aes, geom_point, geom_smooth, facet_wrap, theme_bw
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(aes(color="drv"), alpha=0.6)
    + geom_smooth(method="loess")
    + facet_wrap("class", ncol=3)
    + theme_bw()
)
```

**Ridge plot**

```python
from plotten import ggplot, aes, geom_density_ridges, scale_fill_viridis, theme_minimal
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="hwy", y="class", fill="class"))
    + geom_density_ridges(alpha=0.8)
    + scale_fill_viridis(discrete=True)
    + theme_minimal()
)
```

**Composition**

```python
from plotten import plot_grid

plot_grid([p1, p2, p3], ncol=2, guides="collect")
```

**Publication-quality export**

```python
from plotten import ggsave

ggsave(plot, "figure1.pdf", width=180, height=120, units="mm", dpi=300)
```

---

## Dependencies

| Package | Role |
|---|---|
| **narwhals** | DataFrame abstraction — works with pandas, polars, and more |
| **matplotlib** ≥ 3.8 | Rendering backend |
| **numpy** ≥ 1.24 | Numerical operations |
| **scipy** *(optional)* | Smooth geoms, confidence ellipses, correlation p-values |

---

## License

MIT
