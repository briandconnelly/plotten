"""Demonstrate geom_spoke for wind/flow vector fields with color mapping."""

import math

import polars as pl

from plotten import aes, geom_point, geom_spoke, ggplot, labs, scale_color_viridis, theme

# Denser grid with radii proportional to distance from center
xs = []
ys = []
angles = []
radii = []
speeds = []
cx, cy = 4.0, 4.0

for i in range(9):
    for j in range(9):
        x, y = float(i), float(j)
        xs.append(x)
        ys.append(y)
        # Angle: swirling flow pattern
        dx, dy = x - cx, y - cy
        angle = math.atan2(dy, dx) + math.pi / 2  # perpendicular to radial
        angles.append(angle)
        # Radius proportional to distance from center
        dist = math.sqrt(dx**2 + dy**2)
        r = 0.15 + 0.1 * dist
        radii.append(r)
        speeds.append(dist)

df = pl.DataFrame({"x": xs, "y": ys, "angle": angles, "radius": radii, "speed": speeds})

plot = (
    ggplot(df, aes(x="x", y="y", angle="angle", radius="radius", color="speed"))
    + geom_spoke(arrow=True, size=1.0)
    + geom_point(size=8, color="#333333", alpha=0.3)
    + scale_color_viridis(option="inferno")
    + theme(
        panel_background="#f8f8f8",
        grid_color="#e8e8e8",
        title_size=16,
    )
    + labs(
        title="Swirling Flow Field",
        subtitle="Arrow length and color show flow speed",
        x="X",
        y="Y",
        color="Speed",
    )
)

plot.save("examples/output/vector_field.png", dpi=200)
