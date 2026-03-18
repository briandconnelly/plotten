"""Tests for v0.5 date/time scales."""

from __future__ import annotations

import datetime

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from plotten import aes, geom_line, geom_point, ggplot, scale_x_date
from plotten.scales._base import auto_scale
from plotten.scales._date import ScaleDateContinuous


class TestScaleDateContinuous:
    def test_train_python_date(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [
                datetime.date(2024, 1, 1),
                datetime.date(2024, 6, 1),
                datetime.date(2024, 12, 31),
            ],
        )
        scale.train(dates)
        lo, hi = scale.get_limits()
        assert lo < hi

    def test_train_python_datetime(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [
                datetime.datetime(2024, 1, 1, 0, 0),
                datetime.datetime(2024, 6, 1, 12, 0),
            ],
        )
        scale.train(dates)
        lo, hi = scale.get_limits()
        assert lo < hi

    def test_map_data(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)],
        )
        scale.train(dates)
        mapped = scale.map_data(dates)
        assert isinstance(mapped, list)
        assert len(mapped) == 2
        assert mapped[0] < mapped[1]

    def test_breaks(self):
        scale = ScaleDateContinuous(aesthetic="x")
        dates = pl.Series(
            "x",
            [datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)],
        )
        scale.train(dates)
        breaks = scale.get_breaks()
        assert len(breaks) == 6


class TestAutoScaleDate:
    def test_detects_date(self):
        s = pl.Series("x", [datetime.date(2024, 1, 1), datetime.date(2024, 6, 1)])
        scale = auto_scale("x", s)
        assert isinstance(scale, ScaleDateContinuous)

    def test_detects_datetime(self):
        s = pl.Series(
            "x",
            [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 6, 1)],
        )
        scale = auto_scale("x", s)
        assert isinstance(scale, ScaleDateContinuous)


class TestExplicitDateScale:
    def test_scale_x_date(self):
        scale = scale_x_date()
        assert isinstance(scale, ScaleDateContinuous)
        assert scale.aesthetic == "x"


class TestDateIntegration:
    def test_python_date_renders(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.date(2024, 1, 1),
                    datetime.date(2024, 4, 1),
                    datetime.date(2024, 7, 1),
                ],
                "y": [10, 20, 30],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_python_datetime_renders(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.datetime(2024, 1, 1, 0, 0),
                    datetime.datetime(2024, 6, 1, 12, 0),
                    datetime.datetime(2024, 12, 1, 6, 0),
                ],
                "y": [1, 2, 3],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_point()
        fig = p._repr_png_()
        assert len(fig) > 0

    def test_explicit_scale_x_date(self):
        df = pl.DataFrame(
            {
                "x": [
                    datetime.date(2024, 1, 1),
                    datetime.date(2024, 6, 1),
                ],
                "y": [10, 20],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line() + scale_x_date()
        fig = p._repr_png_()
        assert len(fig) > 0


class TestDateWithPandas:
    def test_pandas_timestamp_renders(self):
        pd = pytest.importorskip("pandas")
        df = pd.DataFrame(
            {
                "x": pd.to_datetime(["2024-01-01", "2024-06-01", "2024-12-01"]),
                "y": [1, 2, 3],
            }
        )
        p = ggplot(df, aes(x="x", y="y")) + geom_line()
        fig = p._repr_png_()
        assert len(fig) > 0
