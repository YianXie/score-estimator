"""Grid class for 2D board operations."""

from typing import List, Callable
from .point import Point
from .vec import Vec


MAX_WIDTH = 25
MAX_HEIGHT = 25


class Grid:
    """A 2D grid used for various purposes while tracking game and estimation state."""
    
    def __init__(self, width: int = -1, height: int = -1):
        self.width = width if width > 0 else 19
        self.height = height if height > 0 else 19
        self._data: List[List[int]] = [[0] * MAX_WIDTH for _ in range(MAX_HEIGHT)]
        self.clear()
    
    def __getitem__(self, key):
        """Access grid by [y][x] or [Point]."""
        if isinstance(key, Point):
            return self._data[key.y][key.x]
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Set grid value by [Point] or [y][x]."""
        if isinstance(key, Point):
            self._data[key.y][key.x] = value
        else:
            self._data[key] = value
    
    def at(self, p: Point) -> int:
        """Get value at Point."""
        return self._data[p.y][p.x]
    
    def set_at(self, p: Point, value: int):
        """Set value at Point."""
        self._data[p.y][p.x] = value
    
    def __add__(self, other: 'Grid') -> 'Grid':
        """Add two grids element-wise."""
        ret = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                ret[y][x] = self[y][x] + other[y][x]
        return ret
    
    def __iadd__(self, other: 'Grid') -> 'Grid':
        """Add another grid to this one element-wise."""
        for y in range(self.height):
            for x in range(self.width):
                self[y][x] += other[y][x]
        return self
    
    def __imul__(self, other) -> 'Grid':
        """Multiply this grid element-wise by another grid or scalar."""
        if isinstance(other, Grid):
            for y in range(self.height):
                for x in range(self.width):
                    self[y][x] *= other[y][x]
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self[y][x] *= other
        return self
    
    def __mul__(self, other) -> 'Grid':
        """Multiply grid element-wise by another grid or scalar."""
        ret = Grid(self.width, self.height)
        ret._data = [row[:] for row in self._data]
        ret *= other
        return ret
    
    def clear(self, value: int = 0):
        """Clear all locations with the provided value."""
        for y in range(self.height):
            for x in range(self.width):
                self._data[y][x] = value
    
    def trace_group(self, starting_point: Point, destination: 'Grid', value: int):
        """Flood match all similar values starting at starting_point."""
        tocheck = Vec()
        neighbors = Vec()
        visited = Grid(self.width, self.height)
        matching_value = self[starting_point]
        
        tocheck.push(starting_point)
        visited[starting_point] = 1
        
        while tocheck.size:
            p = tocheck.remove(0)
            if self[p] == matching_value:
                destination[p] = value
                self.get_neighbors(p, neighbors)
                for i in range(neighbors.size):
                    neighbor = neighbors[i]
                    if visited[neighbor]:
                        continue
                    visited[neighbor] = 1
                    tocheck.push(neighbor)
    
    def group_and_neighbors(self, starting_point, group: Vec, out_neighbors: Vec):
        """Get group and neighbors for a point or list of points."""
        if isinstance(starting_point, Point):
            starting_points = Vec()
            starting_points.push(starting_point)
        else:
            starting_points = starting_point
        
        tocheck = Vec()
        neighbors = Vec()
        visited = Grid(self.width, self.height)
        matching_value = self[starting_points[0]]
        
        for i in range(starting_points.size):
            tocheck.push(starting_points[i])
            visited[starting_points[i]] = 1
        
        while tocheck.size:
            p = tocheck.remove(0)
            if self[p] == matching_value:
                group.push(p)
                self.get_neighbors(p, neighbors)
                for i in range(neighbors.size):
                    neighbor = neighbors[i]
                    if visited[neighbor]:
                        continue
                    visited[neighbor] = 1
                    tocheck.push(neighbor)
            else:
                out_neighbors.push(p)
    
    def has_less_liberties_than(self, starting_points: Vec, amount: int) -> bool:
        """Check if the sum of liberties is less than the given amount."""
        tocheck = Vec()
        neighbors = Vec()
        visited = Grid(self.width, self.height)
        matching_value = self[starting_points[0]]
        total_liberties = 0
        
        for i in range(starting_points.size):
            tocheck.push(starting_points[i])
            visited[starting_points[i]] = 1
        
        while tocheck.size:
            p = tocheck.remove(0)
            self.get_neighbors(p, neighbors)
            for i in range(neighbors.size):
                neighbor = neighbors[i]
                if visited[neighbor]:
                    continue
                visited[neighbor] = 1
                
                v = self[neighbor]
                if v == matching_value:
                    tocheck.push(neighbor)
                elif v == 0:
                    total_liberties += 1
                    if total_liberties >= amount:
                        return False
        
        return True
    
    def group(self, starting_point: Point) -> Vec:
        """Get all points in the same group as starting_point."""
        tocheck = Vec()
        ret = Vec()
        neighbors = Vec()
        visited = Grid(self.width, self.height)
        matching_value = self[starting_point]
        
        tocheck.push(starting_point)
        visited[starting_point] = 1
        
        while tocheck.size:
            p = tocheck.remove(0)
            if self[p] == matching_value:
                ret.push(p)
                self.get_neighbors(p, neighbors)
                for i in range(neighbors.size):
                    neighbor = neighbors[i]
                    if visited[neighbor]:
                        continue
                    visited[neighbor] = 1
                    tocheck.push(neighbor)
        
        return ret
    
    def match(self, group: Vec, value: int) -> Vec:
        """Return all points in group which equal value."""
        ret = Vec()
        for i in range(group.size):
            if self.at(group[i]) == value:
                ret.push(group[i])
        return ret
    
    def not_match(self, group: Vec, value: int) -> Vec:
        """Return all points in group which don't equal value."""
        ret = Vec()
        for i in range(group.size):
            if self.at(group[i]) != value:
                ret.push(group[i])
        return ret
    
    def minmax(self, group: Vec) -> int:
        """Return the value with greatest magnitude."""
        ret = self[group[0]]
        for i in range(group.size):
            if abs(ret) < abs(self[group[i]]):
                ret = self[group[i]]
        return ret
    
    def min(self, group: Vec) -> int:
        """Return minimum value in group."""
        ret = self[group[0]]
        for i in range(group.size):
            if ret > self[group[i]]:
                ret = self[group[i]]
        return ret
    
    def max(self, group: Vec) -> int:
        """Return maximum value in group."""
        ret = self[group[0]]
        for i in range(group.size):
            if ret < self[group[i]]:
                ret = self[group[i]]
        return ret
    
    def set(self, group: Vec, value: int):
        """Set all points in group to value."""
        for i in range(group.size):
            self[group[i]] = value
    
    def add(self, group: Vec, value: int):
        """Add value to all points in group."""
        for i in range(group.size):
            self[group[i]] += value
    
    def all_equal_to(self, group: Vec, value: int) -> bool:
        """Check if all points in group equal value."""
        for i in range(group.size):
            if self.at(group[i]) != value:
                return False
        return True
    
    def all_not_equal_to(self, group: Vec, value: int) -> bool:
        """Check if all points in group don't equal value."""
        for i in range(group.size):
            if self.at(group[i]) == value:
                return False
        return True
    
    def any_abs_lte(self, group: Vec, value: int) -> bool:
        """Check if any point in group has absolute value <= value."""
        for i in range(group.size):
            if abs(self.at(group[i])) <= value:
                return True
        return False
    
    def any_abs_gte(self, group: Vec, value: int) -> bool:
        """Check if any point in group has absolute value >= value."""
        for i in range(group.size):
            if abs(self.at(group[i])) >= value:
                return True
        return False
    
    def all_abs_lte(self, group: Vec, value: int) -> bool:
        """Check if all points in group have absolute value <= value."""
        for i in range(group.size):
            if abs(self.at(group[i])) > value:
                return False
        return True
    
    def all_abs_gte(self, group: Vec, value: int) -> bool:
        """Check if all points in group have absolute value >= value."""
        for i in range(group.size):
            if abs(self.at(group[i])) < value:
                return False
        return True
    
    def any_lte(self, group: Vec, value: int) -> bool:
        """Check if any point in group has value <= value."""
        for i in range(group.size):
            if self.at(group[i]) <= value:
                return True
        return False
    
    def any_gte(self, group: Vec, value: int) -> bool:
        """Check if any point in group has value >= value."""
        for i in range(group.size):
            if self.at(group[i]) >= value:
                return True
        return False
    
    def all_lte(self, group: Vec, value: int) -> bool:
        """Check if all points in group have value <= value."""
        for i in range(group.size):
            if self.at(group[i]) > value:
                return False
        return True
    
    def all_gte(self, group: Vec, value: int) -> bool:
        """Check if all points in group have value >= value."""
        for i in range(group.size):
            if self.at(group[i]) < value:
                return False
        return True
    
    def count_equal(self, group: Vec, value: int) -> int:
        """Count points in group that equal value."""
        ret = 0
        for i in range(group.size):
            if self.at(group[i]) == value:
                ret += 1
        return ret
    
    def get_neighbors(self, pt: Point, output: Vec):
        """Get all valid neighboring points."""
        output.size = 0
        output.points = []
        if pt.x > 0:
            output.push(Point(pt.x - 1, pt.y))
        if pt.x + 1 < self.width:
            output.push(Point(pt.x + 1, pt.y))
        if pt.y > 0:
            output.push(Point(pt.x, pt.y - 1))
        if pt.y + 1 < self.height:
            output.push(Point(pt.x, pt.y + 1))
    
    def get_corner_points(self, pt: Point, output: Vec):
        """Get all valid diagonal corner points."""
        output.size = 0
        output.points = []
        if pt.x > 0 and pt.y > 0:
            output.push(Point(pt.x - 1, pt.y - 1))
        if pt.x + 1 < self.width and pt.y > 0:
            output.push(Point(pt.x + 1, pt.y - 1))
        if pt.x > 0 and pt.y + 1 < self.height:
            output.push(Point(pt.x - 1, pt.y + 1))
        if pt.x + 1 < self.width and pt.y + 1 < self.height:
            output.push(Point(pt.x + 1, pt.y + 1))
    
    def sum(self, group: Vec = None) -> int:
        """Sum all points in group or entire grid."""
        if group is None:
            total = 0
            for y in range(self.height):
                for x in range(self.width):
                    total += self._data[y][x]
            return total
        else:
            total = 0
            for i in range(group.size):
                total += self._data[group[i].y][group[i].x]
            return total
    
    def get_min_liberties_of_surrounding_groups(self, pt: Point) -> int:
        """Count liberties of neighboring groups, return minimum."""
        neighbors = Vec()
        self.get_neighbors(pt, neighbors)
        
        ret = 99999
        
        for i in range(neighbors.size):
            group = Vec()
            group_neighbors = Vec()
            self.group_and_neighbors(neighbors[i], group, group_neighbors)
            
            liberties = self.count_equal(group_neighbors, 0)
            ret = min(ret, liberties)
        
        return ret
