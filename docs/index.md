# plotten

**A grammar-of-graphics plotting library for Python -- ggplot2's API, Python's ecosystem.**

If you've used ggplot2 in R, plotten will feel immediately familiar.
If you haven't, the grammar of graphics is a composable, layered approach to building charts: you describe *what* your data is and *how* it should be encoded visually, and the library handles the rest.

```python
from plotten import ggplot, aes, geom_point, geom_smooth, labs
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

(
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + geom_smooth(method="ols")
    + labs(
        title="Engine displacement vs. highway MPG",
        subtitle="Seven vehicle classes, model years 1999-2008",
        caption="Source: ggplot2::mpg",
        x="Displacement (L)",
        y="Highway MPG",
    )
)
```

![Hero plot](images/hero.png)

---

## Highlights

- **45+ geometry layers** -- points, lines, bars, histograms, density, boxplots, violins, ridgeplots, contours, hex bins, and more
- **50+ scales** -- color, fill, size, shape, alpha, linetype, linewidth, hatch, and position with manual, identity, Brewer, viridis, gradient, and binned variants
- **Full faceting** -- `facet_wrap()` and `facet_grid()` with free/fixed scales and custom labellers
- **12 built-in themes** -- from `theme_minimal` to `theme_tufte` to `theme_economist`, plus full customization via `theme()`
- **Plot composition** -- combine plots with `|` and `/`, or use `plot_grid()` for arbitrary layouts
- **Works with pandas and polars** -- via [narwhals](https://github.com/narwhals-dev/narwhals), no conversion needed
- **Publication-quality export** -- `ggsave()` with 300 DPI default, size in inches/cm/mm
- **Accessibility auditing** -- `accessibility_report()` checks colorblind safety, contrast ratios, and font sizes
- **Helpful error messages** -- typo suggestions for column names, geom parameters, and theme properties
- **Vega-Lite export** -- `to_vegalite(plot)` and `to_html(plot)` for web output

[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[Browse the gallery](gallery.md){ .md-button }
