from __future__ import annotations

import narwhals as nw
import pytest

from plotten import load_dataset
from plotten._validation import PlottenError


class TestLoadDataset:
    def test_iris(self):
        df = load_dataset("iris")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (150, 5)
        assert set(df.columns) == {
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
            "species",
        }

    def test_mtcars(self):
        df = load_dataset("mtcars")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (32, 12)
        assert "mpg" in df.columns
        assert "name" in df.columns

    def test_penguins(self):
        df = load_dataset("penguins")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (344, 7)
        assert "species" in df.columns
        assert "bill_length_mm" in df.columns

    def test_tips(self):
        df = load_dataset("tips")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (244, 7)
        assert "total_bill" in df.columns
        assert "tip" in df.columns

    def test_faithful(self):
        df = load_dataset("faithful")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (272, 2)
        assert set(df.columns) == {"eruptions", "waiting"}

    def test_mpg(self):
        df = load_dataset("mpg")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (234, 11)
        assert "manufacturer" in df.columns
        assert "hwy" in df.columns

    def test_diamonds(self):
        df = load_dataset("diamonds")
        assert isinstance(df, nw.DataFrame)
        assert df.shape == (53940, 10)
        assert "carat" in df.columns
        assert "price" in df.columns

    def test_case_insensitive(self):
        df = load_dataset("Iris")
        assert df.shape == (150, 5)
        df = load_dataset("MTCARS")
        assert df.shape == (32, 12)

    def test_to_native(self):
        df = load_dataset("faithful")
        native = df.to_native()
        assert hasattr(native, "columns")

    def test_unknown_dataset(self):
        with pytest.raises(PlottenError, match="Unknown dataset"):
            load_dataset("nonexistent")

    def test_unknown_suggests_available(self):
        with pytest.raises(PlottenError, match="Available datasets"):
            load_dataset("foo")
