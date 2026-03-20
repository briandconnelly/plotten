from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pytest

matplotlib.use("Agg")

from plotten import Rel, aes, element_text, geom_point, ggplot, rel, theme
from plotten._render._mpl import render
from plotten.themes._elements import ElementText
from plotten.themes._text_props import text_props
from plotten.themes._theme import Theme


class TestRel:
    def test_rel_factory(self):
        r = rel(0.8)
        assert isinstance(r, Rel)
        assert r.factor == 0.8

    def test_rel_frozen(self):
        r = Rel(1.5)
        with pytest.raises(AttributeError):
            r.factor = 2.0  # type: ignore[misc]


class TestRelInTextProps:
    def test_rel_resolves_to_absolute(self):
        elem = ElementText(size=rel(0.8))
        t = Theme()
        props = text_props(elem, t, default_size=20.0)
        assert props["fontsize"] == pytest.approx(16.0)

    def test_rel_1_0_preserves_default(self):
        elem = ElementText(size=rel(1.0))
        t = Theme()
        props = text_props(elem, t, default_size=12.0)
        assert props["fontsize"] == pytest.approx(12.0)

    def test_rel_1_5_scales_up(self):
        elem = ElementText(size=rel(1.5))
        t = Theme()
        props = text_props(elem, t, default_size=10.0)
        assert props["fontsize"] == pytest.approx(15.0)

    def test_rel_without_default_size(self):
        """If no default_size, Rel cannot resolve — fontsize stays unset."""
        elem = ElementText(size=rel(0.8))
        t = Theme()
        props = text_props(elem, t, default_size=None)
        assert "fontsize" not in props

    def test_absolute_size_still_works(self):
        elem = ElementText(size=16.0)
        t = Theme()
        props = text_props(elem, t, default_size=12.0)
        assert props["fontsize"] == 16.0


class TestRelInTheme:
    def test_element_text_with_rel(self):
        elem = element_text(size=rel(0.8))
        assert isinstance(elem.size, Rel)

    def test_theme_composition_with_rel(self):
        """Rel values compose correctly through Theme.__add__."""
        t1 = Theme()
        t2 = Theme(axis_title=ElementText(size=rel(0.9)))
        combined = t1 + t2
        assert isinstance(combined.axis_title, ElementText)
        assert isinstance(combined.axis_title.size, Rel)
        assert combined.axis_title.size.factor == 0.9

    def test_plot_renders_with_rel_theme(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        p = (
            ggplot(df, aes(x="x", y="y"))
            + geom_point()
            + theme(axis_title=element_text(size=rel(0.8)))
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)
