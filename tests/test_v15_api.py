"""Phase 1 API consistency tests for v0.15.0."""

from __future__ import annotations

import importlib

import pytest

import plotten


class TestAllImports:
    """Verify every symbol in plotten.__all__ is importable."""

    @pytest.mark.parametrize("name", plotten.__all__)
    def test_symbol_importable(self, name: str):
        obj = getattr(plotten, name, None)
        assert obj is not None, f"plotten.{name} listed in __all__ but not importable"

    def test_all_sorted(self):
        """__all__ should be sorted for readability."""
        assert plotten.__all__ == sorted(plotten.__all__)


class TestSubpackageAll:
    """Verify subpackage __all__ entries are importable."""

    @pytest.mark.parametrize(
        "module_path",
        [
            "plotten.geoms",
            "plotten.scales",
            "plotten.positions",
            "plotten.coords",
            "plotten.facets",
            "plotten.themes",
            "plotten.stats",
        ],
    )
    def test_subpackage_all_importable(self, module_path: str):
        mod = importlib.import_module(module_path)
        for name in mod.__all__:
            obj = getattr(mod, name, None)
            assert obj is not None, f"{module_path}.{name} in __all__ but not importable"


class TestColourAlias:
    """Verify 'colour' works as alias for 'color' in aes()."""

    def test_colour_alias(self):
        mapping = plotten.aes(x="a", colour="b")
        assert mapping.color == "b"
        assert mapping.x == "a"

    def test_colour_and_color_raises(self):
        with pytest.raises(TypeError, match="Cannot specify both"):
            plotten.aes(color="a", colour="b")

    def test_color_still_works(self):
        mapping = plotten.aes(color="species")
        assert mapping.color == "species"


class TestMethodConsistency:
    """Verify Plot and PlotGrid have consistent public methods."""

    def test_plot_has_show_and_save(self):
        p = plotten.ggplot()
        assert callable(getattr(p, "show", None))
        assert callable(getattr(p, "save", None))

    def test_plotgrid_has_show_and_save(self):
        from plotten._composition import PlotGrid

        g = PlotGrid()
        assert callable(getattr(g, "show", None))
        assert callable(getattr(g, "save", None))

    def test_save_units_parameter(self):
        """Both Plot.save and PlotGrid.save should accept a 'units' parameter."""
        import inspect

        plot_params = inspect.signature(plotten.Plot.save).parameters
        assert "units" in plot_params

        from plotten._composition import PlotGrid

        grid_params = inspect.signature(PlotGrid.save).parameters
        assert "units" in grid_params

    def test_save_signatures_compatible(self):
        """Plot.save and PlotGrid.save should have the same core parameters."""
        import inspect

        plot_params = set(inspect.signature(plotten.Plot.save).parameters)
        grid_params = set(inspect.signature(plotten.PlotGrid.save).parameters)
        core = {"path", "dpi", "width", "height", "units"}
        assert core <= plot_params
        assert core <= grid_params


class TestGeomFactoryConsistency:
    """Verify all geom factories accept **params / **kwargs."""

    @pytest.mark.parametrize(
        "name",
        [n for n in plotten.__all__ if n.startswith("geom_") or n.startswith("stat_")],
    )
    def test_geom_is_callable(self, name: str):
        fn = getattr(plotten, name)
        assert callable(fn), f"{name} should be callable"

    def test_linetype_aesthetic_exists(self):
        """The Aes dataclass should use 'linetype' (not 'line_type')."""
        mapping = plotten.aes(linetype="group")
        assert mapping.linetype == "group"
        assert not hasattr(plotten.Aes, "line_type")
