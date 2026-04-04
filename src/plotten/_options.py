"""Context manager for temporary plotten option overrides."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from plotten.themes._theme import Theme


@contextmanager
def options(
    *,
    theme: Theme | None = None,
    strict: bool | None = None,
) -> Generator[None]:
    """Temporarily override global plotten options.

    Any options set inside the block are restored to their previous values
    when the block exits, even if an exception is raised.

    Parameters
    ----------
    theme : Theme, optional
        A theme to set as the global default for the duration of the block.
    strict : bool, optional
        Enable or disable strict mode (warnings become errors) for the
        duration of the block.

    Examples
    --------
    >>> from plotten import options, theme_dark, ggplot, aes, geom_point
    >>> import pandas as pd
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> p = ggplot(df, aes(x="x", y="y")) + geom_point()
    >>> with options(theme=theme_dark()):
    ...     p.show()  # doctest: +SKIP
    """
    from plotten._validation import get_strict, set_strict
    from plotten.themes._theme import theme_set

    old_theme = None
    old_strict = None
    try:
        if theme is not None:
            old_theme = theme_set(theme)
        if strict is not None:
            old_strict = get_strict()
            set_strict(strict)
        yield
    finally:
        if old_theme is not None:
            theme_set(old_theme)
        if old_strict is not None:
            set_strict(old_strict)
