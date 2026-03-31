# ggplot2 Migration Guide

plotten mirrors the ggplot2 API as closely as possible.
If you know ggplot2, you already know most of plotten.
This guide shows side-by-side R and Python code for common operations and highlights the key differences.

## What's the same

The vast majority of the API is intentionally identical:

- Layer-based grammar: `ggplot()` + `geom_*()` + `scale_*()` + `theme_*()`
- The `+` operator for composing plot elements
- The same geom, stat, scale, coord, and facet names
- `labs()` for axis and legend labels
- `theme()` with element functions (`element_text()`, `element_line()`, etc.)
- `colour` works as an alias for `color` everywhere

## Core concepts

### Basic scatter plot

=== "R"

    ```r
    library(ggplot2)

    ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point()
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    ggplot(mpg, aes(x="displ", y="hwy")) + geom_point()
    ```

!!! note "Column names are strings"

    The biggest syntax difference: ggplot2 uses bare (unquoted) column names, plotten uses quoted strings.
    `aes(x = displ)` in R becomes `aes(x="displ")` in Python.

### Color mapping and labels

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy, colour = drv)) +
      geom_point() +
      labs(
        title = "Engine Displacement vs. Highway MPG",
        x = "Displacement (L)",
        y = "Highway MPG",
        colour = "Drive"
      )
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, labs

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point()
        + labs(
            title="Engine Displacement vs. Highway MPG",
            x="Displacement (L)",
            y="Highway MPG",
            color="Drive",
        )
    )
    ```

!!! tip

    Both `colour` and `color` work in plotten — use whichever you prefer.

### Saving a plot

=== "R"

    ```r
    p <- ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point()

    ggsave("scatter.png", width = 8, height = 5, dpi = 300)
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, ggsave

    p = ggplot(mpg, aes(x="displ", y="hwy")) + geom_point()

    ggsave(p, "scatter.png", width=8, height=5, dpi=300)
    ```

!!! warning "ggsave takes the plot as the first argument"

    In ggplot2, `ggsave()` defaults to saving the last plot.
    In plotten, the plot is always the first argument: `ggsave(plot, filename)`.
    There is no implicit "last plot" concept.

## Scales

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy, colour = drv)) +
      geom_point() +
      scale_colour_brewer(palette = "Set2") +
      scale_x_log10() +
      scale_y_continuous(limits = c(10, 50))
    ```

=== "Python"

    ```python
    from plotten import (
        ggplot, aes, geom_point,
        scale_color_brewer, scale_x_log10, scale_y_continuous,
    )

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point()
        + scale_color_brewer(palette="Set2")
        + scale_x_log10()
        + scale_y_continuous(limits=(10, 50))
    )
    ```

Scale names are the same, with both `color` and `colour` spellings available.
Use Python tuples instead of R's `c()` for limits and ranges.

## Faceting

### `facet_wrap`

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point() +
      facet_wrap(~class, ncol = 3)
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, facet_wrap

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point()
        + facet_wrap("class", ncol=3)
    )
    ```

!!! note "No formula syntax"

    ggplot2 uses formula syntax: `facet_wrap(~class)`.
    plotten uses a string column name: `facet_wrap("class")`.

### `facet_grid`

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point() +
      facet_grid(drv ~ cyl)
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, facet_grid

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point()
        + facet_grid(rows="drv", cols="cyl")
    )
    ```

In plotten, `facet_grid()` uses explicit `rows` and `cols` keyword arguments instead of the `rows ~ cols` formula syntax.

## Themes

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point() +
      theme_minimal() +
      theme(
        plot.title = element_text(size = 20, face = "bold"),
        axis.text.x = element_text(angle = 45, hjust = 1),
        panel.grid.minor = element_blank()
      )
    ```

=== "Python"

    ```python
    from plotten import (
        ggplot, aes, geom_point, theme_minimal,
        theme, element_text, element_blank,
    )

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point()
        + theme_minimal()
        + theme(
            plot_title=element_text(size=20, weight="bold"),
            axis_text_x=element_text(rotation=45, ha="right"),
            panel_grid_minor=element_blank(),
        )
    )
    ```

Key naming differences in theme:

| ggplot2 | plotten | Notes |
|---------|---------|-------|
| `plot.title` | `plot_title` | Dots become underscores |
| `axis.text.x` | `axis_text_x` | Same pattern |
| `panel.grid.minor` | `panel_grid_minor` | Same pattern |
| `face = "bold"` | `weight="bold"` | Parameter name differs |
| `angle = 45` | `rotation=45` | Parameter name differs |
| `hjust = 1` | `ha="right"` or `hjust=1` | Both work in plotten |

For a full guide on theming, see [Theming Deep Dive](theming.md).

## Composition (patchwork)

In R, the patchwork package uses `|` for side-by-side and `/` for stacking.
plotten uses the same operators natively:

=== "R"

    ```r
    library(patchwork)

    p1 <- ggplot(mpg, aes(x = displ, y = hwy)) + geom_point()
    p2 <- ggplot(mpg, aes(x = cty, y = hwy)) + geom_point()

    p1 | p2               # side by side
    p1 / p2               # stacked
    (p1 | p2) / p3        # complex layout

    (p1 | p2) + plot_annotation(title = "Combined plots")
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, plot_annotation

    p1 = ggplot(mpg, aes(x="displ", y="hwy")) + geom_point()
    p2 = ggplot(mpg, aes(x="cty", y="hwy")) + geom_point()

    p1 | p2               # side by side
    p1 / p2               # stacked
    (p1 | p2) / p3        # complex layout

    (p1 | p2) + plot_annotation(title="Combined plots")
    ```

The `|` and `/` operators work directly on `Plot` objects — no extra package needed.
See the [Composition reference](../reference/composition.md) for more details.

## Statistical layers

=== "R"

    ```r
    ggplot(mpg, aes(x = displ, y = hwy)) +
      geom_point() +
      geom_smooth(method = "loess", se = TRUE)
    ```

=== "Python"

    ```python
    from plotten import ggplot, aes, geom_point, geom_smooth

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point()
        + geom_smooth(method="loess", se=True)
    )
    ```

Stat functions use the same names and parameters.

## Key differences summary

| Aspect | ggplot2 (R) | plotten (Python) |
|--------|-------------|------------------|
| Column names in `aes()` | Bare names: `aes(x = displ)` | Strings: `aes(x="displ")` |
| Facet syntax | Formula: `facet_wrap(~class)` | String: `facet_wrap("class")` |
| Facet grid | `facet_grid(drv ~ cyl)` | `facet_grid(rows="drv", cols="cyl")` |
| `ggsave()` | `ggsave(path)` (uses last plot) | `ggsave(plot, path)` (explicit plot) |
| Theme properties | Dots: `plot.title` | Underscores: `plot_title` |
| Font weight | `face = "bold"` | `weight="bold"` |
| Text rotation | `angle = 45` | `rotation=45` |
| Boolean values | `TRUE` / `FALSE` | `True` / `False` |
| NULL | `NULL` | `None` |
| Vectors | `c(10, 50)` | `(10, 50)` (tuples) |
| String operator | `+` with `paste()` | Python string operations |
| DataFrame | data.frame / tibble | Any narwhals-supported DataFrame |
| Composition | patchwork package | Built-in `\|` and `/` operators |

## DataFrame library agnostic

Unlike ggplot2 which is tightly coupled to R data frames and tibbles, plotten works with any DataFrame library supported by [narwhals](https://narwhals-dev.github.io/narwhals/):

- **pandas**
- **Polars**
- **cuDF**
- **Modin**
- **PyArrow tables**

Just pass your DataFrame directly — no conversion needed:

=== "Polars"

    ```python
    import polars as pl
    from plotten import ggplot, aes, geom_point

    df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    ggplot(df, aes(x="x", y="y")) + geom_point()
    ```

=== "pandas"

    ```python
    import pandas as pd
    from plotten import ggplot, aes, geom_point

    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    ggplot(df, aes(x="x", y="y")) + geom_point()
    ```

For more details, see [Working with DataFrames](dataframes.md).
