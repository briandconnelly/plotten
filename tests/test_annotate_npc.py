from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

from plotten import AnnotationCoord, aes, annotate, geom_point, ggplot
from plotten._render._mpl import render


class TestAnnotateNPC:
    def setup_method(self):
        self.df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
        self.base = ggplot(self.df, aes(x="x", y="y")) + geom_point()

    def test_text_npc(self):
        p = self.base + annotate("text", x=0.5, y=0.95, label="NPC label", coord="npc")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_text_npc_enum(self):
        p = self.base + annotate(
            "text", x=0.5, y=0.95, label="NPC label", coord=AnnotationCoord.NPC
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rect_npc(self):
        p = self.base + annotate(
            "rect", xmin=0.1, xmax=0.9, ymin=0.1, ymax=0.3, coord="npc", alpha=0.2
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_segment_npc(self):
        p = self.base + annotate("segment", x=0.1, y=0.1, xend=0.9, yend=0.9, coord="npc")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_curve_npc(self):
        p = self.base + annotate(
            "curve", x=0.1, y=0.5, xend=0.9, yend=0.5, coord="npc", curvature=0.3
        )
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_bracket_npc(self):
        p = self.base + annotate("bracket", xmin=0.2, xmax=0.8, y=0.9, label="*", coord="npc")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_data_coord_still_works(self):
        """Default coord='data' behavior is unchanged."""
        p = self.base + annotate("text", x=2, y=5, label="Data coords")
        fig = render(p)
        assert fig is not None
        plt.close(fig)

    def test_rect_data_coord_unchanged(self):
        p = self.base + annotate("rect", xmin=1, xmax=2, ymin=1, ymax=5)
        fig = render(p)
        assert fig is not None
        plt.close(fig)
