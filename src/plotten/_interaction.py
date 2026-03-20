"""Combine multiple variables into a single grouping variable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Interaction:
    """Combine multiple columns into a single grouping variable.

    When resolved, column values are pasted together with "." separator.
    Usage: ``aes(color=interaction("species", "island"))``
    """

    columns: tuple[str, ...]

    @property
    def name(self) -> str:
        """Return a synthetic column name for the interaction."""
        return ".".join(self.columns)


def interaction(*columns: str) -> Interaction:
    """Combine multiple variables into a single grouping variable.

    Parameters
    ----------
    *columns
        Column names to combine. Values are pasted with "." separator.

    Returns
    -------
    Interaction
        An object usable in ``aes()`` that resolves to a combined column.

    Raises
    ------
    ConfigError
        If fewer than 2 columns are provided.

    Examples
    --------
    >>> aes(color=interaction("species", "island"))
    """
    if len(columns) < 2:
        from plotten._validation import ConfigError

        msg = "interaction() requires at least 2 columns"
        raise ConfigError(msg)
    return Interaction(columns=columns)
