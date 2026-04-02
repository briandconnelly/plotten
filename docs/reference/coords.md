# Coordinates

Coordinate systems control how position aesthetics are mapped to the plane of the plot.

![coord_cartesian](../images/generated/coords/cartesian.png)

::: plotten.coord_cartesian

![coord_flip](../images/generated/coords/flip.png)

::: plotten.coord_flip

![coord_equal](../images/generated/coords/equal.png)

::: plotten.coord_equal

::: plotten.coord_fixed

![coord_polar](../images/generated/coords/polar.png)

::: plotten.coord_polar

## Transformed coordinates

Apply mathematical transformations to axes without changing the underlying data.
Pass transform names as strings to the `x` and `y` parameters.

Available transforms: `"log10"`, `"sqrt"`, `"reverse"`, `"exp"`, `"reciprocal"`, `"logit"`.

```python
from plotten import ggplot, aes, geom_point, coord_trans
from plotten.datasets import load_dataset

diamonds = load_dataset("diamonds").drop("x", "y", "z")

(
    ggplot(diamonds, aes(x="carat", y="price"))
    + geom_point(alpha=0.05, size=3)
    + coord_trans(x="sqrt", y="log10")
)
```

![coord_trans](../images/generated/coords/trans.png)

::: plotten.coord_trans
