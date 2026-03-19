"""Demonstrate geom_spoke for wind/flow vector fields."""

import math

import polars as pl

from plotten import aes, geom_spoke, ggplot, labs

# Grid of vectors
xs = []
ys = []
angles = []
radii = []
for i in range(5):
    for j in range(5):
        xs.append(float(i))
        ys.append(float(j))
        angles.append(math.atan2(j - 2, i - 2))
        radii.append(0.4)

df = pl.DataFrame({"x": xs, "y": ys, "angle": angles, "radius": radii})

plot = (
    ggplot(df, aes(x="x", y="y", angle="angle", radius="radius"))
    + geom_spoke(arrow=True, color="steelblue")
    + labs(title="Vector Field with geom_spoke", x="X", y="Y")
)

plot.save("examples/output/vector_field.png", dpi=200)
