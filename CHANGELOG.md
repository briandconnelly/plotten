# Changelog

## 1.0.0

### v0.15.0 — API Polish & 1.0 Preparation

- Add `colour` alias for `color` in `aes()`
- Add `units` parameter to `PlotGrid.save()` for consistency with `Plot.save()`
- Improve error messages: column name suggestions via `difflib.get_close_matches`
- Improve error messages: scale/data type mismatch includes column name and dtype
- Improve error messages: `theme()` typos suggest closest valid property
- Validate mapped columns exist in data for positional aesthetics
- Lazy imports for faster `import plotten` startup
- Scale computation caching for `get_breaks()` and `get_labels()`
- Comprehensive `__all__` audit (233 exports verified)

### v0.14.0 — New Geoms, Positions, Stats, Binned Scales

- Add `geom_freqpoly` (frequency polygon)
- Add `geom_errorbarh` (horizontal error bars)
- Add `position_jitterdodge` (combined dodge + jitter)
- Add `interaction()` helper for combining variables in aesthetics
- Add `stat_cor` for Pearson/Spearman correlation annotations
- Enhance `stat_summary` with `median_hilow`, `mean_range`, and `fun_data` parameter
- Add `scale_color_binned` / `scale_fill_binned` for discrete color bins
- Add `scale_color_steps`, `scale_fill_steps`, `scale_color_fermenter`, `scale_fill_fermenter`

### Layout Refactor

- Replace `tight_layout` + hardcoded positioning with `constrained_layout` + `subfigures`
- Dedicated regions for title, subtitle, panels, caption, and legend
- Eliminate 12 hardcoded figure-fraction positioning constants
- Fix strip label / axis title overlap at all font sizes

### v0.13.0 — Layout, Composition, Facets, Coord Trans

- Add `coord_trans()` for arbitrary axis transformations (log10, sqrt, reverse, exp, custom)
- Add `inset_element()` for embedding plots within plots
- Add facet labellers: `labeller_both()`, `labeller_wrap()`
- Add `strip_position="bottom"` for `facet_wrap()`
- Add `plot_grid(guides="collect")` for shared legends

### v0.12.0 — Polynomial Smooth, Stat Ellipse, Geom Count, Ridge Plots

- Add polynomial smoothing (`method="poly"`, configurable degree)
- Add `stat_ellipse` for confidence ellipses (requires scipy)
- Add `geom_count` / `stat_count_overlap` for overlapping point counts
- Add `geom_density_ridges` / `stat_density_ridges` for ridge plots

### v0.11.0 — Remove Pandas Dependency, New Scales, Theme System

- Remove pandas as a dependency; use narwhals for dataframe abstraction
- Add `ggsave()` for publication-quality output
- Add identity scales (`scale_color_identity`, `scale_fill_identity`, etc.)
- Add grey/gray scales
- Add `theme_set()`, `theme_get()`, `theme_update()` for global theming
- Add callable breaks support for scales

### v0.10.0 — Rendering Polish, Quality of Life, New Geoms, Annotations

- Add `theme()` function for incremental theme overrides
- Smart facet axis labels (shared edge labels)
- Better default axis formatting (`_smart_format`)
- Multi-column legend support via `guide_legend(ncol=...)`
- Add viridis scale convenience functions
- Add `expand_limits()`
- Better error messages with column suggestions
- `after_stat` validation
- Add `geom_curve`, `geom_spoke`, `geom_dotplot`, `stat_summary_bin`
- Annotations overhaul: arrow styles, curved arrows, text boxes, brackets
