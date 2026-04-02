# Recipes

High-level constructors for common chart patterns.
Each recipe returns a fully configured `Plot` that can be further customized with `+`.

## Waterfall chart

Visualize cumulative effects of sequential positive and negative values — useful for financial statements, budget breakdowns, and contribution analyses.

![Waterfall chart](../images/generated/recipes/waterfall.png)

::: plotten.plot_waterfall

## Dumbbell chart

Compare two values per category with a connecting segment — ideal for showing changes between two time periods or paired measurements.

![Dumbbell chart](../images/generated/recipes/dumbbell.png)

::: plotten.plot_dumbbell

## Lollipop chart

A cleaner alternative to bar charts that uses a dot-and-stem to show a single value per category, reducing visual clutter.

![Lollipop chart](../images/generated/recipes/lollipop.png)

::: plotten.plot_lollipop

## Slope chart

Connect paired observations across two (or more) conditions to highlight trends and rank changes between groups.

![Slope chart](../images/generated/recipes/slope.png)

::: plotten.plot_slope

## Forest plot

Display effect sizes with confidence intervals — the standard visualization for meta-analyses and regression coefficient summaries.

![Forest plot](../images/generated/recipes/forest.png)

::: plotten.plot_forest

## Waffle chart

Show proportions as a grid of colored squares — a more readable alternative to pie charts for part-to-whole relationships.

![Waffle chart](../images/generated/recipes/waffle.png)

::: plotten.plot_waffle
