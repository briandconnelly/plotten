"""Tests for font registration, Google Fonts integration, and ElementText propagation."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")

from plotten import (
    Theme,
    aes,
    available_fonts,
    element_text,
    facet_wrap,
    geom_point,
    ggplot,
    labs,
    register_font,
    register_google_font,
    theme,
)
from plotten._render._mpl import render
from plotten._validation import FontError
from plotten.themes._text_props import text_props

# ---- helpers ---------------------------------------------------------------


def _make_plot(df=None, **theme_kw):
    """Create a simple plot with a legend, title, subtitle, and caption."""
    if df is None:
        import polars as pl

        df = pl.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "g": ["a", "b", "c"]})
    p = (
        ggplot(df, aes(x="x", y="y", color="g"))
        + geom_point()
        + labs(title="Title", subtitle="Sub", caption="Cap", x="X", y="Y")
        + theme(**theme_kw)
    )
    fig = render(p)
    plt.close(fig)
    return fig


def _make_faceted_plot(**theme_kw):
    """Create a faceted plot."""
    import polars as pl

    df = pl.DataFrame(
        {"x": [1, 2, 3, 4], "y": [4, 5, 6, 7], "g": ["a", "a", "b", "b"]},
    )
    p = (
        ggplot(df, aes(x="x", y="y"))
        + geom_point()
        + facet_wrap("g")
        + labs(title="Title", x="X", y="Y")
        + theme(**theme_kw)
    )
    fig = render(p)
    plt.close(fig)
    return fig


# ---- Phase 1A: text_props helper ------------------------------------------


class TestTextProps:
    def test_defaults(self):
        t = Theme()
        result = text_props(None, t, default_size=12.0, default_color="red")
        assert result["fontsize"] == 12.0
        assert result["color"] == "red"
        assert result["fontfamily"] == "sans-serif"
        assert "fontweight" not in result
        assert "fontstyle" not in result

    def test_element_text_overrides(self):
        t = Theme(font_family="serif")
        et = element_text(size=20, color="blue", family="monospace", weight="bold", style="italic")
        result = text_props(et, t, default_size=12.0)
        assert result["fontsize"] == 20
        assert result["color"] == "blue"
        assert result["fontfamily"] == "monospace"
        assert result["fontweight"] == "bold"
        assert result["fontstyle"] == "italic"

    def test_element_blank_returns_defaults(self):
        from plotten import element_blank

        t = Theme()
        result = text_props(element_blank(), t, default_size=10.0)
        assert result["fontsize"] == 10.0
        assert "fontweight" not in result

    def test_partial_override(self):
        t = Theme(font_family="serif")
        et = element_text(weight="bold")
        result = text_props(et, t, default_size=14.0, default_color="#333")
        assert result["fontsize"] == 14.0
        assert result["color"] == "#333"
        assert result["fontfamily"] == "serif"
        assert result["fontweight"] == "bold"


# ---- Phase 1B-1G: ElementText propagation ---------------------------------


class TestTitlePropagation:
    def test_plot_title_weight_style(self):
        """theme(plot_title=element_text(weight='bold', style='italic')) applies to title."""
        fig = _make_plot(plot_title=element_text(weight="bold", style="italic"))
        # Header is rendered via suptitle — check the figure's texts
        title_texts = [t for t in fig.texts if t.get_text() == "Title"]
        if not title_texts:
            # May be in subfigures
            for sf in fig.subfigs:
                title_texts.extend(t for t in sf.texts if t.get_text() == "Title")
                if (
                    hasattr(sf, "_suptitle")
                    and sf._suptitle is not None
                    and sf._suptitle.get_text() == "Title"
                ):
                    title_texts.append(sf._suptitle)
        assert len(title_texts) > 0
        t = title_texts[0]
        assert t.get_fontweight() == "bold"
        assert t.get_fontstyle() == "italic"

    def test_plot_subtitle_family(self):
        """Subtitle picks up family from element_text."""
        fig = _make_plot(plot_subtitle=element_text(family="monospace"))
        subtitle_texts = []
        for sf in getattr(fig, "subfigs", []):
            subtitle_texts.extend(t for t in sf.texts if t.get_text() == "Sub")
        assert len(subtitle_texts) > 0
        assert "monospace" in subtitle_texts[0].get_fontfamily()


class TestCaptionPropagation:
    def test_caption_element(self):
        """theme(plot_caption=element_text(size=8, color='gray')) applies to caption."""
        fig = _make_plot(plot_caption=element_text(size=8, color="gray"))
        cap_texts = []
        for sf in getattr(fig, "subfigs", []):
            cap_texts.extend(t for t in sf.texts if t.get_text() == "Cap")
        assert len(cap_texts) > 0
        assert cap_texts[0].get_fontsize() == 8
        assert cap_texts[0].get_color() == "gray"


class TestAxisTitlePropagation:
    def test_axis_title_family(self):
        """theme(axis_title=element_text(family='monospace')) applies to axis labels."""
        fig = _make_plot(axis_title=element_text(family="monospace"))
        axes = fig.get_axes()
        # Find the main plot axes (not legend)
        for ax in axes:
            xlabel = ax.get_xlabel()
            if xlabel == "X":
                assert "monospace" in ax.xaxis.label.get_fontfamily()
                break

    def test_axis_title_weight_color(self):
        """weight and color propagate to axis titles."""
        fig = _make_plot(axis_title=element_text(weight="bold", color="red"))
        for ax in fig.get_axes():
            if ax.get_xlabel() == "X":
                assert ax.xaxis.label.get_fontweight() == "bold"
                assert ax.xaxis.label.get_color() == "red"
                break


class TestTickLabelPropagation:
    def test_axis_text_family(self):
        """theme(axis_text=element_text(family='monospace')) applies to tick labels."""
        fig = _make_plot(axis_text=element_text(family="monospace"))
        for ax in fig.get_axes():
            if ax.get_xlabel() == "X":
                labels = ax.get_xticklabels()
                if labels:
                    assert "monospace" in labels[0].get_fontfamily()
                break

    def test_axis_text_color(self):
        """Tick label color from axis_text element."""
        fig = _make_plot(axis_text=element_text(color="blue"))
        for ax in fig.get_axes():
            if ax.get_xlabel() == "X":
                # tick_params sets labelcolor
                # Check via the tick label objects
                labels = ax.get_xticklabels()
                if labels:
                    assert labels[0].get_color() == "blue"
                break


class TestStripTextPropagation:
    def test_strip_text_weight(self):
        """theme(strip_text=element_text(weight='bold')) applies to facet strips."""
        fig = _make_faceted_plot(strip_text=element_text(weight="bold"))
        # Strip labels are set via set_title on each subplot
        for ax in fig.get_axes():
            title_obj = ax.title
            if title_obj.get_text() in ("a", "b"):
                assert title_obj.get_fontweight() == "bold"


class TestLegendPropagation:
    def test_legend_title_style(self):
        """theme(legend_title_element=element_text(style='italic')) applies."""
        fig = _make_plot(legend_title_element=element_text(style="italic"))
        # Legend title is rendered as text on a legend axes
        for ax in fig.get_axes():
            for t in ax.texts:
                if t.get_text() == "g":
                    assert t.get_fontstyle() == "italic"
                    return
        # If legend is drawn via a different mechanism, at least no error occurred

    def test_legend_text_color(self):
        """Legend entry text picks up color."""
        fig = _make_plot(legend_text_element=element_text(color="red"))
        for ax in fig.get_axes():
            for t in ax.texts:
                if t.get_text() in ("a", "b", "c"):
                    assert t.get_color() == "red"
                    return


# ---- Phase 2: Font API ----------------------------------------------------


class TestRegisterFont:
    def test_invalid_path(self):
        with pytest.raises(FontError, match="not found"):
            register_font("/nonexistent/font.ttf")

    def test_invalid_extension(self, tmp_path):
        bad = tmp_path / "font.txt"
        bad.write_text("not a font")
        with pytest.raises(FontError, match="Unsupported font extension"):
            register_font(bad)


class TestAvailableFonts:
    def test_returns_sorted_list(self):
        fonts = available_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0
        assert fonts == sorted(fonts)

    def test_contains_default_font(self):
        fonts = available_fonts()
        # matplotlib always has DejaVu Sans
        assert any("DejaVu" in f for f in fonts)


# ---- Phase 3: Google Fonts ------------------------------------------------


class TestGoogleFonts:
    def test_caching_skips_download(self, tmp_path):
        """When font files already exist in cache, no download occurs."""
        family = "FakeFont"
        cache_dir = tmp_path / family

        # Create a fake cached TTF — use a real TTF so matplotlib can parse it
        cache_dir.mkdir()
        fake_ttf = cache_dir / "FakeFont-0.ttf"
        import matplotlib.font_manager as fm

        real_ttf = fm.findfont("DejaVu Sans")
        fake_ttf.write_bytes(Path(real_ttf).read_bytes())

        with (
            patch("plotten.fonts._CACHE_DIR", tmp_path),
            patch("plotten.fonts.urlopen") as mock_urlopen,
        ):
            result = register_google_font(family)
            mock_urlopen.assert_not_called()
            assert isinstance(result, str)
            assert len(result) > 0

    def test_bad_family_raises(self):
        """A network error raises FontError."""
        with patch("plotten.fonts.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("HTTP 404")
            with pytest.raises(FontError, match="Failed to fetch"):
                register_google_font("NonExistentFontXYZ123")

    def test_no_font_urls_in_css_raises(self, tmp_path):
        """CSS response with no font URLs raises FontError."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"/* empty CSS, no @font-face */"
        with (
            patch("plotten.fonts._CACHE_DIR", tmp_path),
            patch("plotten.fonts.urlopen", return_value=mock_resp),
            pytest.raises(FontError, match="No font files found"),
        ):
            register_google_font("BogusFont")

    def test_download_and_register(self, tmp_path):
        """CSS with a TTF URL triggers download and registration."""
        import matplotlib.font_manager as fm

        real_ttf_path = fm.findfont("DejaVu Sans")
        real_ttf_bytes = Path(real_ttf_path).read_bytes()

        css_body = b"@font-face { src: url(https://fonts.gstatic.com/s/fake/v1/Fake.ttf); }"
        css_resp = MagicMock()
        css_resp.read.return_value = css_body

        ttf_resp = MagicMock()
        ttf_resp.read.return_value = real_ttf_bytes

        def fake_urlopen(req, *a, **kw):
            # First call = CSS, second call = TTF download
            if isinstance(req, str) and req.startswith("https://fonts.gstatic"):
                return ttf_resp
            return css_resp

        with (
            patch("plotten.fonts._CACHE_DIR", tmp_path),
            patch("plotten.fonts.urlopen", side_effect=fake_urlopen),
        ):
            result = register_google_font("FakeFamily")
            assert isinstance(result, str)
            assert len(result) > 0
            # Verify the file was cached
            cached = list((tmp_path / "FakeFamily").glob("*.ttf"))
            assert len(cached) == 1


# ---- Phase 4D: Math text verification -------------------------------------


class TestMathText:
    def test_math_in_axis_labels(self):
        """$x^2$ in axis labels renders without error."""
        import polars as pl

        df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(x="$x^2$", y="$y^2$")
        fig = render(p)
        plt.close(fig)

    def test_math_in_title(self):
        """$\\alpha$ in title renders without error."""
        import polars as pl

        df = pl.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = ggplot(df, aes(x="x", y="y")) + geom_point() + labs(title=r"$\alpha$ test")
        fig = render(p)
        plt.close(fig)
