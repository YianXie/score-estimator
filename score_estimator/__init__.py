"""
OGS Score Estimator - Python 3.11 Implementation

This is a Python port of the C++ Go score estimator and dead stone removal
suggester used on online-go.com. The algorithm has been faithfully translated
to maintain the exact same behavior as the original C++ version.

Main classes:
    - Goban: The Go board with score estimation capabilities
    - Color: Enum for stone colors (BLACK, WHITE, EMPTY)
    - Grid: 2D grid for board state and calculations
    - Point: Coordinate on the board
    - Vec: Vector of points

Example usage:
    >>> from score_estimator import Goban, Color, BLACK, WHITE, EMPTY
    >>> 
    >>> # Create a 19x19 board
    >>> goban = Goban(19, 19)
    >>> 
    >>> # Set up a position (example: simple corner)
    >>> goban.board[3][3] = BLACK
    >>> goban.board[3][4] = BLACK
    >>> goban.board[4][3] = BLACK
    >>> 
    >>> # Estimate the score
    >>> result = goban.estimate(
    ...     player_to_move=BLACK,
    ...     num_iterations=1000,
    ...     tolerance=0.4
    ... )
    >>> 
    >>> # Result grid shows ownership: 1=black, -1=white, 0=dame/unclear
    >>> score_difference = result.sum()
    >>> print(f"Score difference (positive = black ahead): {score_difference}")
"""

from .color import Color, BLACK, WHITE, EMPTY, other
from .point import Point
from .vec import Vec
from .grid import Grid
from .goban import Goban

__version__ = "1.0.0"

__all__ = [
    "Goban",
    "Color",
    "BLACK",
    "WHITE", 
    "EMPTY",
    "other",
    "Point",
    "Vec",
    "Grid",
]
