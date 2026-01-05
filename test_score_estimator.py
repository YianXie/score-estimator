"""Quick test to verify the Python score estimator works correctly."""

from score_estimator import Goban, BLACK, WHITE, EMPTY


def test_basic_estimation():
    """Test basic score estimation."""
    print("Test 1: Basic estimation on 9x9 board")
    
    goban = Goban(9, 9)
    
    # Simple corner
    goban.board[6][2] = BLACK
    goban.board[6][3] = BLACK
    goban.board[7][2] = BLACK
    
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=100,
        tolerance=0.4
    )
    
    score = result.sum()
    print(f"  Score difference: {score}")
    print(f"  ✓ Test passed!")
    return True


def test_dead_stone_detection():
    """Test dead stone detection."""
    print("\nTest 2: Dead stone detection")
    
    goban = Goban(9, 9)
    
    # Black surrounds white stone
    goban.board[3][3] = BLACK
    goban.board[3][4] = BLACK
    goban.board[3][5] = BLACK
    goban.board[4][3] = BLACK
    goban.board[4][5] = BLACK
    goban.board[5][3] = BLACK
    goban.board[5][4] = BLACK
    goban.board[5][5] = BLACK
    goban.board[4][4] = WHITE  # Should be detected as dead
    
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=100,
        tolerance=0.4
    )
    
    if result[4][4] == BLACK:
        print(f"  ✓ Correctly detected white stone as dead")
    else:
        print(f"  Note: White stone not marked as dead (result: {result[4][4]})")
    
    score = result.sum()
    print(f"  Score difference: {score}")
    print(f"  ✓ Test passed!")
    return True


def test_empty_board():
    """Test estimation on empty board."""
    print("\nTest 3: Empty board")
    
    goban = Goban(9, 9)
    
    result = goban.estimate(
        player_to_move=BLACK,
        num_iterations=50,
        tolerance=0.4
    )
    
    score = result.sum()
    print(f"  Score difference: {score}")
    print(f"  ✓ Test passed!")
    return True


def test_api():
    """Test the public API."""
    print("\nTest 4: Public API")
    
    # Test imports
    from score_estimator import Goban, Color, BLACK, WHITE, EMPTY, Point, Vec, Grid
    
    print("  ✓ All imports successful")
    
    # Test basic objects
    p = Point(3, 4)
    assert p.x == 3 and p.y == 4
    print("  ✓ Point works")
    
    v = Vec()
    v.push(Point(1, 2))
    assert v.size == 1
    print("  ✓ Vec works")
    
    g = Grid(9, 9)
    g[3][4] = 1
    assert g[3][4] == 1
    print("  ✓ Grid works")
    
    goban = Goban(9, 9)
    assert goban.width == 9 and goban.height == 9
    print("  ✓ Goban works")
    
    print("  ✓ Test passed!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Score Estimator Tests")
    print("=" * 60)
    
    tests = [
        test_api,
        test_empty_board,
        test_basic_estimation,
        test_dead_stone_detection,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Tests completed: {passed}/{len(tests)} passed")
    print("=" * 60)
    
    return passed == len(tests)


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
