"""
Example usage of the OGS Score Estimator Python library.

This demonstrates how to use the Python version of the score estimator
to estimate territory ownership and detect dead stones on a Go board.
"""

from score_estimator import Goban, BLACK, WHITE, EMPTY


def example_simple_corner():
    """Example 1: Simple corner position."""
    print("=" * 60)
    print("Example 1: Simple Corner Position")
    print("=" * 60)
    
    # Create a 9x9 board
    goban = Goban(9, 9)
    
    # Set up a simple corner position
    # Black stones in the 3-3 point area
    goban.board[6][2] = BLACK
    goban.board[6][3] = BLACK
    goban.board[6][4] = BLACK
    goban.board[7][2] = BLACK
    goban.board[8][2] = BLACK
    
    print("\nInitial board position:")
    print_board(goban)
    
    # Estimate the score
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=1000,
        tolerance=0.4
    )
    
    print("\nEstimated ownership (1=black, -1=white, 0=dame):")
    print_grid(result)
    
    # Calculate score
    score_diff = result.sum()
    print(f"\nScore difference: {score_diff}")
    print(f"(Positive means black is ahead)")


def example_with_dead_stones():
    """Example 2: Position with dead stones."""
    print("\n" + "=" * 60)
    print("Example 2: Position with Potentially Dead Stones")
    print("=" * 60)
    
    # Create a 9x9 board
    goban = Goban(9, 9)
    
    # Black territory with a captured white stone
    goban.board[3][3] = BLACK
    goban.board[3][4] = BLACK
    goban.board[3][5] = BLACK
    goban.board[4][3] = BLACK
    goban.board[4][5] = BLACK
    goban.board[5][3] = BLACK
    goban.board[5][4] = BLACK
    goban.board[5][5] = BLACK
    
    # White stone that should be detected as dead
    goban.board[4][4] = WHITE
    
    print("\nInitial board position:")
    print_board(goban)
    
    # Estimate the score
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=1000,
        tolerance=0.4
    )
    
    print("\nEstimated ownership (1=black, -1=white, 0=dame):")
    print_grid(result)
    
    # The white stone at [4][4] should be detected as dead (result will show BLACK)
    if result[4][4] == BLACK:
        print(f"\n✓ Correctly detected white stone at (4,4) as dead")
    
    score_diff = result.sum()
    print(f"\nScore difference: {score_diff}")


def example_larger_board():
    """Example 3: Larger board with multiple groups."""
    print("\n" + "=" * 60)
    print("Example 3: 19x19 Board with Multiple Groups")
    print("=" * 60)
    
    # Create a standard 19x19 board
    goban = Goban(19, 19)
    
    # Black corner (top-left)
    for i in range(3):
        goban.board[2][i+2] = BLACK
        goban.board[i+3][2] = BLACK
    
    # White corner (top-right)
    for i in range(3):
        goban.board[2][16-i] = WHITE
        goban.board[i+3][16] = WHITE
    
    # Black corner (bottom-left)
    for i in range(3):
        goban.board[16][i+2] = BLACK
        goban.board[15-i][2] = BLACK
    
    # White corner (bottom-right)
    for i in range(3):
        goban.board[16][16-i] = WHITE
        goban.board[15-i][16] = WHITE
    
    print("\nBoard has stones in all four corners")
    print("Running estimation...")
    
    # Estimate the score
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=2000,  # More iterations for larger board
        tolerance=0.35
    )
    
    # Count territory
    black_territory = sum(1 for y in range(19) for x in range(19) if result[y][x] > 0)
    white_territory = sum(1 for y in range(19) for x in range(19) if result[y][x] < 0)
    dame = sum(1 for y in range(19) for x in range(19) if result[y][x] == 0)
    
    print(f"\nTerritory count:")
    print(f"  Black: {black_territory} points")
    print(f"  White: {white_territory} points")
    print(f"  Dame:  {dame} points")
    
    score_diff = result.sum()
    print(f"\nScore difference: {score_diff}")


def example_custom_parameters():
    """Example 4: Using different estimation parameters."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Estimation Parameters")
    print("=" * 60)
    
    goban = Goban(9, 9)
    
    # Simple position
    goban.board[4][4] = BLACK
    goban.board[4][5] = BLACK
    goban.board[5][4] = BLACK
    
    print("\nComparing different tolerance values:")
    
    for tolerance in [0.25, 0.35, 0.45]:
        result = goban.estimate(
            player_to_move=BLACK,
            num_iterations=1000,
            tolerance=tolerance
        )
        score = result.sum()
        print(f"  Tolerance {tolerance}: Score difference = {score}")
    
    print("\nComparing different iteration counts:")
    
    for iterations in [500, 1000, 2000]:
        result = goban.estimate(
            player_to_move=BLACK,
            num_iterations=iterations,
            tolerance=0.4
        )
        score = result.sum()
        print(f"  {iterations} iterations: Score difference = {score}")


def print_board(goban: Goban):
    """Print a simple ASCII representation of the board."""
    symbols = {EMPTY: '.', BLACK: 'X', WHITE: 'O'}
    
    print("   ", end="")
    for x in range(goban.width):
        print(f"{x:2}", end=" ")
    print()
    
    for y in range(goban.height):
        print(f"{y:2} ", end="")
        for x in range(goban.width):
            print(f" {symbols[goban.board[y][x]]} ", end="")
        print()


def print_grid(grid):
    """Print a grid with numerical values."""
    print("   ", end="")
    for x in range(grid.width):
        print(f"{x:2}", end=" ")
    print()
    
    for y in range(grid.height):
        print(f"{y:2} ", end="")
        for x in range(grid.width):
            val = grid[y][x]
            if val > 0:
                print(f" X ", end="")
            elif val < 0:
                print(f" O ", end="")
            else:
                print(f" . ", end="")
        print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("OGS Score Estimator - Python Library Examples")
    print("=" * 60)
    
    example_simple_corner()
    example_with_dead_stones()
    example_larger_board()
    example_custom_parameters()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
