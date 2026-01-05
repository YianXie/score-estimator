# Python Score Estimator - Usage Guide

## Installation

Install the package from the repository:

```bash
# From the repository root
pip install .

# For development
pip install -e .
```

## Basic Usage

### Creating a Board

```python
from score_estimator import Goban, BLACK, WHITE, EMPTY

# Create a 19x19 board (standard size)
goban = Goban(19, 19)

# Or smaller boards
goban_9x9 = Goban(9, 9)
goban_13x13 = Goban(13, 13)
```

### Setting Up a Position

```python
# Set stones on the board
# Coordinates are [y][x] (row, column)
goban.board[3][3] = BLACK   # Black stone at (3,3)
goban.board[3][15] = WHITE  # White stone at (3,15)

# Empty points remain 0 (EMPTY)
goban.board[4][4] = EMPTY
```

### Running the Estimator

```python
# Estimate the score
result = goban.estimate(
    player_to_move=BLACK,     # Who plays next
    num_iterations=1000,      # Number of random playouts
    tolerance=0.4             # Confidence threshold
)

# result is a Grid where:
#   1 = Black owns this point
#  -1 = White owns this point
#   0 = Dame (neutral) or unclear
```

### Interpreting Results

```python
# Get the score difference (positive = black ahead)
score_difference = result.sum()

# Check ownership of specific points
if result[3][3] == BLACK:
    print("Point (3,3) is estimated as black territory")
elif result[3][3] == WHITE:
    print("Point (3,3) is estimated as white territory")
else:
    print("Point (3,3) is dame or unclear")

# Count territory
black_points = sum(1 for y in range(19) for x in range(19) if result[y][x] > 0)
white_points = sum(1 for y in range(19) for x in range(19) if result[y][x] < 0)
dame_points = sum(1 for y in range(19) for x in range(19) if result[y][x] == 0)
```

## Parameter Tuning

### Number of Iterations

More iterations = more accurate but slower:

```python
# Fast but less accurate
result = goban.estimate(BLACK, num_iterations=500, tolerance=0.4)

# Balanced (recommended)
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.4)

# Slow but more accurate
result = goban.estimate(BLACK, num_iterations=2000, tolerance=0.4)
```

### Tolerance

Lower tolerance = more conservative (less marked as owned):

```python
# Conservative - only marks very confident ownership
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.3)

# Balanced (recommended)
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.4)

# Aggressive - marks more points as owned
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.5)
```

## Advanced Usage

### Loading Board State from Array

```python
# Load from a flat array (reading left-to-right, top-to-bottom)
board_state = [
    0, 0, 0, 1, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 0, 0, 0, 0,
    # ... (81 values for 9x9)
]

goban = Goban(9, 9)
idx = 0
for y in range(9):
    for x in range(9):
        goban.board[y][x] = board_state[idx]
        idx += 1
```

### Converting to/from SGF Coordinates

```python
def sgf_to_coords(sgf_move: str) -> tuple:
    """Convert SGF coordinate like 'dd' to (x, y)."""
    x = ord(sgf_move[0]) - ord('a')
    y = ord(sgf_move[1]) - ord('a')
    return (x, y)

def coords_to_sgf(x: int, y: int) -> str:
    """Convert (x, y) to SGF coordinate."""
    return chr(ord('a') + x) + chr(ord('a') + y)

# Usage
x, y = sgf_to_coords('dd')  # (3, 3)
goban.board[y][x] = BLACK
```

### Working with Different Rule Sets

```python
# The estimator works with any ruleset, but you may want to adjust:

# For Chinese rules (area scoring)
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.4)
# Count all marked points as territory

# For Japanese rules (territory scoring)
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.4)
# Only count empty marked points, stones are already counted
```

## API Reference

### Goban Class

#### Constructor
```python
Goban(width: int, height: int)
```

#### Main Methods

**estimate()**
```python
def estimate(
    self,
    player_to_move: Color,
    num_iterations: int,
    tolerance: float,
    debug: bool = False
) -> Grid
```

Runs the score estimation algorithm.

**Board Access**
```python
goban.board[y][x]  # Get/set stone at position
goban[y][x]        # Alternative access
goban.at(Point(x, y))  # Access via Point object
```

### Grid Class

A 2D grid used for board state and results.

```python
grid[y][x]           # Access value
grid[Point(x,y)]     # Access via Point
grid.sum()           # Sum all values
grid.clear()         # Clear to zeros
```

### Color Constants

```python
BLACK = 1
WHITE = -1
EMPTY = 0
```

### Point Class

```python
p = Point(x, y)
p.x  # x coordinate
p.y  # y coordinate
```

### Vec Class

Internal vector class for managing collections of Points.

## Examples

See `examples.py` for complete working examples:
- Simple corner positions
- Dead stone detection
- Large board estimation
- Parameter comparison

Run examples:
```bash
python examples.py
```

Run tests:
```bash
python test_score_estimator.py
```

## Algorithm Overview

The estimator uses these steps:

1. **False Eye Detection**: Identifies and fills false eyes
2. **Seki Detection**: Finds probable seki situations
3. **Monte Carlo Rollouts**: Simulates random games
4. **Territory Analysis**: Computes ownership based on simulations
5. **Dead Stone Detection**: Identifies stones that should be removed

The algorithm is the same as the C++ version used on online-go.com.

## Performance

Typical performance on modern hardware:
- 9x9 board, 1000 iterations: ~0.5-1 second
- 13x13 board, 1000 iterations: ~1-2 seconds
- 19x19 board, 1000 iterations: ~2-4 seconds

For production use, consider running estimation in a background thread.

## Limitations

- The estimator is optimized for end-game positions
- Very complex positions may need more iterations
- Seki detection is heuristic-based and may not catch all cases
- The algorithm assumes both players play reasonably (not perfectly)

## Troubleshooting

**Import Error**
```python
# Make sure you're in the right directory or have installed the package
pip install -e .
```

**Slow Performance**
```python
# Reduce iterations for faster results
result = goban.estimate(BLACK, num_iterations=500, tolerance=0.4)
```

**Unexpected Results**
```python
# Try adjusting tolerance
result = goban.estimate(BLACK, num_iterations=1000, tolerance=0.3)

# Or increase iterations
result = goban.estimate(BLACK, num_iterations=2000, tolerance=0.4)
```
