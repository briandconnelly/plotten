"""Statistical significance testing for pairwise group comparisons."""

from __future__ import annotations

from typing import Any

import narwhals as nw


class StatSignif:
    """Compute p-values for pairwise group comparisons.

    For each ``(group_a, group_b)`` pair, filters the data and runs the
    specified statistical test on the *y* values of each group.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        comparisons: list[tuple[str, str]],
        test: str = "t-test",
        p_adjust: str | None = None,
        step_increase: float = 0.1,
    ) -> None:
        self.comparisons = comparisons
        self.test = test
        self.p_adjust = p_adjust
        self.step_increase = step_increase

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)

        # Build group -> y-values mapping via group_by
        groups: dict[str, list[float]] = {}
        for (xv,), group in frame.group_by("x"):
            groups[str(xv)] = group.get_column("y").cast(nw.Float64).to_list()

        # Get unique x positions sorted alphabetically (matching ScaleDiscrete)
        sorted_groups = sorted(groups)
        group_positions = {g: i for i, g in enumerate(sorted_groups)}

        # Overall y-max for stacking brackets
        y_col = frame.get_column("y").cast(nw.Float64)
        y_max = float(y_col.max())
        y_range = float(y_max - y_col.min()) if len(y_col) > 1 else 1.0

        results: dict[str, list[Any]] = {
            # Use _signif_ prefix to avoid scale training via _AUX_TO_POSITION
            "_signif_xmin": [],
            "_signif_xmax": [],
            "y": [],
            "p_value": [],
            "label": [],
        }

        raw_pvalues = []
        for i, (ga, gb) in enumerate(self.comparisons):
            vals_a = groups.get(ga, [])
            vals_b = groups.get(gb, [])

            p = _run_test(vals_a, vals_b, self.test)
            raw_pvalues.append(p)

            bracket_y = y_max + y_range * self.step_increase * (i + 1)

            # Store numeric positions matching ScaleDiscrete's sorted order
            results["_signif_xmin"].append(group_positions.get(ga, 0))
            results["_signif_xmax"].append(group_positions.get(gb, 1))
            results["y"].append(bracket_y)
            results["p_value"].append(p)
            results["label"].append("")  # filled after adjustment

        # P-value adjustment
        adjusted = _adjust_pvalues(raw_pvalues, self.p_adjust)
        results["p_value"] = adjusted
        results["label"] = [_format_pvalue(p) for p in adjusted]

        backend = nw.get_native_namespace(df).__name__
        return nw.to_native(nw.from_dict(results, backend=backend))


def _run_test(a: list[float], b: list[float], test: str) -> float:
    """Run a statistical test and return the p-value."""
    if len(a) < 2 or len(b) < 2:
        return 1.0

    try:
        from scipy import stats as sp_stats
    except ImportError:
        msg = "scipy is required for geom_signif(). Install it with: uv add scipy"
        raise ImportError(msg) from None

    match test:
        case "t-test":
            _, p = sp_stats.ttest_ind(a, b)
        case "wilcoxon":
            # Wilcoxon signed-rank (paired) -- requires equal lengths
            if len(a) != len(b):
                _, p = sp_stats.mannwhitneyu(a, b, alternative="two-sided")
            else:
                _, p = sp_stats.wilcoxon(a, b)
        case "mann-whitney":
            _, p = sp_stats.mannwhitneyu(a, b, alternative="two-sided")
        case _:
            from plotten._validation import StatError

            msg = f"Unknown test: {test!r}. Valid tests: 't-test', 'wilcoxon', 'mann-whitney'."
            raise StatError(msg)

    return float(p)


def _adjust_pvalues(pvalues: list[float], method: str | None) -> list[float]:
    """Apply multiple testing correction."""
    if method is None or len(pvalues) == 0:
        return pvalues

    match method:
        case "bonferroni":
            n = len(pvalues)
            return [min(p * n, 1.0) for p in pvalues]
        case "holm":
            n = len(pvalues)
            indexed = sorted(enumerate(pvalues), key=lambda x: x[1])
            adjusted = [0.0] * n
            cummax = 0.0
            for rank, (orig_idx, p) in enumerate(indexed):
                val = min(p * (n - rank), 1.0)
                cummax = max(cummax, val)
                adjusted[orig_idx] = cummax
            return adjusted
        case "fdr":
            n = len(pvalues)
            indexed = sorted(enumerate(pvalues), key=lambda x: x[1], reverse=True)
            adjusted = [0.0] * n
            cummin = 1.0
            for rank, (orig_idx, p) in enumerate(indexed):
                val = min(p * n / (n - rank), 1.0)
                cummin = min(cummin, val)
                adjusted[orig_idx] = cummin
            return adjusted
        case _:
            from plotten._validation import StatError

            msg = (
                f"Unknown p_adjust method: {method!r}. Valid methods: 'bonferroni', 'holm', 'fdr'."
            )
            raise StatError(msg)


def _format_pvalue(p: float) -> str:
    """Format p-value as significance stars."""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"
