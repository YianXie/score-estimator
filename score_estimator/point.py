"""Point class representing a coordinate on the Go board."""


class Point:
    """Represents a coordinate (x, y) on the Go board."""
    
    __slots__ = ['x', 'y']
    
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.y, self.x) < (other.y, other.x)
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"
