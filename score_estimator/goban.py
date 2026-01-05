"""Goban class implementing the Go score estimator and dead stone removal algorithm."""

import random
from typing import Tuple
from .color import Color, EMPTY, BLACK, WHITE
from .point import Point
from .vec import Vec
from .grid import Grid


class Goban:
    """
    Go board with score estimation and dead stone removal capabilities.
    
    This implementation maintains the exact algorithm from the C++ version.
    """
    
    # Result codes
    OK = 0
    ILLEGAL = 1
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.board = Grid(width, height)
        self.do_ko_check = 0
        self.possible_ko = Point(-1, -1)
        
        self.global_visited = Grid(width, height)
        self.last_visited_counter = 1
    
    def __getitem__(self, key):
        """Access board by [Point] or [y]."""
        return self.board[key]
    
    def __setitem__(self, key, value):
        """Set board value by [Point] or [y]."""
        self.board[key] = value
    
    def at(self, p: Point) -> int:
        """Get value at Point."""
        return self.board[p]
    
    def set_board_size(self, width: int, height: int):
        """Set the board size."""
        self.width = width
        self.height = height
        self.board.width = width
        self.board.height = height
        self.global_visited.width = width
        self.global_visited.height = height
        
        self.board.clear()
        self.global_visited.clear()
    
    def estimate(self, player_to_move: Color, num_iterations: int, 
                 tolerance: float, debug: bool = False) -> Grid:
        """
        Estimate the score and mark dead stones.
        
        Args:
            player_to_move: The player to move next (BLACK or WHITE)
            num_iterations: Number of rollout iterations
            tolerance: Threshold for determining ownership (0.0-1.0)
            debug: Enable debug output
            
        Returns:
            Grid with ownership marked (1=black, -1=white, 0=dame/unsure)
        """
        # Fill false eyes
        false_eyes = self.get_false_eyes()
        self.fill_false_eyes(false_eyes)
        
        # Look for seki situations
        seki_pass_iterations = num_iterations
        seki_pass = self.rollout(seki_pass_iterations, player_to_move, False)
        seki = self.scan_for_seki(num_iterations, 0.2, seki_pass)
        
        # Horseshoe bias
        horseshoe_bias = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if self.board[p] == 0 and (self.is_safe_horseshoe(p, BLACK) or 
                                           self.is_safe_horseshoe(p, WHITE)):
                    neighbors = Vec()
                    self.board.get_neighbors(p, neighbors)
                    for i in range(neighbors.size):
                        gr = self.board.group(neighbors[i])
                        horseshoe_bias.add(gr, 1)
        
        horseshoe_bias *= self.board
        horseshoe_bias *= int(num_iterations * (tolerance / 4))
        
        ret = Grid(self.width, self.height)
        pass1 = Grid(self.width, self.height)
        tolerance_scale = 1
        
        tolerance *= tolerance_scale
        
        bias = Grid(self.width, self.height)
        territory_map = self.compute_territory()
        group_map = self.compute_group_map()
        liberty_map = self.compute_liberties(group_map)
        strong_life = self.compute_strong_life(group_map, territory_map, liberty_map)
        
        bias += horseshoe_bias
        
        tolerance /= tolerance_scale
        
        # Main rollout pass
        pass1_iterations = num_iterations
        pass1 = self.rollout(pass1_iterations, player_to_move, True, strong_life, bias, seki)
        dead = self.get_dead(pass1_iterations, tolerance, pass1)
        
        # Create result board based on rollout results
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                # If we're confident about ownership, mark it
                if pass1[y][x] > num_iterations * tolerance:
                    ret[y][x] = 1
                elif pass1[y][x] < num_iterations * -tolerance:
                    ret[y][x] = -1
                # Otherwise it's probably dame
                else:
                    if self.board[y][x]:
                        if abs(pass1[y][x]) < num_iterations * tolerance / 3:
                            ret[y][x] = 0
                        else:
                            ret[y][x] = 1 if pass1[y][x] > 0 else -1
                    else:
                        ret[y][x] = 0
        
        # Fill holes that can only reach one color
        for y in range(self.height):
            for x in range(self.width):
                group = Vec()
                neighbors = Vec()
                p = Point(x, y)
                if ret[p] == 0:
                    self.board.group_and_neighbors(p, group, neighbors)
                    if ret.all_not_equal_to(neighbors, WHITE):
                        ret.set(group, BLACK)
                    elif ret.all_not_equal_to(neighbors, BLACK):
                        ret.set(group, WHITE)
        
        return ret
    
    def scan_for_seki(self, num_iterations: int, tolerance: float, 
                      rollout_pass: Grid) -> Grid:
        """Look for probable seki situations."""
        seki = Grid(self.width, self.height)
        visited = Grid(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                group = Vec()
                neighbors = Vec()
                
                if visited[p]:
                    continue
                
                self.board.group_and_neighbors(p, group, neighbors)
                visited.set(group, 1)
                
                for color in [BLACK, WHITE]:
                    other = -color
                    
                    if (self.board[p] == color and 
                        rollout_pass.all_abs_lte(group, num_iterations * tolerance)):
                        neighboring = self.board.match(neighbors, other)
                        my_liberties = self.board.count_equal(neighbors, EMPTY)
                        
                        # Check for seki with neighboring group
                        if rollout_pass.any_abs_lte(neighboring, num_iterations * tolerance):
                            in_seki = True
                            
                            for i in range(neighboring.size):
                                if abs(rollout_pass[neighboring[i]]) < num_iterations * tolerance:
                                    neighbor_group = Vec()
                                    neighbor_neighbors = Vec()
                                    self.board.group_and_neighbors(neighboring[i], 
                                                                   neighbor_group, 
                                                                   neighbor_neighbors)
                                    
                                    neighbor_liberties = self.board.count_equal(neighbor_neighbors, EMPTY)
                                    if neighbor_liberties != my_liberties:
                                        in_seki = False
                            
                            if in_seki:
                                seki.set(group, 1)
                                territory = self.board.match(neighbors, EMPTY)
                                seki.set(territory, 1)
        
        return seki
    
    def rollout(self, num_iterations: int, player_to_move: Color,
                pullup_life_based_on_neighboring_territory: bool = True,
                life_map: Grid = None, bias: Grid = None, seki: Grid = None) -> Grid:
        """
        Play num_iterations random matches.
        
        Args:
            num_iterations: Number of random games to simulate
            player_to_move: Starting player
            pullup_life_based_on_neighboring_territory: Adjust group scores based on territory
            life_map: Bias map for assuming spots are alive
            bias: Additional bias grid
            seki: Grid marking seki positions
            
        Returns:
            Grid with accumulated scores from all rollouts
        """
        if life_map is None:
            life_map = Grid(self.width, self.height)
        if bias is None:
            bias = Grid(self.width, self.height)
        if seki is None:
            seki = Grid(self.width, self.height)
        
        ret = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                ret[y][x] = bias[y][x]
        
        for i in range(num_iterations):
            # Create a copy and play out
            t = Goban(self.width, self.height)
            for y in range(self.height):
                for x in range(self.width):
                    t.board[y][x] = self.board[y][x]
            
            t.play_out_position(player_to_move, life_map, seki)
            
            # Fill in territory
            for y in range(self.height):
                for x in range(self.width):
                    p = Point(x, y)
                    if t[p] == 0:
                        if t.is_territory(p, BLACK):
                            t.fill_territory(p, BLACK)
                        if t.is_territory(p, WHITE):
                            t.fill_territory(p, WHITE)
            
            # Track how many times each spot was black or white
            for y in range(self.height):
                for x in range(self.width):
                    ret[y][x] += t.board[y][x]
        
        # Pull up group scores based on neighboring territory
        visited = Grid(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                
                if not visited[p] and self.board[p]:
                    group = Vec()
                    neighbors = Vec()
                    self.board.group_and_neighbors(p, group, neighbors)
                    minmax = ret.minmax(group)
                    visited.set(group, 1)
                    
                    if pullup_life_based_on_neighboring_territory:
                        # Adjust based on neighboring territory
                        if minmax < 0:
                            minmax = min(ret.min(neighbors), minmax)
                        
                        if minmax > 0:
                            minmax = max(ret.max(neighbors), minmax)
                    
                    ret.set(group, minmax)
        
        return ret
    
    def compute_group_map(self) -> Grid:
        """Uniquely label strings of groups on the board."""
        ret = Grid(self.width, self.height)
        cur_group = 1
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if ret[p] == 0:
                    self.board.trace_group(p, ret, cur_group)
                    cur_group += 1
        
        return ret
    
    def compute_territory(self) -> Grid:
        """
        Mark each location with positive/negative size of territory.
        Negative for white, positive for black, zero if not territory.
        """
        ret = Grid(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if ret[p]:
                    continue
                
                group = Vec()
                neighbors = Vec()
                if self.board[p] == 0 and self.is_territory(p, BLACK):
                    self.board.group_and_neighbors(p, group, neighbors)
                    ret.set(group, group.size * BLACK)
                if self.board[p] == 0 and self.is_territory(p, WHITE):
                    self.board.group_and_neighbors(p, group, neighbors)
                    ret.set(group, group.size * WHITE)
        
        return ret
    
    def compute_liberties(self, group_map: Grid) -> Grid:
        """
        Compute liberties for groups on the board.
        For empty spaces, compute number of black minus white stones touching.
        """
        ret = Grid(self.width, self.height)
        visited = Grid(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if visited[p]:
                    continue
                
                group = Vec()
                neighbors = Vec()
                self.board.group_and_neighbors(p, group, neighbors)
                visited.set(group, 1)
                
                liberty_count = 0
                if self[p] == 0:
                    # Sum of all adjacent black - all adjacent white
                    for i in range(neighbors.size):
                        liberty_count += self[neighbors[i]]
                else:
                    # Liberties of stone group
                    for i in range(neighbors.size):
                        if self[neighbors[i]] == 0:
                            liberty_count += self[p]
                
                ret.set(group, liberty_count)
        
        return ret
    
    def compute_strong_life(self, groups: Grid, territory: Grid, 
                           liberties: Grid) -> Grid:
        """
        Flag spaces that are part of a string of like-colored stones and territory
        where the stones have combined two or more eyes.
        """
        ret = Grid(self.width, self.height)
        visited = Grid(self.width, self.height)
        
        unified_territory_and_stones = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if self.board[p] == 0:
                    if territory[p] <= -1:
                        unified_territory_and_stones[p] = -1
                    elif territory[p] >= 1:
                        unified_territory_and_stones[p] = 1
                    else:
                        unified_territory_and_stones[p] = 0
                else:
                    unified_territory_and_stones[p] = self.board[p]
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if visited[p]:
                    continue
                
                group = Vec()
                neighbors = Vec()
                unified_territory_and_stones.group_and_neighbors(p, group, neighbors)
                
                num_eyes = 0
                num_territory = 0
                for i in range(group.size):
                    if visited[group[i]]:
                        continue
                    if territory[group[i]]:
                        territory_group = Vec()
                        territory_neighbors = Vec()
                        self.board.group_and_neighbors(group[i], territory_group, 
                                                       territory_neighbors)
                        visited.set(territory_group, 1)
                        num_eyes += 1
                        num_territory += territory_group.size
                
                visited.set(group, 1)
                if num_eyes >= 2 or num_territory >= 5:
                    ret.set(group, num_territory)
        
        return ret
    
    def get_dead(self, num_iterations: int, tolerance: float, 
                 rollout_pass: Grid) -> Vec:
        """
        Return a list of stones that are probably dead based on rollout results.
        """
        removed = Vec()
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                # If we're confident about ownership
                if rollout_pass[p] > num_iterations * tolerance:
                    if self.board[p] == -1:  # Should be black but was white
                        removed.push(p)
                elif rollout_pass[p] < num_iterations * -tolerance:
                    if self.board[p] == 1:  # Should be white but was black
                        removed.push(p)
                else:
                    # No idea who owns it, but there's a stone? Probably dead
                    if self.board[p] != 0:
                        removed.push(p)
        
        return removed
    
    def get_false_eyes(self) -> Vec:
        """Return a list of false eyes detected."""
        false_eyes = Vec()
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if self.at(p) == 0:
                    neighbors = Vec()
                    corners = Vec()
                    self.board.get_neighbors(p, neighbors)
                    self.board.get_corner_points(p, corners)
                    
                    if self.board.get_min_liberties_of_surrounding_groups(p) > 1:
                        continue
                    
                    if (self.board.all_equal_to(neighbors, BLACK) and 
                        self.board.count_equal(corners, WHITE) >= (corners.size >> 1)):
                        false_eyes.push(p)
                    elif (self.board.all_equal_to(neighbors, WHITE) and 
                          self.board.count_equal(corners, BLACK) >= (corners.size >> 1)):
                        false_eyes.push(p)
        
        return false_eyes
    
    def fill_false_eyes(self, false_eyes: Vec):
        """Fill false eyes, removing stones if appropriate."""
        for i in range(false_eyes.size):
            neighbors = Vec()
            dummy = Vec()
            self.board.get_neighbors(false_eyes[i], neighbors)
            
            self.place_and_remove(false_eyes[i], self.board[neighbors[0]], dummy)
    
    def is_territory(self, pt: Point, player: Color) -> bool:
        """Check if a point is territory for a player."""
        tocheck = Vec()
        neighbors = Vec()
        visited_counter = self.last_visited_counter + 1
        self.last_visited_counter = visited_counter
        adjacent_player_stones = 0
        
        tocheck.push(pt)
        self.global_visited[pt] = visited_counter
        
        while tocheck.size:
            p = tocheck.remove(0)
            if self[p] == 0:
                self.board.get_neighbors(p, neighbors)
                for i in range(neighbors.size):
                    neighbor = neighbors[i]
                    if self.global_visited[neighbor] == visited_counter:
                        continue
                    self.global_visited[neighbor] = visited_counter
                    tocheck.push(neighbor)
            else:
                if self[p] != player:
                    return False
                adjacent_player_stones += 1
        
        # If no adjacent player stones, we have a blank board
        return adjacent_player_stones > 0
    
    def fill_territory(self, pt: Point, player: Color):
        """Fill empty territory with player color."""
        tocheck = Vec()
        neighbors = Vec()
        visited_counter = self.last_visited_counter + 1
        self.last_visited_counter = visited_counter
        
        tocheck.push(pt)
        self.global_visited[pt] = visited_counter
        
        while tocheck.size:
            p = tocheck.remove(0)
            if self[p] == 0:
                self[p] = player
                self.board.get_neighbors(p, neighbors)
                for i in range(neighbors.size):
                    neighbor = neighbors[i]
                    if self.global_visited[neighbor] == visited_counter:
                        continue
                    self.global_visited[neighbor] = visited_counter
                    tocheck.push(neighbor)
    
    def play_out_position(self, player_to_move: Color, life_map: Grid, seki: Grid):
        """Play out random moves until no more legal moves."""
        self.do_ko_check = 0
        self.possible_ko = Point(-1, -1)
        
        possible_moves = Vec()
        illegal_moves = Vec()
        
        for y in range(self.height):
            for x in range(self.width):
                p = Point(x, y)
                if self.board[p] == 0 and seki[p] == 0 and life_map[p] == 0:
                    possible_moves.push(Point(x, y))
        
        sanity = 1000
        passed = False
        while possible_moves.size > 0 and sanity > 0:
            sanity -= 1
            move_idx = random.randint(0, possible_moves.size - 1)
            mv = possible_moves[move_idx]
            
            if self.is_eye(mv, player_to_move):
                illegal_moves.push(possible_moves.remove(move_idx))
                
                if possible_moves.size == 0:
                    if passed:
                        break
                    passed = True
                    possible_moves += illegal_moves
                    illegal_moves.clear()
                    player_to_move = -player_to_move
                continue
            
            result = self.place_and_remove(mv, player_to_move, possible_moves)
            if result == self.OK:
                passed = False
                possible_moves.remove(move_idx)
                player_to_move = -player_to_move
                possible_moves += illegal_moves
                illegal_moves.clear()
                continue
            elif result == self.ILLEGAL:
                illegal_moves.push(possible_moves.remove(move_idx))
                
                if possible_moves.size == 0:
                    if passed:
                        break
                    passed = True
                    possible_moves += illegal_moves
                    illegal_moves.clear()
                    player_to_move = -player_to_move
                
                continue
    
    def place_and_remove(self, move: Point, player: Color, possible_moves: Vec) -> int:
        """Place a stone and remove captured groups."""
        if self.do_ko_check:
            if move == self.possible_ko:
                return self.ILLEGAL
        
        reset_ko_check = True
        removed = False
        neighbors = Vec()
        
        self.board.get_neighbors(move, neighbors)
        
        self[move] = player
        self.last_visited_counter += 1
        for i in range(neighbors.size):
            if self[neighbors[i]] == -player:
                if (self.global_visited[neighbors[i]] != self.last_visited_counter and
                    not self.has_liberties(neighbors[i])):
                    if self.remove_group(neighbors[i], possible_moves) == 1:
                        reset_ko_check = False
                        self.do_ko_check = 1
                        self.possible_ko = neighbors[i]
                    removed = True
        
        if not removed:
            if not self.has_liberties(move):
                self[move] = 0
                return self.ILLEGAL
        
        if reset_ko_check:
            self.do_ko_check = False
        
        return self.OK
    
    def has_liberties(self, pt: Point) -> bool:
        """Check if a group has liberties."""
        tocheck = Vec()
        w_1 = self.width - 1
        h_1 = self.height - 1
        my_color = self[pt]
        my_visited_counter = self.last_visited_counter + 1
        self.last_visited_counter = my_visited_counter
        
        tocheck.push(pt)
        self.global_visited[pt] = my_visited_counter
        
        while tocheck.size:
            p = tocheck.remove(tocheck.size - 1)
            
            # Check all four directions
            if p.x > 0:
                neighbor = Point(p.x - 1, p.y)
                c = self.board[neighbor.y][neighbor.x]
                if c == 0:
                    return True
                if c == my_color and self.global_visited[neighbor.y][neighbor.x] != my_visited_counter:
                    self.global_visited[neighbor.y][neighbor.x] = my_visited_counter
                    tocheck.push(neighbor)
            
            if p.x < w_1:
                neighbor = Point(p.x + 1, p.y)
                c = self.board[neighbor.y][neighbor.x]
                if c == 0:
                    return True
                if c == my_color and self.global_visited[neighbor.y][neighbor.x] != my_visited_counter:
                    self.global_visited[neighbor.y][neighbor.x] = my_visited_counter
                    tocheck.push(neighbor)
            
            if p.y > 0:
                neighbor = Point(p.x, p.y - 1)
                c = self.board[neighbor.y][neighbor.x]
                if c == 0:
                    return True
                if c == my_color and self.global_visited[neighbor.y][neighbor.x] != my_visited_counter:
                    self.global_visited[neighbor.y][neighbor.x] = my_visited_counter
                    tocheck.push(neighbor)
            
            if p.y < h_1:
                neighbor = Point(p.x, p.y + 1)
                c = self.board[neighbor.y][neighbor.x]
                if c == 0:
                    return True
                if c == my_color and self.global_visited[neighbor.y][neighbor.x] != my_visited_counter:
                    self.global_visited[neighbor.y][neighbor.x] = my_visited_counter
                    tocheck.push(neighbor)
        
        return False
    
    def remove_group(self, move: Point, possible_moves: Vec) -> int:
        """Remove a captured group."""
        visited = Grid(self.width, self.height)
        tocheck = Vec()
        neighbors = Vec()
        n_removed = 0
        my_color = self[move]
        
        tocheck.push(move)
        visited[move] = True
        
        while tocheck.size:
            p = tocheck.remove(0)
            
            self[p] = 0
            possible_moves.push(p)
            n_removed += 1
            
            self.board.get_neighbors(p, neighbors)
            
            for i in range(neighbors.size):
                neighbor = neighbors[i]
                if visited[neighbor]:
                    continue
                visited[neighbor] = True
                
                c = self[neighbor]
                if c == my_color:
                    tocheck.push(neighbor)
        
        return n_removed
    
    def would_self_atari(self, pt: Point, player: Color) -> bool:
        """Check if a move would be self-atari."""
        neighbors = Vec()
        self.board.get_neighbors(pt, neighbors)
        
        if self.board.count_equal(neighbors, 0):
            return False
        
        for i in range(neighbors.size):
            if self.board[neighbors[i]] == -player:
                group = Vec()
                group_neighbors = Vec()
                self.board.group_and_neighbors(neighbors[i], group, group_neighbors)
                if self.board.count_equal(group_neighbors, 0) <= 1:
                    return False
        
        connected_group_surrounding_points = Vec()
        groups_connecting = Vec()
        for i in range(neighbors.size):
            if self.board[neighbors[i]] == player:
                groups_connecting.push(neighbors[i])
        groups_connecting.push(pt)
        if self.board.has_less_liberties_than(groups_connecting, 2):
            return True
        
        return False
    
    def is_eye(self, pt: Point, player: Color) -> bool:
        """Check if a point is an eye for a player."""
        if ((pt.x == 0 or self.board[pt.y][pt.x - 1] == player) and
            (pt.x == self.width - 1 or self.board[pt.y][pt.x + 1] == player) and
            (pt.y == 0 or self.board[pt.y - 1][pt.x] == player) and
            (pt.y == self.height - 1 or self.board[pt.y + 1][pt.x] == player)):
            
            corners = Vec()
            self.board.get_corner_points(pt, corners)
            if (self.board.count_equal(corners, -player) >= (corners.size >> 1) and
                self.board.get_min_liberties_of_surrounding_groups(pt) <= 1):
                # False eye
                return False
            
            return True
        return False
    
    def is_safe_horseshoe(self, pt: Point, player: Color) -> bool:
        """Check if point is a safe horseshoe shape (U shape but not eye)."""
        neighbors = Vec()
        self.board.get_neighbors(pt, neighbors)
        
        if (self.board.count_equal(neighbors, player) >= neighbors.size - 1 and
            self.board.count_equal(neighbors, -player) == 0):
            corners = Vec()
            self.board.get_corner_points(pt, corners)
            
            if (self.board.count_equal(corners, -player) >= (corners.size >> 1) and
                self.board.get_min_liberties_of_surrounding_groups(pt) <= 1):
                # Looks like a false eye
                return False
            
            return True
        
        return False
    
    def set_size(self, width: int, height: int):
        """Set the board size."""
        self.width = width
        self.height = height
    
    def clear_board(self):
        """Clear the board."""
        self.board.clear()
