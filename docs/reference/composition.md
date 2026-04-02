# Composition

Tools for combining multiple plots into a single figure.

## Operators

Plots can be composed directly using Python operators — no extra package needed:

| Operator | Effect | Example |
|----------|--------|---------|
| `p1 \| p2` | Side by side (horizontal) | Two plots in one row |
| `p1 / p2` | Stacked (vertical) | Two plots in one column |
| `(p1 \| p2) / p3` | Combined layout | Two on top, one below |

```python
from plotten import ggplot, aes, geom_point, geom_histogram
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

scatter = ggplot(mpg, aes(x="displ", y="hwy")) + geom_point()
hist = ggplot(mpg, aes(x="hwy")) + geom_histogram()

# Side by side
scatter | hist

# Stacked vertically
scatter / hist
```

Add a shared annotation with `+`:

```python
from plotten import plot_annotation

(scatter | hist) + plot_annotation(title="Two views of MPG data")
```

## Plot grid

For more control over layout, use `plot_grid()` with explicit rows, columns, and widths.
Pass `guides="collect"` to suppress per-plot legends and draw a single shared legend instead.

```python
from plotten import plot_grid

plot_grid(p1, p2, p3, ncol=2, guides="collect")
```

::: plotten.plot_grid

## Annotations

Annotate a composed plot with a shared title, subtitle, caption, or automatic panel tags.

::: plotten.plot_annotation

## Inset plots

Embed a smaller plot inside a larger one at a specific position.

::: plotten.inset_element
