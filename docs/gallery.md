# Gallery

A cookbook-style showcase of plotten's capabilities.
Every image on this page is generated from the scripts in the documentation -- see [generate_images.py](https://github.com/briandconnelly/plotten/blob/main/docs/generate_images.py) for the full source.
For complete API details, refer to the [reference pages](reference/core.md).

---

## Geoms

Core geometric layers for building plots.

### Scatter plot

![Scatter plot colored by vehicle class](images/generated/geoms/point.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="class"))
        + geom_point(alpha=0.7)
        + labs(title="geom_point", x="Displacement (L)", y="Highway MPG")
    )
    ```

### Histogram

![Histogram of highway MPG](images/generated/geoms/histogram.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_histogram, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy"))
        + geom_histogram(bins=20, fill="#2ecc71", alpha=0.8)
        + labs(title="geom_histogram", x="Highway MPG", y="Count")
    )
    ```

### Overlaid densities

![Density curves by drive train](images/generated/geoms/density.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_density, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy", fill="drv"))
        + geom_density(alpha=0.5)
        + labs(title="geom_density", x="Highway MPG", y="Density")
    )
    ```

### Density ridges

![Ridge plot of highway MPG by class](images/generated/geoms/density_ridges.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_density_ridges, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy", y="class"))
        + geom_density_ridges(alpha=0.7)
        + labs(title="geom_density_ridges", x="Highway MPG")
    )
    ```

### Box plot

![Box plot by vehicle class](images/generated/geoms/boxplot.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_boxplot, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="class", y="hwy"))
        + geom_boxplot(fill="#3498db", alpha=0.7)
        + labs(title="geom_boxplot", x="Vehicle class", y="Highway MPG")
    )
    ```

### Violin + box overlay

![Violin with boxplot overlay](images/generated/gallery/violin_boxplot.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_violin, geom_boxplot, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="class", y="hwy"))
        + geom_violin(fill="#dfe6e9", alpha=0.7)
        + geom_boxplot(width=0.2, fill="#74b9ff", alpha=0.8)
        + labs(
            title="Highway MPG by vehicle class",
            subtitle="Violin + boxplot overlay",
            x="Vehicle class",
            y="Highway MPG",
        )
    )
    ```

### Hexagonal binning

![Hex bins of diamonds data](images/generated/geoms/hex.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_hex, labs
    from plotten.datasets import load_dataset

    diamonds = load_dataset("diamonds").drop("x", "y", "z")

    (
        ggplot(diamonds, aes(x="carat", y="price"))
        + geom_hex(bins=25)
        + labs(title="geom_hex", x="Carat", y="Price")
    )
    ```

### Heatmap with tiles

![Heatmap using geom_tile](images/generated/gallery/heatmap.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_tile, scale_fill_gradient2, labs

    # Build a correlation-style matrix
    heat_df = ...  # DataFrame with columns x, y, r

    (
        ggplot(heat_df, aes(x="x", y="y", fill="r"))
        + geom_tile()
        + scale_fill_gradient2(low="#2166ac", mid="#f7f7f7", high="#b2182b", midpoint=0)
        + labs(title="Heatmap with geom_tile + scale_fill_gradient2")
    )
    ```

### Label repelling

![Text repel avoiding overlaps](images/generated/geoms/text_repel.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, geom_text_repel, labs

    (
        ggplot(df, aes(x="x", y="y", label="name"))
        + geom_point(size=30, color="#2c3e50")
        + geom_text_repel()
        + labs(title="geom_text_repel")
    )
    ```

### Significance brackets

![Boxplot with significance annotation](images/generated/geoms/signif.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_boxplot, geom_signif, labs

    (
        ggplot(df, aes(x="group", y="value"))
        + geom_boxplot(fill="#3498db", alpha=0.6)
        + geom_signif(comparisons=[("Control", "Treatment")])
        + labs(title="geom_signif", x="Group", y="Value")
    )
    ```

---

## Statistical layers

Computed overlays that summarize or annotate data.

### ECDF

![Empirical CDF by drive train](images/generated/stats/ecdf.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, stat_ecdf, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy", color="drv"))
        + stat_ecdf()
        + labs(title="stat_ecdf", x="Highway MPG", y="ECDF")
    )
    ```

### Smooth fit with OLS

![OLS smooth over scatter](images/generated/geoms/smooth.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, geom_smooth, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(alpha=0.4)
        + geom_smooth(method="ols", color="#e74c3c")
        + labs(title="geom_smooth (OLS)", x="Displacement (L)", y="Highway MPG")
    )
    ```

### Confidence ellipse

![Ellipses around groups](images/generated/stats/ellipse.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, stat_ellipse, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point(alpha=0.5)
        + stat_ellipse()
        + labs(title="stat_ellipse", x="Displacement (L)", y="Highway MPG")
    )
    ```

### Correlation annotation

![Scatter with correlation label](images/generated/stats/cor.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, stat_cor, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(alpha=0.4)
        + stat_cor()
        + labs(title="stat_cor", x="Displacement (L)", y="Highway MPG")
    )
    ```

### Summary statistics

![Mean and SE by class](images/generated/stats/summary.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, stat_summary, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="class", y="hwy"))
        + stat_summary()
        + labs(title="stat_summary (mean +/- SE)", x="Vehicle class", y="Highway MPG")
    )
    ```

### Mathematical functions

![Sin and cos curves](images/generated/stats/function.png)

??? example "Code"
    ```python
    import numpy as np
    from plotten import ggplot, stat_function, labs

    (
        ggplot()
        + stat_function(fun=np.sin, xlim=(-2 * np.pi, 2 * np.pi), color="#e74c3c")
        + stat_function(fun=np.cos, xlim=(-2 * np.pi, 2 * np.pi), color="#3498db")
        + labs(title="stat_function (sin & cos)", x="x", y="y")
    )
    ```

---

## Scales

Control how data values map to visual properties.

### Viridis color scale

![Points colored with viridis](images/generated/scales/color_viridis.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, scale_color_viridis, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
        + geom_point(size=20, alpha=0.7)
        + scale_color_viridis()
        + labs(title="scale_color_viridis")
    )
    ```

### ColorBrewer palette

![Points with Set2 palette](images/generated/scales/color_brewer.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, scale_color_brewer, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point(size=20, alpha=0.7)
        + scale_color_brewer(palette="Set2")
        + labs(title="scale_color_brewer (Set2)")
    )
    ```

### Diverging gradient

![Diverging color gradient](images/generated/scales/color_gradient2.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, scale_color_gradient2, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="cty"))
        + geom_point(size=20, alpha=0.7)
        + scale_color_gradient2(low="#2166ac", mid="#f7f7f7", high="#b2182b", midpoint=20)
        + labs(title="scale_color_gradient2")
    )
    ```

### Size mapping

![Points sized by city MPG](images/generated/scales/size_continuous.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, scale_size_continuous, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", size="cty"))
        + geom_point(alpha=0.5)
        + scale_size_continuous()
        + labs(title="scale_size_continuous")
    )
    ```

### Hatch patterns

![Bars with hatch patterns](images/generated/scales/hatch_discrete.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_bar, scale_hatch_discrete, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="class", hatch="drv"))
        + geom_bar(alpha=0.7)
        + scale_hatch_discrete()
        + labs(title="scale_hatch_discrete", x="Vehicle class", y="Count")
    )
    ```

### Fill with viridis

![2D bins with viridis fill](images/generated/scales/fill_viridis.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_bin2d, scale_fill_viridis, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_bin2d(bins=15)
        + scale_fill_viridis()
        + labs(title="scale_fill_viridis", x="Displacement (L)", y="Highway MPG")
    )
    ```

---

## Facets and coordinates

Split data into panels or transform the coordinate system.

### facet_wrap

![Faceted scatter by drive train](images/generated/facets/wrap.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, facet_wrap, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(alpha=0.5)
        + facet_wrap("drv")
        + labs(title="facet_wrap", x="Displacement (L)", y="Highway MPG")
    )
    ```

### facet_grid

![Grid of panels by drive train and cylinders](images/generated/facets/grid.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, facet_grid, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(alpha=0.5)
        + facet_grid(rows="drv", cols="cyl")
        + labs(title="facet_grid (drv ~ cyl)", x="Displacement (L)", y="Highway MPG")
    )
    ```

### Polar coordinates

![Wind rose style polar chart](images/generated/coords/polar.png)

??? example "Code"
    ```python
    import polars as pl
    from plotten import ggplot, aes, geom_col, coord_polar, labs

    wind_df = pl.DataFrame({
        "direction": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        "speed": [12, 8, 15, 6, 10, 14, 9, 11],
    })

    (
        ggplot(wind_df, aes(x="direction", y="speed"))
        + geom_col(fill="#2980b9", alpha=0.8)
        + coord_polar()
        + labs(title="coord_polar")
    )
    ```

### Coordinate transform

![Scatter with sqrt and log10 axes](images/generated/coords/trans.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, coord_trans, labs
    from plotten.datasets import load_dataset

    diamonds = load_dataset("diamonds").drop("x", "y", "z")

    (
        ggplot(diamonds, aes(x="carat", y="price"))
        + geom_point(alpha=0.05, size=3)
        + coord_trans(x="sqrt", y="log10")
        + labs(title="coord_trans (sqrt x, log10 y)", x="Carat", y="Price")
    )
    ```

### Flipped coordinates

![Horizontal bar chart](images/generated/coords/flip.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_bar, coord_flip, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="class"))
        + geom_bar(fill="#3498db", alpha=0.8)
        + coord_flip()
        + labs(title="coord_flip", x="Vehicle class", y="Count")
    )
    ```

---

## Themes

Change the overall look of any plot by adding a theme.

### theme_minimal

![Minimal theme](images/generated/themes/minimal.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, labs, theme_minimal
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="class"))
        + geom_point(alpha=0.7)
        + theme_minimal()
        + labs(title="theme_minimal", x="Displacement (L)", y="Highway MPG")
    )
    ```

### theme_dark

![Dark theme](images/generated/themes/dark.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, labs, theme_dark
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="class"))
        + geom_point(alpha=0.7)
        + theme_dark()
        + labs(title="theme_dark", x="Displacement (L)", y="Highway MPG")
    )
    ```

### theme_tufte

![Tufte theme](images/generated/themes/tufte.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, labs, theme_tufte
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="class"))
        + geom_point(alpha=0.7)
        + theme_tufte()
        + labs(title="theme_tufte", x="Displacement (L)", y="Highway MPG")
    )
    ```

### theme_economist

![Economist theme](images/generated/themes/economist.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, labs, theme_economist
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="class"))
        + geom_point(alpha=0.7)
        + theme_economist()
        + labs(title="theme_economist", x="Displacement (L)", y="Highway MPG")
    )
    ```

---

## Gallery showcase

Multi-layer compositions that combine several plotten features.

### Faceted scatter with smooth

![Faceted scatter with OLS smooths](images/generated/gallery/scatter_smooth_facet.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, geom_smooth, facet_wrap, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy", color="drv"))
        + geom_point(alpha=0.6)
        + geom_smooth(method="ols")
        + facet_wrap("drv")
        + labs(
            title="Displacement vs. MPG by drive train",
            x="Displacement (L)",
            y="Highway MPG",
        )
    )
    ```

### Stacked histogram

![Stacked histogram by drive train](images/generated/gallery/stacked_histogram.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_histogram, position_stack, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy", fill="drv"))
        + geom_histogram(bins=20, alpha=0.5, position=position_stack())
        + labs(
            title="Stacked highway MPG by drive train",
            x="Highway MPG",
            y="Count",
        )
    )
    ```

### Ridge plot

![Ridge plot of highway MPG](images/generated/gallery/ridge_plot.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_density_ridges, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="hwy", y="class"))
        + geom_density_ridges(alpha=0.8)
        + labs(title="Highway MPG density ridges", x="Highway MPG")
    )
    ```

### Annotated scatter

![Scatter with smooth, correlation, and reference line](images/generated/gallery/annotated_scatter.png)

??? example "Code"
    ```python
    from plotten import ggplot, aes, geom_point, geom_smooth, geom_hline, stat_cor, labs
    from plotten.datasets import load_dataset

    mpg = load_dataset("mpg")

    (
        ggplot(mpg, aes(x="displ", y="hwy"))
        + geom_point(mapping=aes(color="class"), alpha=0.6)
        + geom_smooth(method="ols", color="#2c3e50")
        + stat_cor()
        + geom_hline(yintercept=25, linetype="dashed", color="#e74c3c", alpha=0.6)
        + labs(
            title="Annotated scatter: smooth + correlation + reference line",
            x="Displacement (L)",
            y="Highway MPG",
        )
    )
    ```
