"""Polar coordinate plots — cardioid, radar chart, and wind rose."""

import numpy as np
import polars as pl

from plotten import aes, coord_polar, geom_bar, geom_line, geom_point, ggplot, labs, theme_minimal

# --- Cardioid curve: r = 1 + cos(θ) ---
theta = np.linspace(0, 2 * np.pi, 200)
r = 1 + np.cos(theta)

cardioid_df = pl.DataFrame({"theta": theta.tolist(), "r": r.tolist()})

cardioid = (
    ggplot(cardioid_df, aes(x="theta", y="r"))
    + geom_line(color="#9C27B0", linewidth=2)
    + coord_polar()
    + labs(title="Cardioid", subtitle="r = 1 + cos(θ)")
    + theme_minimal()
)
cardioid.save("examples/output/polar_cardioid.png", dpi=200)


# --- Radar / spider chart ---
categories = ["Speed", "Power", "Technique", "Stamina", "Defense", "Agility"]
n = len(categories)
player_a = [8, 6, 9, 5, 7, 8]

# Close the polygon by repeating the first point
angles = [*np.linspace(0, 2 * np.pi, n, endpoint=False).tolist(), 0]
values = [*player_a, player_a[0]]

radar_df = pl.DataFrame({"angle": angles, "value": values})

radar = (
    ggplot(radar_df, aes(x="angle", y="value"))
    + geom_line(color="#E91E63", linewidth=2)
    + geom_point(color="#E91E63", size=4)
    + coord_polar()
    + labs(title="Player Radar Chart")
    + theme_minimal()
)
radar.save("examples/output/polar_radar.png", dpi=200)


# --- Wind rose: bar chart in polar ---
directions = list(range(8))
wind_speed = [12, 8, 15, 6, 10, 9, 18, 7]

wind_df = pl.DataFrame({"direction": directions, "speed": wind_speed})

rose = (
    ggplot(wind_df, aes(x="direction", y="speed"))
    + geom_bar(fill="#4CAF50", alpha=0.7)
    + coord_polar(start=np.pi / 2, direction=-1)
    + labs(title="Wind Rose")
    + theme_minimal()
)
rose.save("examples/output/polar_windrose.png", dpi=200)
