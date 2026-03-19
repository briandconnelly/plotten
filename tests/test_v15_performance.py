"""Tests for v0.15.0 Phase 3: Performance improvements."""

from __future__ import annotations

import subprocess
import sys

import polars as pl

from plotten.scales._base import MappedContinuousScale, MappedDiscreteScale
from plotten.scales._position import ScaleContinuous, ScaleDiscrete


class TestImportTime:
    """Verify that ``import plotten`` completes in a reasonable time."""

    def test_import_time_under_200ms(self) -> None:
        """import plotten should complete in under 200ms.

        This guards against accidentally pulling heavy dependencies
        (matplotlib, scipy) at import time.
        """
        code = (
            "import time; t = time.time(); import plotten; "
            "print(f'{(time.time() - t) * 1000:.0f}')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        ms = int(result.stdout.strip())
        assert ms < 200, f"import plotten took {ms}ms, expected < 200ms"


class TestScaleCaching:
    """Verify that scale break/label computation is cached."""

    def test_continuous_breaks_cached(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series = pl.Series("x", [1.0, 2.0, 3.0, 4.0, 5.0])
        scale.train(series)

        breaks1 = scale.get_breaks()
        breaks2 = scale.get_breaks()
        assert breaks1 is breaks2, "get_breaks() should return cached list"

    def test_continuous_labels_cached(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series = pl.Series("x", [1.0, 2.0, 3.0, 4.0, 5.0])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2, "get_labels() should return cached list"

    def test_cache_invalidated_on_train(self) -> None:
        scale = ScaleContinuous(aesthetic="x")
        series1 = pl.Series("x", [1.0, 2.0, 3.0])
        scale.train(series1)
        breaks1 = scale.get_breaks()

        series2 = pl.Series("x", [10.0, 20.0])
        scale.train(series2)
        breaks2 = scale.get_breaks()

        assert breaks1 is not breaks2, "Cache should be invalidated after train()"
        assert breaks2[-1] > breaks1[-1], "New breaks should reflect expanded domain"

    def test_discrete_labels_cached(self) -> None:
        scale = ScaleDiscrete(aesthetic="x")
        series = pl.Series("x", ["a", "b", "c"])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2, "get_labels() should return cached list"

    def test_discrete_cache_invalidated(self) -> None:
        scale = ScaleDiscrete(aesthetic="x")
        series1 = pl.Series("x", ["a", "b"])
        scale.train(series1)
        labels1 = scale.get_labels()

        series2 = pl.Series("x", ["c", "d"])
        scale.train(series2)
        labels2 = scale.get_labels()

        assert labels1 is not labels2
        assert len(labels2) == 4

    def test_mapped_continuous_breaks_cached(self) -> None:
        """MappedContinuousScale subclasses should also cache breaks."""

        class _TestScale(MappedContinuousScale):
            def __init__(self) -> None:
                super().__init__("test")
                self._breaks = None
                self._limits = None

            def map_data(self, values: object) -> object:
                return values

        scale = _TestScale()
        series = pl.Series("v", [0.0, 10.0])
        scale.train(series)

        breaks1 = scale.get_breaks()
        breaks2 = scale.get_breaks()
        assert breaks1 is breaks2

    def test_mapped_discrete_labels_cached(self) -> None:
        """MappedDiscreteScale subclasses should also cache labels."""

        class _TestScale(MappedDiscreteScale):
            def __init__(self) -> None:
                super().__init__("test")
                self._levels: list = []

            def map_data(self, values: object) -> object:
                return values

        scale = _TestScale()
        series = pl.Series("v", ["x", "y", "z"])
        scale.train(series)

        labels1 = scale.get_labels()
        labels2 = scale.get_labels()
        assert labels1 is labels2
