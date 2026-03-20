from __future__ import annotations

import numpy as np

from plotten import cut_interval, cut_number, cut_width


class TestCutWidth:
    def test_basic(self):
        labels = cut_width([1, 5, 10, 15, 20], 10)
        assert len(labels) == 5
        assert all(isinstance(label, str) for label in labels)
        assert labels[0].startswith("[")

    def test_same_value(self):
        labels = cut_width([5, 5, 5], 1)
        assert len(labels) == 3
        assert len(set(labels)) == 1

    def test_bin_format(self):
        labels = cut_width([1, 2, 3], 2)
        for label in labels:
            assert label.startswith("[")
            assert label.endswith(")")

    def test_all_values_binned(self):
        x = list(range(100))
        labels = cut_width(x, 10)
        assert len(labels) == 100


class TestCutInterval:
    def test_basic(self):
        labels = cut_interval([1, 2, 3, 4, 5], 2)
        assert len(labels) == 5

    def test_bin_count(self):
        x = np.linspace(0, 100, 1000)
        labels = cut_interval(x, 5)
        unique_bins = set(labels)
        # May be 5 or 6 depending on endpoint handling
        assert 5 <= len(unique_bins) <= 6

    def test_single_value(self):
        labels = cut_interval([5, 5, 5], 3)
        assert len(labels) == 3


class TestCutNumber:
    def test_basic(self):
        labels = cut_number([1, 2, 3, 4, 5, 6], 3)
        assert len(labels) == 6

    def test_roughly_equal_counts(self):
        x = list(range(100))
        labels = cut_number(x, 4)
        from collections import Counter

        counts = Counter(labels)
        assert len(counts) == 4
        # Each bin should have roughly 25 values
        for count in counts.values():
            assert 20 <= count <= 30

    def test_label_format(self):
        labels = cut_number([1, 2, 3, 4], 2)
        for label in labels:
            assert label.startswith("[")
            assert label.endswith(")")
