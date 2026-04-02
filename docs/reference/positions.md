# Positions

Position adjustments control how overlapping geoms are arranged within a plot.
When multiple observations share the same x (or y) value, a position adjustment determines whether they stack, dodge side-by-side, jitter randomly, or remain in place.

Pass a position to any geom via the `position` parameter:

```python
geom_bar(position=position_dodge(width=0.9))
```

## Identity

No adjustment — observations are plotted at their exact data positions.
This is the default for most geoms except bar charts.

::: plotten.position_identity

## Dodge

Place overlapping groups side-by-side within the same x position.

![position_dodge](../images/generated/positions/dodge.png)

::: plotten.position_dodge

## Dodge2

A variant of dodge that leaves a small gap between items and does not require groups to have equal size.

::: plotten.position_dodge2

## Jitter

Add a small amount of random noise to prevent overplotting in dense scatter plots.

![position_jitter](../images/generated/positions/jitter.png)

::: plotten.position_jitter

## Jitter + Dodge

Combine dodging and jittering — useful for grouped categorical plots where you want both separation and spread.

![position_jitterdodge](../images/generated/positions/jitterdodge.png)

::: plotten.position_jitterdodge

## Nudge

Shift all points by a fixed offset — commonly used with `geom_text` to move labels away from their data points.

![position_nudge](../images/generated/positions/nudge.png)

::: plotten.position_nudge

## Stack

Stack overlapping items on top of each other (absolute values).
This is the default position for `geom_bar` and `geom_area`.

![position_stack](../images/generated/positions/stack.png)

::: plotten.position_stack

## Fill

Stack and normalize to 100% — shows proportional composition rather than absolute values.

![position_fill](../images/generated/positions/fill.png)

::: plotten.position_fill

## Beeswarm

Arrange points in a beeswarm layout that avoids overlap while staying as close to the center as possible.

![position_beeswarm](../images/generated/positions/beeswarm.png)

::: plotten.position_beeswarm
