# Bindable Aesthetics

Aesthetics are the visual properties of a plot — position, color, size, shape, and more.
In plotten, you control aesthetics in two ways: **mapping** them to data columns via `aes()`, or **setting** them to fixed values directly on a geom.
This guide covers both approaches, lists every available aesthetic, and shows which geoms support which aesthetics.

## How `aes()` mappings work

The `aes()` function creates an aesthetic mapping that tells plotten which columns in your data correspond to which visual properties.
Pass column names as strings:

```python
from plotten import ggplot, aes, geom_point
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
)
```

Here, `x="displ"` maps the `displ` column to the x-axis, `y="hwy"` maps `hwy` to the y-axis, and `color="drv"` maps the `drv` column to point color.
plotten automatically creates a scale and legend for each mapped aesthetic.

You can set global mappings in `ggplot()` and override or extend them in individual geom layers:

```python
from plotten import ggplot, aes, geom_point, geom_smooth

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(aes(color="drv"))          # color only for points
    + geom_smooth(aes(linetype="drv"))       # linetype only for smooth
)
```

## Setting vs mapping

This is one of the most common sources of confusion.
The rule is simple:

- **Inside `aes()`** = map a data column to an aesthetic (creates a scale and legend)
- **Outside `aes()`** = set a constant value for an aesthetic (no legend)

```python
# MAPPING: color varies by the "drv" column, legend is created
ggplot(mpg, aes(x="displ", y="hwy")) + geom_point(aes(color="drv"))

# SETTING: all points are red, no legend
ggplot(mpg, aes(x="displ", y="hwy")) + geom_point(color="red")
```

!!! warning "A common mistake"

    Writing `aes(color="red")` does **not** make points red.
    It tells plotten to look for a column named `"red"` in your data.
    To set a fixed color, pass it directly to the geom: `geom_point(color="red")`.

Setting works for any aesthetic that accepts a constant value:

```python
(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(color="steelblue", size=3, alpha=0.5, shape="D")
)
```

## Available aesthetics

The full list of aesthetics you can use in `aes()`:

| Aesthetic | Description | Example values |
|-----------|-------------|----------------|
| `x` | Horizontal position | Column name |
| `y` | Vertical position | Column name |
| `color` / `colour` | Outline or line color | Column name or hex color |
| `fill` | Fill color for bars, areas, etc. | Column name or hex color |
| `size` | Point size or line thickness | Column name or numeric |
| `alpha` | Transparency (0 = invisible, 1 = opaque) | Column name or float |
| `shape` | Point marker shape | Column name or marker code |
| `linetype` | Line dash pattern | Column name or style string |
| `linewidth` | Line width (separate from `size`) | Column name or numeric |
| `hatch` | Hatch fill pattern | Column name or pattern string |
| `label` | Text label content | Column name |
| `group` | Grouping variable (no legend) | Column name |

Additional positional aesthetics used by specific geoms:

| Aesthetic | Used by |
|-----------|---------|
| `ymin`, `ymax` | `geom_ribbon`, `geom_errorbar`, `geom_crossbar`, `geom_linerange`, `geom_pointrange` |
| `xmin`, `xmax` | `geom_rect`, `geom_errorbarh` |
| `xend`, `yend` | `geom_segment`, `geom_curve` |
| `z` | `geom_contour`, `geom_contour_filled` |
| `angle` | `geom_spoke` |
| `radius` | `geom_spoke` |

!!! tip "colour is an alias for color"

    You can use `colour` anywhere you would use `color`.
    This matches the ggplot2 convention: `aes(colour="class")` works identically to `aes(color="class")`.

## Aesthetics by geom

The table below shows which aesthetics each common geom supports.
Required aesthetics are marked with **bold**.
Optional aesthetics are marked with a dot.

| Geom | x | y | color | fill | size | alpha | shape | linetype | linewidth | hatch | label | group |
|------|---|---|-------|------|------|-------|-------|----------|-----------|-------|-------|-------|
| `geom_point` | **x** | **y** | . | . | . | . | . | | | | | . |
| `geom_line` | **x** | **y** | . | | . | . | | . | . | | | . |
| `geom_bar` | **x** | | . | . | | . | | . | . | . | | . |
| `geom_col` | **x** | **y** | . | . | | . | | . | . | . | | . |
| `geom_histogram` | **x** | | . | . | | . | | . | . | . | | . |
| `geom_density` | **x** | | . | . | . | . | | . | . | | | . |
| `geom_boxplot` | **x** | **y** | . | . | . | . | | . | . | | | . |
| `geom_violin` | **x** | **y** | . | . | | . | | . | . | | | . |
| `geom_area` | **x** | **y** | . | . | | . | | . | . | | | . |
| `geom_ribbon` | **x** | | . | . | | . | | . | . | | | . |
| `geom_text` | **x** | **y** | . | | . | . | | | | | . | . |
| `geom_segment` | **x** | **y** | . | | . | . | | . | . | | | . |

!!! note

    `geom_ribbon` requires `ymin` and `ymax` in `aes()` instead of `y`.
    `geom_segment` requires `xend` and `yend` in `aes()` in addition to `x` and `y`.

## Computed aesthetics

Some geoms compute new variables during the statistical transformation step.
You can map these computed variables using `after_stat()`.

### `after_stat()`

Use `after_stat()` to reference a variable computed by the stat layer:

```python
from plotten import ggplot, aes, geom_histogram, after_stat
from plotten.datasets import load_dataset

diamonds = load_dataset("diamonds")

# Default histogram uses count on the y-axis.
# Use after_stat("density") to show density instead:
(
    ggplot(diamonds, aes(x="price", y=after_stat("density")))
    + geom_histogram(bins=50, fill="steelblue")
)
```

Common computed variables:

- `after_stat("count")` — number of observations in each bin
- `after_stat("density")` — density estimate (integrates to 1)
- `after_stat("ncount")` — count normalized to a maximum of 1
- `after_stat("ndensity")` — density normalized to a maximum of 1

### `after_scale()`

Use `after_scale()` to reference an aesthetic value after it has been mapped through its scale.
This is useful for deriving one aesthetic from another:

```python
from plotten import ggplot, aes, geom_point, after_scale

# Make the fill a lighter version of the mapped color
(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point(aes(fill=after_scale("color")), shape="o", size=4)
)
```

### `stage()`

The `stage()` function lets you specify different mappings for different stages of the rendering pipeline.
It accepts up to three keyword arguments:

```python
from plotten import ggplot, aes, geom_bar, stage, after_stat

penguins = load_dataset("penguins")

(
    ggplot(penguins, aes(x="species"))
    + geom_bar(
        aes(
            y=stage(after_stat="count"),
            fill="species",
        )
    )
)
```

The three stages are:

1. `start` — the raw column name (used during data mapping)
2. `after_stat` — a variable computed by the stat (used after statistical transformation)
3. `after_scale` — a variable after scale mapping (used after scales are applied)

`stage()` returns the latest-stage mapping you provide.

## The `interaction()` helper

When you need to group or color by the combination of two or more variables, use `interaction()`:

```python
from plotten import ggplot, aes, geom_line, interaction
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

# Group lines by the combination of drv and cyl
(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_line(aes(color=interaction("drv", "cyl")))
)
```

The `interaction()` function requires at least two column names.
It concatenates the values with a `.` separator (e.g., `"4.4"`, `"f.6"`) to create a single grouping variable.

!!! tip

    `interaction()` is equivalent to ggplot2's `interaction()` function.
    Use it whenever you need to distinguish groups defined by multiple categorical variables.

## Putting it all together

Here is a more complete example combining several aesthetic techniques:

```python
from plotten import (
    ggplot, aes, geom_point, geom_smooth,
    labs, theme_minimal, scale_color_brewer,
)
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(
        aes(color="drv", size="cyl"),
        alpha=0.6,
    )
    + geom_smooth(method="loess", color="black", linewidth=1)
    + scale_color_brewer(palette="Set2")
    + labs(
        title="Engine displacement vs. highway MPG",
        x="Displacement (L)",
        y="Highway MPG",
        color="Drive",
        size="Cylinders",
    )
    + theme_minimal()
)
```

In this example:

- `x` and `y` are mapped globally in `ggplot()`
- `color` is mapped to `"drv"` only in `geom_point()`
- `size` is mapped to `"cyl"` only in `geom_point()`
- `alpha` is set to a constant `0.6` (not mapped)
- `color` and `linewidth` are set to constants in `geom_smooth()`
- `scale_color_brewer()` controls how the `color` mapping is rendered
- `labs()` provides human-readable labels for each aesthetic
