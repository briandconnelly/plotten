"""Waffle charts — proportional grid visualizations."""

import polars as pl

from plotten import plot_waffle

# --- Example 1: Market share ---
market = pl.DataFrame(
    {
        "company": ["Acme Corp", "Beta Inc", "Gamma Ltd", "Others"],
        "share": [42, 28, 18, 12],
    }
)

p1 = plot_waffle(
    market,
    category="company",
    value="share",
    colors={
        "Acme Corp": "#2196F3",
        "Beta Inc": "#FF9800",
        "Gamma Ltd": "#4CAF50",
        "Others": "#9E9E9E",
    },
    title="Market Share (each square = 1%)",
)
p1.save("examples/output/waffle_market_share.png", dpi=200)

# --- Example 2: Budget allocation with custom grid ---
budget = pl.DataFrame(
    {
        "category": ["Engineering", "Marketing", "Sales", "Operations", "R&D"],
        "amount": [35, 20, 15, 15, 15],
    }
)

p2 = plot_waffle(
    budget,
    category="category",
    value="amount",
    rows=5,
    cols=20,
    colors=["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E"],
    title="Budget Allocation -- 5x20 grid",
)
p2.save("examples/output/waffle_budget.png", dpi=200)

# --- Example 3: Simple two-category split ---
votes = pl.DataFrame(
    {
        "party": ["Yes", "No"],
        "count": [63, 37],
    }
)

p3 = plot_waffle(
    votes,
    category="party",
    value="count",
    colors={"Yes": "#43A047", "No": "#E53935"},
    title="Referendum Result — 63% Yes",
)
p3.save("examples/output/waffle_votes.png", dpi=200)

print("Saved 3 waffle chart examples to examples/output/")
