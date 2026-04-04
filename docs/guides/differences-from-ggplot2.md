# Differences from ggplot2

plotten follows the grammar of graphics and mirrors ggplot2's API closely.
However, several deliberate design choices make plotten more idiomatic for Python developers.
This page documents every intentional divergence from ggplot2.

For syntax-level translation (R code to Python code), see the [Migration Guide](ggplot2-migration.md).

## Naming conventions

### Underscores instead of dots

Theme properties use underscores where ggplot2 uses dots:

```python
# ggplot2: plot.title, axis.text.x, panel.grid.minor
theme(plot_title=..., axis_text_x=..., panel_grid_minor=...)
```

plotten also accepts nested dicts as a shorthand:

```python
theme(axis={"text_x": element_text(rotation=45)})
```

### `gray` is the primary spelling

Functions and themes use American English as the primary spelling, with British aliases:

| Primary | Alias |
|---------|-------|
| `scale_color_gray()` | `scale_color_grey()` |
| `theme_gray()` | `theme_grey()` |

Both spellings work everywhere, but documentation and autocomplete surface `gray` first.

### Python-style parameter names

Several parameter names were renamed from R abbreviations to self-documenting Python names:

| ggplot2 | plotten | Where |
|---------|---------|-------|
| `nrow`, `ncol` | `n_rows`, `n_cols` | `facet_wrap()`, `plot_grid()`, `guide_legend()` |
| `fun.y`, `fun.ymin`, `fun.ymax` | `center`, `lower`, `upper` | `stat_summary()` |
| `accuracy` | `precision` | `label_number()`, `label_percent()`, etc. |
| `big.mark` | `thousands_separator` | `label_number()`, `label_currency()` |
| `fmt` | `format_string` | `label_date()` |
| `units` | `unit` | `label_bytes()` |
| `legend.byrow` | `legend_row_major` | `theme()` |
| `dir` | `direction` | `facet_wrap()` |

The old names still work but emit a `DeprecationWarning`.

## Enums instead of magic strings

ggplot2 uses plain strings for constrained parameters.
plotten provides `StrEnum` types so autocomplete and type checkers catch invalid values, while bare strings still work:

```python
from plotten import FacetScales, Transform, ViridisOption

# Enum style (discoverable, type-safe)
facet_wrap("g", scales=FacetScales.FREE_X)
scale_x_continuous(transform=Transform.LOG10)
scale_color_viridis(ViridisOption.MAGMA)

# String style (still works)
facet_wrap("g", scales="free_x")
scale_x_continuous(transform="log10")
scale_color_viridis("magma")
```

Available enums:

| Enum | Used by | Values |
|------|---------|--------|
| `FacetScales` | `facet_wrap()`, `facet_grid()` | `FIXED`, `FREE`, `FREE_X`, `FREE_Y` |
| `Transform` | `scale_x/y_continuous()` | `LOG10`, `SQRT`, `REVERSE` |
| `ViridisOption` | `scale_color_viridis()` | `VIRIDIS`, `MAGMA`, `INFERNO`, `PLASMA`, `CIVIDIS` |
| `Direction` | `facet_wrap()`, `PlotGrid` | `HORIZONTAL`, `VERTICAL` |
| `StripPosition` | `facet_wrap()` | `TOP`, `BOTTOM`, `LEFT`, `RIGHT` |
| `LegendPosition` | `theme()` | `RIGHT`, `LEFT`, `TOP`, `BOTTOM`, `NONE` |
| `SmoothMethod` | `geom_smooth()` | `OLS`, `LOESS`, `MOVING_AVERAGE`, `POLY` |
| `SizeUnit` | `plot.save()` | `INCHES`, `CM`, `MM`, `PX` |
| `PolarAxis` | `coord_polar()` | `X`, `Y` |
| `GuideType` | identity scales | `NONE`, `LEGEND`, `COLORBAR` |
| `TagLevel` | `plot_annotation()` | `UPPERCASE`, `LOWERCASE`, `NUMERIC`, `ROMAN` |
| `AnnotationType` | `annotate()` | `TEXT`, `RECT`, `SEGMENT`, `CURVE`, `BRACKET` |

## Methods over standalone functions

### `plot.save()` instead of `ggsave()`

ggplot2's `ggsave()` implicitly saves the "last plot".
plotten uses an explicit method call:

```python
p = ggplot(df, aes(x="x", y="y")) + geom_point()
p.save("output.png", dpi=300)
```

`ggsave()` is deprecated and will be removed in a future version.

### `options()` context manager

Instead of `theme_set()` / `theme_get()` pairs for temporary changes, plotten provides a context manager:

```python
from plotten import options, theme_dark

with options(theme=theme_dark()):
    p.show()  # uses dark theme
# automatically reverts
```

## Smarter defaults

### `geom_bar()` auto-detects stat

In ggplot2, `geom_bar()` always counts and `geom_col()` uses raw values, requiring you to pick the right one.
In plotten, `geom_bar()` detects whether `y` is mapped:

```python
geom_bar()                      # no y → counts (like ggplot2 geom_bar)
geom_bar(mapping=aes(y="val"))  # y present → identity (like ggplot2 geom_col)
```

`geom_col()` is deprecated — `geom_bar()` handles both cases.

### `orientation="y"` instead of `coord_flip()`

ggplot2's `coord_flip()` swaps axes globally.
plotten supports per-geom horizontal orientation:

```python
geom_bar(orientation="y")       # horizontal bars
geom_boxplot(orientation="y")   # horizontal boxplots
geom_histogram(orientation="y") # horizontal histogram
```

`coord_flip()` is deprecated.

### `reverse=True` instead of `direction=-1`

Brewer scales use a boolean instead of an integer direction flag:

```python
# ggplot2: scale_color_brewer(direction = -1)
scale_color_brewer(reverse=True)
```

Similarly, `coord_polar()` uses `clockwise=True/False` instead of `direction=1/-1`.

### `aesthetic` parameter on color scales

All `scale_color_*` factories accept `aesthetic="fill"`, so you don't need separate `scale_fill_*` imports when you just want a different aesthetic target:

```python
scale_color_brewer("Set2", aesthetic="fill")  # acts as scale_fill_brewer
```

### `transform` parameter on position scales

Instead of separate `scale_x_log10()`, `scale_x_sqrt()` functions, you can use a single entry point:

```python
scale_x_continuous(transform="log10")
scale_y_continuous(transform=Transform.SQRT)
```

The standalone `scale_x_log10()` etc. still work.

## Typed return values

### `guides()` returns a `Guides` object

`guides()` returns a `Guides` instance (a `dict` subclass) instead of a plain dict, giving a clearer repr and type identity.

### `computed()` and `scaled()` aliases

`after_stat()` and `after_scale()` are available under more intuitive names:

```python
aes(y=computed("count"))   # same as after_stat("count")
aes(color=scaled("fill"))  # same as after_scale("fill")
```

## Facet label separator

`facet_grid()` with both `rows` and `cols` uses `" | "` as the strip label separator instead of ggplot2's `" ~ "`:

```
# ggplot2: "setosa ~ virginica"
# plotten: "setosa | virginica"
```

## Viridis palette names

Single-letter viridis option codes (`"A"` through `"E"`) are deprecated.
Use the full palette name instead:

```python
# Deprecated: scale_color_viridis("D")
scale_color_viridis("viridis")    # was "D"
scale_color_viridis("magma")      # was "A"
```

## DataFrame-agnostic

plotten works with any [narwhals](https://narwhals-dev.github.io/narwhals/)-supported DataFrame library (pandas, Polars, cuDF, Modin, PyArrow) without conversion.
ggplot2 requires R data frames.

## Notebook display

`Plot` objects have `_repr_png_`, `_repr_html_`, `_repr_mimebundle_`, and `_mime_` methods for automatic display in Jupyter, Marimo, and other notebook environments.
No explicit `print()` or `show()` call is needed.
