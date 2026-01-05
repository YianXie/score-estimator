# About

This repository contains the source code used for the score estimator and dead
stone removal suggester on online-go.com.

**Now available in Python 3.11+!** This repository includes both the original C++
implementation and a faithful Python port that maintains the exact same algorithm.

The C++ version is designed to be a score estimator with a small memory and code size foot
print and fast single threaded execution speeds. The C++ source is compiled to JavaScript using
[Emscripten](https://github.com/kripken/emscripten) for client side use within
the browser.

The Python version provides the same algorithm in a more accessible form for Python
developers, maintaining algorithmic fidelity to the C++ implementation.


## Seki

Different GO rules treat territory in seki differently. The output of this
program will attempt to mark shared territory spots as being dead, but will
specifically attempt to not mark any territory in seki as being dead, and
instead leave that to a scoring ruleset to determine as being counted or
not.

That is to say
![](https://senseis.xmp.net/diagrams/30/1d10677a69ac35bb0021701f2e1c02a7.png)
points a and b will *not* be marked dead, but the two shared territory spaces
will be marked as dead.

## Python Usage

### Installation

You can install the Python package in several ways:

```bash
# Install from the repository directory
pip install .

# Or install in development mode
pip install -e .
```

### Quick Start

```python
from score_estimator import Goban, BLACK, WHITE, EMPTY

# Create a 19x19 board
goban = Goban(19, 19)

# Set up your position (0 = empty, 1 = black, -1 = white)
goban.board[3][3] = BLACK
goban.board[3][4] = BLACK
goban.board[4][3] = BLACK

# Estimate the score and detect dead stones
result = goban.estimate(
    player_to_move=BLACK,
    num_iterations=1000,  # Number of random playouts
    tolerance=0.4         # Confidence threshold (0.0-1.0)
)

# Result grid shows ownership: 1=black, -1=white, 0=dame/unclear
score_difference = result.sum()
print(f"Score difference (positive = black ahead): {score_difference}")
```

### Parameters

- **player_to_move**: `BLACK` (1) or `WHITE` (-1) - which player moves next
- **num_iterations**: Number of random playouts (default: 1000, higher = more accurate but slower)
- **tolerance**: Confidence threshold 0.0-1.0 (default: 0.4, lower = more conservative)

### Example Usage

See `examples.py` for comprehensive usage examples including:

1. Simple corner positions
2. Detecting dead stones
3. Large board estimation
4. Custom parameter tuning

Run the examples:
```bash
python examples.py
```

### Key Classes

- **Goban**: The main Go board class with estimation capabilities
- **Grid**: 2D grid for board state and calculations
- **Point**: Represents a coordinate (x, y) on the board
- **Vec**: Vector of points used internally
- **Color**: Enum for stone colors (BLACK=1, WHITE=-1, EMPTY=0)

### Algorithm

The Python implementation uses the exact same algorithm as the C++ version:

1. **False Eye Detection**: Identifies and fills false eyes
2. **Seki Detection**: Finds probable seki situations
3. **Monte Carlo Rollouts**: Plays random games to estimate ownership
4. **Territory Analysis**: Computes liberties and strong life
5. **Dead Stone Detection**: Identifies likely dead stones

The algorithm is optimized for suggesting reasonable score estimates and dead stone
removals for games played by humans of varying skill levels.
