"""Plot recipes — high-level constructors for common chart types."""

import polars as pl

from plotten import plot_dumbbell, plot_forest, plot_lollipop, plot_slope, plot_waterfall

# --- Waterfall chart ---
waterfall_df = pl.DataFrame(
    {
        "category": ["Revenue", "COGS", "Gross Profit", "OpEx", "Tax", "Net Income"],
        "amount": [500, -200, 100, -120, -50, 30],
    }
)
p1 = plot_waterfall(waterfall_df, x="category", y="amount", title="Income Statement Waterfall")
p1.save("examples/output/recipe_waterfall.png", dpi=200)

# --- Dumbbell chart ---
dumbbell_df = pl.DataFrame(
    {
        "department": ["Engineering", "Marketing", "Sales", "Support", "HR"],
        "q1": [82, 65, 71, 78, 60],
        "q4": [91, 72, 85, 80, 75],
    }
)
p2 = plot_dumbbell(
    dumbbell_df,
    x_start="q1",
    x_end="q4",
    y="department",
    title="Employee Satisfaction: Q1 vs Q4",
)
p2.save("examples/output/recipe_dumbbell.png", dpi=200)

# --- Lollipop chart ---
lollipop_df = pl.DataFrame(
    {
        "feature": [1, 2, 3, 4, 5, 6, 7, 8],
        "importance": [0.32, 0.28, 0.15, 0.10, 0.06, 0.04, 0.03, 0.02],
    }
)
p3 = plot_lollipop(
    lollipop_df,
    x="feature",
    y="importance",
    color="#8e44ad",
    title="Feature Importance",
)
p3.save("examples/output/recipe_lollipop.png", dpi=200)

# --- Slope chart ---
slope_df = pl.DataFrame(
    {
        "year": ["2023", "2023", "2023", "2024", "2024", "2024"],
        "revenue": [120, 95, 80, 140, 110, 60],
        "product": ["Widget A", "Widget B", "Widget C", "Widget A", "Widget B", "Widget C"],
    }
)
p4 = plot_slope(
    slope_df,
    x="year",
    y="revenue",
    group="product",
    title="Revenue by Product: 2023 vs 2024",
)
p4.save("examples/output/recipe_slope.png", dpi=200)

# --- Forest plot ---
forest_df = pl.DataFrame(
    {
        "study": ["Smith 2020", "Jones 2021", "Lee 2022", "Garcia 2023", "Overall"],
        "estimate": [0.45, 0.22, 0.68, 0.35, 0.42],
        "ci_low": [0.12, -0.10, 0.30, 0.05, 0.25],
        "ci_high": [0.78, 0.54, 1.06, 0.65, 0.59],
    }
)
p5 = plot_forest(
    forest_df,
    y="study",
    x="estimate",
    xmin="ci_low",
    xmax="ci_high",
    title="Meta-Analysis: Treatment Effect",
)
p5.save("examples/output/recipe_forest.png", dpi=200)

print("Saved 5 recipe plots to examples/output/")
