from plotten.themes import Theme, theme_default, theme_minimal, theme_dark


def test_theme_defaults():
    t = theme_default()
    assert t.title_size == 14
    assert t.panel_background == "#ebebeb"


def test_theme_minimal():
    t = theme_minimal()
    assert t.panel_background == "none"
    assert t.axis_line_width == 0.0


def test_theme_dark():
    t = theme_dark()
    assert t.background == "#2d2d2d"
    assert t.panel_background == "#3d3d3d"


def test_theme_add():
    base = theme_default()
    overlay = Theme(title_size=20)
    combined = base + overlay
    assert combined.title_size == 20
    # Non-overridden fields stay from base
    assert combined.panel_background == "#ebebeb"


def test_theme_frozen():
    t = Theme()
    try:
        t.title_size = 99  # type: ignore[misc]
        assert False
    except AttributeError:
        pass
