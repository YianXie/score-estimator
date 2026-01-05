"""Vec class for managing collections of Points."""

from typing import List
from .point import Point


class Vec:
    """A vector/list of Points used throughout the algorithm."""
    
    def __init__(self):
        self.points: List[Point] = []
        self.size: int = 0
    
    def __getitem__(self, idx: int) -> Point:
        return self.points[idx]
    
    def __setitem__(self, idx: int, point: Point):
        self.points[idx] = point
    
    def push(self, point: Point):
        """Add a point to the vector."""
        self.points.append(point)
        self.size += 1
    
    def remove(self, idx: int) -> Point:
        """Remove and return the point at the given index."""
        ret = self.points[idx]
        self.points[idx] = self.points[self.size - 1]
        self.points.pop()
        self.size -= 1
        return ret
    
    def __iadd__(self, other: 'Vec'):
        """Add all points from another Vec to this one."""
        for i in range(other.size):
            self.push(other[i])
        return self
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return f"Vec({self.points[:self.size]})"
