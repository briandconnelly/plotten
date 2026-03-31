# Theming Deep Dive

plotten's theme system gives you full control over every non-data element of your plot: backgrounds, grid lines, fonts, axis labels, legends, and more.
This guide covers built-in themes, the element system for fine-grained customization, and how to create reusable themes.

## Overview

Every plot has a theme that controls its visual appearance.
You can:

1. Apply a **built-in theme** for a complete look with a single function call
2. Use `theme()` to override individual properties
3. Combine both — start with a built-in theme and tweak specific elements
4. Set a **global default** so all plots share the same style

Themes compose with the `+` operator, just like layers and scales:

```python
from plotten import ggplot, aes, geom_point, theme_minimal, theme
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
    + theme_minimal()
    + theme(title_size=20, legend_position="bottom")
)
```

## Built-in themes

plotten ships with 13 built-in themes.
Each is a function that returns a complete `Theme` object.

| Theme | Description | Best for |
|-------|-------------|----------|
| `theme_default()` | Modern, clean look with subtle grid and no axis lines. plotten's default. | General-purpose use |
| `theme_grey()` / `theme_gray()` | Classic ggplot2 grey background with white grid lines. | Matching ggplot2's default style |
| `theme_bw()` | White background with a thin panel border and grid lines. | Print-friendly figures |
| `theme_minimal()` | White background, grid lines, no axis lines or panel border. | Clean, distraction-free plots |
| `theme_classic()` | White background with axis lines, no grid. Mimics base R. | Publication figures, traditional style |
| `theme_dark()` | Dark grey background with muted grid lines. | Presentations on dark backgrounds |
| `theme_light()` | Light grey axis lines and border. Emphasizes data. | Busy plots with many facets |
| `theme_linedraw()` | Black lines on a white background. High contrast. | Black-and-white printing |
| `theme_void()` | Completely blank — no axes, grid, or background. | Maps, diagrams, annotations |
| `theme_tufte()` | Minimal design inspired by Edward Tufte's principles. | Data-ink maximization |
| `theme_economist()` | Style inspired by *The Economist* magazine. | Business presentations |
| `theme_538()` | Style inspired by FiveThirtyEight. | Data journalism |
| `theme_seaborn()` | Style matching seaborn's default aesthetic. | Familiarity for seaborn users |

```python
from plotten import ggplot, aes, geom_point, theme_tufte
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + theme_tufte()
)
```

!!! note

    `theme_grey()` and `theme_gray()` are aliases for the same theme, as are `scale_color_grey()` and `scale_color_gray()`.

## The `theme()` function

The `theme()` function creates a partial theme that overrides specific properties.
It accepts any valid `Theme` field as a keyword argument.

### Simple scalar properties

Many theme properties are simple scalars — numbers, strings, or booleans:

```python
from plotten import theme

# Adjust text sizes and font
theme(
    title_size=18,
    label_size=12,
    tick_size=10,
    font_family="serif",
)

# Control grid visibility
theme(
    grid_major_x=True,
    grid_major_y=True,
    grid_minor_x=False,
    grid_minor_y=False,
)

# Panel and background colors
theme(
    background="#f5f5f5",
    panel_background="#ffffff",
    grid_color="#cccccc",
)
```

### Legend position

Move the legend with the `legend_position` property:

```python
from plotten import ggplot, aes, geom_point, theme
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

# Legend at the bottom
(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
    + theme(legend_position="bottom")
)

# Legend inside the plot area (x, y in 0-1 coordinates)
(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
    + theme(legend_position=(0.85, 0.85))
)

# Remove the legend entirely
(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
    + theme(legend_position="none")
)
```

Valid positions: `"right"` (default), `"left"`, `"top"`, `"bottom"`, `"none"`, or a `(x, y)` tuple.

## The element system

For fine-grained control, plotten provides four element types that map to ggplot2's element system.
Use these with the element override fields on `theme()`.

### `element_text()`

Controls text rendering — titles, labels, tick marks, and legend text.

```python
from plotten import theme, element_text

theme(
    plot_title=element_text(
        size=20,
        color="#1a1a1a",
        weight="bold",
        family="Georgia",
    ),
    axis_text_x=element_text(
        rotation=45,
        ha="right",
        size=9,
    ),
    axis_title=element_text(
        size=13,
        color="#333333",
    ),
)
```

`element_text()` parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `size` | `float` or `Rel` | Font size in points, or relative via `rel()` |
| `color` | `str` | Text color (hex, named color) |
| `family` | `str` | Font family name |
| `weight` | `str` | Font weight: `"normal"`, `"bold"`, `"semibold"`, etc. |
| `style` | `str` | Font style: `"normal"`, `"italic"` |
| `rotation` | `float` | Rotation angle in degrees |
| `ha` / `hjust` | `str` or `float` | Horizontal justification: `"left"`, `"center"`, `"right"`, or 0-1 |
| `va` / `vjust` | `str` or `float` | Vertical justification: `"bottom"`, `"center"`, `"top"`, or 0-1 |

### `element_line()`

Controls line rendering — grid lines, axis lines, and tick marks.

```python
from plotten import theme, element_line

theme(
    panel_grid_major=element_line(
        color="#e0e0e0",
        size=0.5,
        linetype="dashed",
    ),
    axis_ticks=element_line(
        color="#333333",
        size=0.8,
    ),
)
```

`element_line()` parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `color` | `str` | Line color |
| `size` | `float` | Line width in points |
| `linetype` | `str` | Dash pattern: `"solid"`, `"dashed"`, `"dotted"`, `"dashdot"` |

### `element_rect()`

Controls rectangle rendering — panel backgrounds, legend keys, and plot backgrounds.

```python
from plotten import theme, element_rect

theme(
    panel_border=element_rect(
        fill="none",
        color="#999999",
        size=0.5,
    ),
    legend_key=element_rect(
        fill="#f0f0f0",
        color="none",
    ),
)
```

`element_rect()` parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `fill` | `str` | Fill color |
| `color` | `str` | Border color |
| `size` | `float` | Border width in points |

### `element_blank()`

Removes an element entirely.
Takes no arguments.

```python
from plotten import theme, element_blank

# Remove the panel grid and axis ticks
theme(
    panel_grid_major=element_blank(),
    panel_grid_minor=element_blank(),
    axis_ticks=element_blank(),
)
```

## `margin()` and `rel()` helpers

### `margin()`

The `margin()` function specifies padding around plot elements.
Use it with the `plot_margin` theme property:

```python
from plotten import theme, margin

# Add margin around the plot (top, right, bottom, left)
theme(
    plot_margin=margin(top=0.1, right=0.05, bottom=0.1, left=0.05, unit="npc"),
)

# Margins in physical units
theme(
    plot_margin=margin(top=1, right=1, bottom=1, left=1, unit="cm"),
)
```

Supported units: `"npc"` (normalized parent coordinates, 0-1), `"in"` (inches), `"cm"`, `"mm"`.

### `rel()`

The `rel()` function creates a relative size multiplier.
Use it anywhere `element_text()` accepts a `size`:

```python
from plotten import theme, element_text, rel

# Title 20% larger than default, caption 20% smaller
theme(
    plot_title=element_text(size=rel(1.2)),
    plot_caption=element_text(size=rel(0.8)),
)
```

## Common customization recipes

### Rotate axis labels

```python
from plotten import ggplot, aes, geom_bar, theme, element_text
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="manufacturer"))
    + geom_bar(fill="steelblue")
    + theme(axis_text_x=element_text(rotation=45, ha="right"))
)
```

### Style the title and subtitle

```python
from plotten import ggplot, aes, geom_point, labs, theme, element_text

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(
        title="Engine Displacement vs. Highway MPG",
        subtitle="Data from the EPA fuel economy dataset",
    )
    + theme(
        plot_title=element_text(size=18, weight="bold", color="#1a1a1a"),
        plot_subtitle=element_text(size=13, color="#666666"),
    )
)
```

### Customize grid lines

```python
from plotten import theme, element_line, element_blank

# Horizontal grid only (good for bar charts)
theme(
    panel_grid_major_x=element_blank(),
    panel_grid_major_y=element_line(color="#e0e0e0", size=0.3),
    panel_grid_minor=element_blank(),
)
```

### Style the legend

```python
from plotten import theme, element_text, element_rect

theme(
    legend_position="bottom",
    legend_title_element=element_text(size=11, weight="bold"),
    legend_text_element=element_text(size=10),
    legend_key=element_rect(fill="none", color="none"),
)
```

### Facet strip styling

```python
from plotten import theme, element_text

theme(
    strip_text=element_text(size=11, weight="bold", color="#333333"),
    strip_background="#f0f0f0",
)
```

## Creating a custom reusable theme

Define a function that returns theme additions.
This makes it easy to share a consistent style across plots:

```python
from plotten import (
    theme_minimal, theme, element_text, element_line,
    element_blank, element_rect, margin,
)


def theme_corporate():
    """Corporate house style."""
    return (
        theme_minimal()
        + theme(
            font_family="Helvetica",
            title_size=16,
            title_weight="bold",
            title_color="#2c3e50",
            subtitle_color="#7f8c8d",
            label_size=11,
            tick_size=10,
            panel_grid_major=element_line(color="#ecf0f1", size=0.3),
            panel_grid_minor=element_blank(),
            axis_ticks=element_line(color="#bdc3c7", size=0.5),
            legend_position="bottom",
            plot_margin=margin(top=0.05, right=0.03, bottom=0.05, left=0.03),
        )
    )
```

Use it like any built-in theme:

```python
from plotten import ggplot, aes, geom_point
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
    + geom_point()
    + theme_corporate()
)
```

## Google Fonts

plotten can download and register fonts from Google Fonts.
Use `register_google_font()` to fetch a font, then reference it by family name:

```python
from plotten import register_google_font, theme, element_text

# Download and register the Lato font family
register_google_font("Lato")

# Use it in a theme
theme(
    font_family="Lato",
    plot_title=element_text(family="Lato", weight="bold"),
)
```

Fonts are cached locally in `~/.cache/plotten/fonts/` (or `$XDG_CACHE_HOME/plotten/fonts/`) so subsequent calls are fast.
All available weights are downloaded automatically.

You can also register local font files with `register_font()`:

```python
from plotten import register_font

name = register_font("/path/to/CustomFont.ttf")
# name is the font family string to use in element_text(family=name)
```

!!! tip

    Use `available_fonts()` to see all font families currently registered with matplotlib, including any you have added.

## Global defaults

### `theme_set()`

Set a global default theme that applies to every plot in the session:

```python
from plotten import theme_set, theme_minimal

# All subsequent plots use theme_minimal() as their base
theme_set(theme_minimal())
```

`theme_set()` returns the previous global theme, so you can restore it later:

```python
from plotten import theme_set, theme_minimal, theme_default

old = theme_set(theme_minimal())
# ... create plots with minimal theme ...
theme_set(old)  # restore previous theme
```

### `theme_get()`

Retrieve the current global default theme:

```python
from plotten import theme_get

current = theme_get()
print(current.font_family)
```

### `theme_update()`

Update the global theme incrementally without replacing it entirely:

```python
from plotten import theme_update

# Bump up the title size globally
theme_update(title_size=18, font_family="serif")
```

`theme_update()` returns the updated theme.
It is equivalent to `theme_set(theme_get() + theme(...))`.

## Composing themes

Themes compose with `+`.
Later additions override earlier ones:

```python
from plotten import theme_bw, theme

# Start with theme_bw, then override the legend and grid
my_theme = (
    theme_bw()
    + theme(legend_position="bottom")
    + theme(grid_minor_x=False, grid_minor_y=False)
)
```

When a complete theme (one of the built-in theme functions) is added, it replaces the current theme entirely.
Partial themes created with `theme()` only override the fields they specify.

```python
from plotten import ggplot, aes, geom_point, theme_minimal, theme_dark, theme

# theme_dark() replaces everything, then theme() modifies it
(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + theme_dark()
    + theme(title_size=20)
)
```

## Element override hierarchy

plotten's theme fields follow a hierarchy similar to ggplot2.
More specific fields override more general ones:

1. `axis_text` — applies to all axis tick labels
2. `axis_text_x` — overrides `axis_text` for the x-axis only
3. `axis_text_x_bottom` — overrides `axis_text_x` for the bottom x-axis only

The same pattern applies to `axis_title`, `axis_ticks`, `axis_line`, `panel_grid`, and `strip_text`.
This lets you set a base style and selectively override it for specific axes or positions.

```python
from plotten import theme, element_text, element_blank

theme(
    axis_text=element_text(size=10, color="#333333"),       # base
    axis_text_x=element_text(rotation=45, ha="right"),      # x-axis override
    axis_text_y=element_blank(),                             # hide y tick labels
)
```

For the complete list of theme fields, see the [Themes reference](../reference/themes.md).
