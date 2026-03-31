# Changelog

## 0.1.0 — Initial Public Release

First public release of plotten, a grammar-of-graphics plotting library for Python.

### Core

- `ggplot()` + `aes()` with layered `+` composition, mirroring ggplot2's API
- `colour` works as an alias for `color` everywhere
- Immutable `Plot` dataclass built up via `+` operator
- Works with pandas, polars, and other DataFrame libraries via narwhals
- Declarative spec API: `from_spec()`, `from_spec_json()`, `spec_schema()`
- Vega-Lite export: `to_vegalite()`, `to_html()`

### Geoms (45+)

point, jitter, count, line, path, step, segment, curve, spoke, area, ribbon, bar, col, histogram, density, freqpoly, dotplot, boxplot, violin, density_ridges, qq, qq_line, quantile, bin2d, hex, contour, contour_filled, raster, tile, errorbar, errorbarh, crossbar, pointrange, linerange, text, label, text_repel, label_repel, hline, vline, abline, rect, polygon, rug, smooth, blank, signif

### Scales (50+)

- Position: continuous, discrete, log10, sqrt, reverse, date, datetime, binned
- Color/fill: continuous, discrete, manual, identity, brewer, distiller, viridis, gradient, gradient2, gradientn, grey, steps, fermenter
- Size, alpha, shape, linetype, linewidth, hatch: continuous, discrete, manual, identity, and area variants
- Secondary axes via `sec_axis()` and `dup_axis()`
- Breaks: `breaks_pretty`, `breaks_width`, `breaks_integer`, `breaks_log`, `breaks_quantile`, callable breaks
- Labels: `label_comma`, `label_dollar`, `label_percent`, `label_scientific`, `label_si`, `label_bytes`, `label_date`, `label_pvalue`, `label_ordinal`, `label_duration`, `label_wrap`
- Out-of-bounds: `oob_censor`, `oob_keep`, `oob_squish`

### Stats

`stat_ecdf`, `stat_summary`, `stat_summary_bin`, `stat_function`, `stat_density_2d`, `stat_density_2d_filled`, `stat_ellipse`, `stat_cor`, `stat_poly_eq`, `stat_sum`, `stat_unique`

### Positions

identity, dodge, dodge2, jitter, jitterdodge, nudge, stack, fill, beeswarm

### Coordinates

cartesian, flip, polar, equal/fixed, trans (log10, sqrt, reverse, exp, custom)

### Facets

- `facet_wrap()` and `facet_grid()` with free/fixed scales
- Labellers: `label_value`, `labeller_both`, `labeller_wrap`
- Configurable strip position

### Themes

- 13 built-in themes: default, grey/gray, bw, minimal, classic, dark, light, linedraw, void, tufte, economist, 538, seaborn
- Full customization via `theme()` with `element_text`, `element_line`, `element_rect`, `element_blank`
- `margin()` and `rel()` helpers
- Global defaults: `theme_set()`, `theme_get()`, `theme_update()`

### Composition

- `|` (side by side) and `/` (stacked) operators
- `plot_grid()` for arbitrary layouts with `guides="collect"`
- `inset_element()` for embedding plots within plots
- `plot_annotation()` for shared titles and captions

### Plot recipes

`plot_waterfall`, `plot_dumbbell`, `plot_lollipop`, `plot_slope`, `plot_forest`, `plot_waffle`

### Output and accessibility

- `ggsave()` with 300 DPI default, width/height in inches/cm/mm
- `accessibility_report()` checks colorblind safety, contrast ratios, and font sizes
- `register_font()` and `register_google_font()` for custom fonts
- Strict mode (`set_strict(True)`) converts warnings to errors for CI

### Error handling

- Domain-specific error hierarchy: `ValidationError`, `DataError`, `ScaleError`, `StatError`, `RenderError`, `ConfigError`, `FontError`, `ExportError`, `SpecError`
- Typo suggestions for column names, geom parameters, theme properties, and color names

### Datasets

7 built-in datasets via `load_dataset()`: diamonds, mtcars, iris, faithful, tips, mpg, penguins

### Rendering

- `constrained_layout` with dedicated regions for title, subtitle, panels, caption, and legend
- Computed aesthetics: `after_stat()`, `after_scale()`, `stage()`
- Lazy imports for fast startup
- Scale computation caching
