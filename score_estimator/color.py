"""Color constants for Go stones."""

from enum import IntEnum


class Color(IntEnum):
    """Represents the color of a stone or empty space on the Go board."""
    EMPTY = 0
    BLACK = 1
    WHITE = -1


def other(c: Color) -> Color:
    """Return the opposite color."""
    return Color.BLACK if c == Color.WHITE else Color.WHITE


# Convenient constants
EMPTY = Color.EMPTY
BLACK = Color.BLACK
WHITE = Color.WHITE
