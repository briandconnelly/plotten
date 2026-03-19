"""Tests for v0.12.0 smooth enhancements."""

import pandas as pd

from plotten import Aes, geom_point, geom_smooth, ggplot, stat_poly_eq
from plotten._render._mpl import render
from plotten.stats._poly_eq import StatPolyEq
from plotten.stats._smooth import StatSmooth


class TestPolynomialSmooth:
    def test_poly_method(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + geom_smooth(method="poly", degree=2)
        fig = render(p)
        assert fig is not None

    def test_poly_default_degree(self):
        stat = StatSmooth(method="poly")
        assert stat.degree == 2

    def test_poly_cubic(self):
        df = pd.DataFrame({"x": range(10), "y": [x**3 for x in range(10)]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_smooth(method="poly", degree=3)
        fig = render(p)
        assert fig is not None

    def test_poly_no_se(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_smooth(method="poly", se=False)
        fig = render(p)
        assert fig is not None


class TestStatPolyEq:
    def test_renders(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 5, 4, 5]})
        p = ggplot(df, Aes(x="x", y="y")) + geom_point() + stat_poly_eq()
        fig = render(p)
        assert fig is not None

    def test_compute_output(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        stat = StatPolyEq(degree=1)
        result = stat.compute(df)
        import narwhals as nw

        frame = nw.from_native(result)
        assert "label" in frame.columns
        label = frame.get_column("label").to_list()[0]
        assert "R²" in label
        assert "y =" in label

    def test_quadratic_eq(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
        stat = StatPolyEq(degree=2)
        result = stat.compute(df)
        import narwhals as nw

        label = nw.from_native(result).get_column("label").to_list()[0]
        assert "R²" in label

    def test_perfect_fit_r_squared(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [2, 4, 6]})
        stat = StatPolyEq(degree=1)
        result = stat.compute(df)
        import narwhals as nw

        label = nw.from_native(result).get_column("label").to_list()[0]
        assert "1.000" in label  # R² should be 1.0
