"""Tests for break generators, label formatters, and oob utilities."""

from __future__ import annotations

from plotten import (
    breaks_integer,
    breaks_log,
    breaks_pretty,
    breaks_quantile,
    breaks_width,
    censor,
    expand_range,
    label_bytes,
    label_comma,
    label_currency,
    label_date,
    label_date_short,
    label_dollar,
    label_duration,
    label_log,
    label_number,
    label_number_auto,
    label_ordinal,
    label_percent,
    label_pvalue,
    label_scientific,
    label_si,
    label_wrap,
    oob_censor,
    oob_keep,
    oob_squish,
    rescale,
    rescale_mid,
    squish,
    zero_range,
)

# ---------------------------------------------------------------------------
# Break generators
# ---------------------------------------------------------------------------


class TestBreaksPretty:
    def test_round_numbers(self):
        result = breaks_pretty(5)((0, 97))
        # Should produce round numbers spanning the range
        assert all(isinstance(x, float | int) for x in result)
        assert result[0] <= 0
        assert result[-1] >= 97

    def test_small_range(self):
        result = breaks_pretty(5)((0.3, 4.1))
        assert result[0] <= 0.3
        assert result[-1] >= 4.1

    def test_negative_range(self):
        result = breaks_pretty(5)((-10, 10))
        assert 0 in result or 0.0 in result

    def test_zero_range(self):
        result = breaks_pretty(5)((5, 5))
        assert result == [5]

    def test_large_range(self):
        result = breaks_pretty(5)((0, 1_000_000))
        # Should have nice round numbers (multiples of 250k or similar)
        assert all(v % 50_000 == 0 for v in result)


class TestBreaksWidth:
    def test_basic(self):
        result = breaks_width(25)((0, 100))
        assert result == [0, 25, 50, 75, 100]

    def test_with_offset(self):
        result = breaks_width(10, offset=5)((0, 30))
        assert result == [5, 15, 25]

    def test_non_aligned(self):
        result = breaks_width(30)((0, 100))
        assert result == [0, 30, 60, 90]

    def test_decimal_width(self):
        result = breaks_width(0.5)((0, 2))
        assert len(result) == 5
        assert result[0] == 0
        assert result[-1] == 2.0


class TestBreaksLog:
    def test_basic_decades(self):
        result = breaks_log(10)((1, 1000))
        assert 1 in result
        assert 10 in result
        assert 100 in result
        assert 1000 in result

    def test_subdivisions(self):
        result = breaks_log(10)((1, 1000))
        # Should include 2x and 5x subdivisions
        assert 2 in result
        assert 5 in result
        assert 20 in result
        assert 50 in result

    def test_narrow_range(self):
        result = breaks_log(10)((5, 50))
        assert all(5 <= v <= 50 for v in result)


class TestBreaksInteger:
    def test_basic(self):
        result = breaks_integer(5)((0, 7))
        assert all(isinstance(v, int) for v in result)
        assert result[0] <= 0
        assert result[-1] >= 7

    def test_small_range(self):
        result = breaks_integer(5)((0, 3))
        assert result == [0, 1, 2, 3]

    def test_no_fractional_ticks(self):
        result = breaks_integer(10)((0, 4))
        assert all(v == int(v) for v in result)

    def test_large_range(self):
        result = breaks_integer(5)((0, 1000))
        assert all(isinstance(v, int) for v in result)
        assert len(result) >= 3

    def test_equal_limits(self):
        result = breaks_integer(5)((3, 3))
        assert result == [3]

    def test_negative(self):
        result = breaks_integer(5)((-5, 5))
        assert 0 in result
        assert all(isinstance(v, int) for v in result)


class TestBreaksQuantile:
    def test_basic(self):
        data = list(range(100))
        result = breaks_quantile(data, n=5)((0, 99))
        assert len(result) == 5
        assert result[0] == 0
        assert result[-1] == 99

    def test_median(self):
        data = list(range(101))
        result = breaks_quantile(data, n=3)((0, 100))
        assert result[1] == 50  # median

    def test_skewed(self):
        # Exponential-like: most values near 0, long tail
        data = [1, 1, 1, 2, 2, 3, 5, 10, 50, 100]
        result = breaks_quantile(data, n=5)((1, 100))
        # Breaks should be concentrated where data is dense
        assert result[2] < 10  # median is around 2.5

    def test_empty(self):
        result = breaks_quantile([], n=5)((0, 1))
        assert result == []

    def test_single_value(self):
        result = breaks_quantile([42], n=5)((42, 42))
        assert result == [42]

    def test_unsorted_input(self):
        data = [50, 10, 90, 30, 70]
        result = breaks_quantile(data, n=3)((10, 90))
        assert result[0] == 10
        assert result[-1] == 90


# ---------------------------------------------------------------------------
# Label formatters (existing)
# ---------------------------------------------------------------------------


class TestExistingLabels:
    def test_label_comma(self):
        fmt = label_comma()
        assert fmt(1234567) == "1,234,567"

    def test_label_dollar(self):
        fmt = label_dollar()
        assert fmt(1234.5) == "$1,234.50"

    def test_label_percent(self):
        fmt = label_percent()
        assert fmt(0.5) == "50.0%"

    def test_label_percent_scale_1(self):
        fmt = label_percent(scale=1)
        assert fmt(50) == "50.0%"

    def test_label_percent_scale_1_decimal(self):
        fmt = label_percent(accuracy=0, scale=1)
        assert fmt(75) == "75%"

    def test_label_scientific(self):
        fmt = label_scientific()
        assert "e" in fmt(12345)

    def test_label_number(self):
        fmt = label_number(accuracy=2)
        assert fmt(1234.5) == "1,234.50"

    def test_label_number_dot_separator(self):
        fmt = label_number(big_mark=".")
        assert fmt(1234567) == "1.234.567"

    def test_label_number_no_separator(self):
        fmt = label_number(big_mark="")
        assert fmt(1234567) == "1234567"


# ---------------------------------------------------------------------------
# Label formatters (new)
# ---------------------------------------------------------------------------


class TestLabelBytes:
    def test_auto_bytes(self):
        fmt = label_bytes()
        assert fmt(500) == "500.0 B"

    def test_auto_kilobytes(self):
        fmt = label_bytes()
        result = fmt(1536)
        assert "KB" in result

    def test_auto_megabytes(self):
        fmt = label_bytes()
        result = fmt(2_500_000)
        assert "MB" in result

    def test_fixed_unit(self):
        fmt = label_bytes(units="MB")
        result = fmt(1_048_576)
        assert "MB" in result
        assert result.startswith("1.0")

    def test_zero(self):
        fmt = label_bytes()
        assert fmt(0) == "0 B"


class TestLabelOrdinal:
    def test_basic_ordinals(self):
        fmt = label_ordinal()
        assert fmt(1) == "1st"
        assert fmt(2) == "2nd"
        assert fmt(3) == "3rd"
        assert fmt(4) == "4th"

    def test_teens(self):
        fmt = label_ordinal()
        assert fmt(11) == "11th"
        assert fmt(12) == "12th"
        assert fmt(13) == "13th"

    def test_twenties(self):
        fmt = label_ordinal()
        assert fmt(21) == "21st"
        assert fmt(22) == "22nd"
        assert fmt(23) == "23rd"


class TestLabelDate:
    def test_basic(self):
        fmt = label_date("%Y-%m-%d")
        # matplotlib date number for 2020-01-01 is roughly 737425
        from datetime import datetime

        import matplotlib.dates as mdates

        num = mdates.date2num(datetime(2020, 1, 15))
        result = fmt(num)
        assert "2020" in result
        assert "01" in result

    def test_invalid_value(self):
        fmt = label_date()
        # Should not raise
        result = fmt(float("inf"))
        assert isinstance(result, str)


class TestLabelLog:
    def test_powers_of_ten(self):
        fmt = label_log(10)
        assert fmt(1) == "10\u2070"  # 10⁰
        assert fmt(10) == "10\u00b9"  # 10¹
        assert fmt(100) == "10\u00b2"  # 10²
        assert fmt(1000) == "10\u00b3"  # 10³

    def test_non_power(self):
        fmt = label_log(10)
        # Non-powers should fall back to str
        result = fmt(50)
        assert result == "50"

    def test_zero(self):
        fmt = label_log(10)
        result = fmt(0)
        assert result == "0"


class TestLabelWrap:
    def test_short_text(self):
        fmt = label_wrap(20)
        assert fmt("short") == "short"

    def test_long_text(self):
        fmt = label_wrap(10)
        result = fmt("A very long category name")
        assert "\n" in result

    def test_exact_width(self):
        fmt = label_wrap(5)
        result = fmt("hello world")
        assert "\n" in result


class TestLabelSi:
    def test_zero(self):
        fmt = label_si()
        assert fmt(0) == "0"

    def test_below_k(self):
        fmt = label_si()
        assert fmt(500) == "500"

    def test_kilo(self):
        fmt = label_si()
        assert fmt(1500) == "1.5k"

    def test_mega(self):
        fmt = label_si()
        assert fmt(2_500_000) == "2.5M"

    def test_giga(self):
        fmt = label_si()
        assert fmt(3_800_000_000) == "3.8G"

    def test_tera(self):
        fmt = label_si()
        assert fmt(1.2e12) == "1.2T"

    def test_negative(self):
        fmt = label_si()
        assert fmt(-2500) == "-2.5k"

    def test_accuracy(self):
        fmt = label_si(accuracy=2)
        assert fmt(1234) == "1.23k"

    def test_small_decimal(self):
        fmt = label_si()
        assert fmt(0.5) == "0.5"


class TestLabelPvalue:
    def test_large(self):
        fmt = label_pvalue()
        assert fmt(0.85) == "0.850"

    def test_moderate(self):
        fmt = label_pvalue()
        assert fmt(0.032) == "0.032"

    def test_small(self):
        fmt = label_pvalue()
        assert fmt(0.0001) == "< 0.001"

    def test_one(self):
        fmt = label_pvalue()
        assert fmt(1.0) == "1"

    def test_custom_threshold(self):
        fmt = label_pvalue(threshold=0.01)
        assert fmt(0.005) == "< 0.01"
        assert fmt(0.05) == "0.050"

    def test_custom_accuracy(self):
        fmt = label_pvalue(accuracy=4)
        assert fmt(0.0456) == "0.0456"


class TestLabelDuration:
    def test_seconds(self):
        fmt = label_duration()
        assert fmt(45) == "45s"

    def test_minutes(self):
        fmt = label_duration()
        assert fmt(90) == "1m 30s"

    def test_hours(self):
        fmt = label_duration()
        assert fmt(3661) == "1h 1m"

    def test_days(self):
        fmt = label_duration()
        assert fmt(90061) == "1d 1h"

    def test_zero(self):
        fmt = label_duration()
        assert fmt(0) == "0s"

    def test_negative(self):
        fmt = label_duration()
        assert fmt(-45) == "-45s"

    def test_subsecond(self):
        fmt = label_duration()
        assert "s" in fmt(0.5)


class TestLabelCurrency:
    def test_default_dollar(self):
        fmt = label_currency()
        assert fmt(1234.5) == "$1,234.50"

    def test_euro_prefix(self):
        fmt = label_currency(prefix="EUR ")
        assert fmt(1234.5) == "EUR 1,234.50"

    def test_suffix(self):
        fmt = label_currency(prefix="", suffix=" kr", accuracy=0)
        assert fmt(9500) == "9,500 kr"

    def test_negative(self):
        fmt = label_currency()
        assert fmt(-42.5) == "-$42.50"

    def test_zero_accuracy(self):
        fmt = label_currency(accuracy=0)
        assert fmt(1234) == "$1,234"

    def test_custom_big_mark(self):
        fmt = label_currency(prefix="", suffix=" EUR", big_mark=".")
        assert fmt(1234.56) == "1.234.56 EUR"


class TestLabelDateShort:
    def test_month_boundary(self):
        from datetime import datetime

        import matplotlib.dates as mdates

        fmt = label_date_short()
        # Feb 1 should show "Feb"
        num = mdates.date2num(datetime(2024, 2, 1))
        result = fmt(num)
        assert "Feb" in result

    def test_january_shows_year(self):
        from datetime import datetime

        import matplotlib.dates as mdates

        fmt = label_date_short()
        num = mdates.date2num(datetime(2024, 1, 1))
        result = fmt(num)
        assert "2024" in result

    def test_mid_month_day(self):
        from datetime import datetime

        import matplotlib.dates as mdates

        fmt = label_date_short()
        num = mdates.date2num(datetime(2024, 3, 15))
        result = fmt(num)
        assert "15" in result

    def test_invalid_value(self):
        fmt = label_date_short()
        result = fmt(float("inf"))
        assert isinstance(result, str)


class TestLabelNumberAuto:
    def test_zero(self):
        fmt = label_number_auto()
        assert fmt(0) == "0"

    def test_small_integer(self):
        fmt = label_number_auto()
        assert fmt(42) == "42"

    def test_decimal(self):
        fmt = label_number_auto()
        result = fmt(3.14)
        assert result == "3.14"

    def test_large_comma(self):
        fmt = label_number_auto()
        assert fmt(12500) == "12,500"

    def test_very_large_si(self):
        fmt = label_number_auto()
        result = fmt(2_500_000)
        assert "M" in result

    def test_very_small_scientific(self):
        fmt = label_number_auto()
        result = fmt(0.005)
        assert "e" in result

    def test_negative(self):
        fmt = label_number_auto()
        result = fmt(-2_500_000)
        assert result.startswith("-")
        assert "M" in result

    def test_billion(self):
        fmt = label_number_auto()
        result = fmt(1_500_000_000)
        assert "G" in result


# ---------------------------------------------------------------------------
# Out-of-bounds utilities
# ---------------------------------------------------------------------------


class TestRescale:
    def test_default(self):
        result = rescale([0, 5, 10])
        assert result == [0.0, 0.5, 1.0]

    def test_custom_range(self):
        result = rescale([0, 5, 10], to=(0, 100))
        assert result == [0.0, 50.0, 100.0]

    def test_from_range(self):
        result = rescale([5], to=(0, 1), from_=(0, 10))
        assert result == [0.5]

    def test_zero_span(self):
        result = rescale([5, 5, 5])
        assert all(v == 0.5 for v in result)

    def test_empty(self):
        assert rescale([]) == []


class TestRescaleMid:
    def test_symmetric(self):
        result = rescale_mid([-2, 0, 2], mid=0)
        assert result[1] == 0.5  # midpoint maps to center

    def test_asymmetric(self):
        result = rescale_mid([-2, 0, 4], mid=0)
        assert result[1] == 0.5
        assert result[0] < 0.5
        assert result[2] > 0.5

    def test_empty(self):
        assert rescale_mid([]) == []


class TestSquish:
    def test_clamp(self):
        result = squish([-1, 0.5, 2], limits=(0, 1))
        assert result == [0, 0.5, 1]

    def test_no_clamp(self):
        result = squish([0.2, 0.5, 0.8], limits=(0, 1))
        assert result == [0.2, 0.5, 0.8]


class TestCensor:
    def test_basic(self):
        result = censor([-1, 0.5, 2], limits=(0, 1))
        assert result == [None, 0.5, None]

    def test_none_passthrough(self):
        result = censor([None, 0.5], limits=(0, 1))
        assert result == [None, 0.5]


class TestOobHandlers:
    def test_oob_squish(self):
        handler = oob_squish(limits=(0, 10))
        assert handler([-5, 3, 15]) == [0, 3, 10]

    def test_oob_censor(self):
        handler = oob_censor(limits=(0, 10))
        assert handler([-5, 3, 15]) == [None, 3, None]

    def test_oob_keep(self):
        handler = oob_keep()
        assert handler([-5, 3, 15]) == [-5, 3, 15]


class TestExpandRange:
    def test_multiplicative(self):
        result = expand_range((0, 10), mul=0.1)
        assert result == (-1.0, 11.0)

    def test_additive(self):
        result = expand_range((0, 10), add=2)
        assert result == (-2, 12)

    def test_both(self):
        lo, hi = expand_range((0, 10), mul=0.1, add=1)
        assert lo == -2.0
        assert hi == 12.0


class TestZeroRange:
    def test_equal(self):
        assert zero_range((0, 0)) is True

    def test_different(self):
        assert zero_range((0, 1)) is False

    def test_near_zero(self):
        assert zero_range((1, 1 + 1e-8)) is True

    def test_not_near_zero(self):
        assert zero_range((0, 0.01)) is False


# ---------------------------------------------------------------------------
# Integration: breaks + labels with scales
# ---------------------------------------------------------------------------


class TestScaleIntegration:
    def test_breaks_pretty_with_scale(self):
        """breaks_pretty can be passed as the breaks parameter to a scale."""
        import pandas as pd

        from plotten import aes, geom_point, ggplot, scale_x_continuous

        df = pd.DataFrame({"x": [0, 25, 50, 75, 100], "y": [1, 2, 3, 4, 5]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_x_continuous(breaks=breaks_pretty(5))
        )
        png = p._repr_png_()
        assert len(png) > 0

    def test_breaks_width_with_scale(self):
        import pandas as pd

        from plotten import aes, geom_point, ggplot, scale_y_continuous

        df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 50, 90]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + scale_y_continuous(breaks=breaks_width(25))
        )
        png = p._repr_png_()
        assert len(png) > 0

    def test_label_log_with_scale(self):
        import pandas as pd

        from plotten import aes, geom_point, ggplot, scale_x_log10

        df = pd.DataFrame({"x": [1, 10, 100, 1000], "y": [1, 2, 3, 4]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_log10()
        png = p._repr_png_()
        assert len(png) > 0
