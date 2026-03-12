"""Dungeon Escape Solver.

A knight must cross a linear dungeon of marble platforms (1) and lava pools (0).
Allowed moves: Jump (1 unit) or Prime Teleport (2, 3, or 5 units forward).
Uses BFS to find the minimum number of moves and the exact path.
"""

from typing import List, Optional, Set, Tuple
from collections import deque


# The set of allowed move distances (jump=1, prime teleport=2,3,5)
MOVE_DISTANCES: List[int] = [1, 2, 3, 5]


def solve_dungeon(dungeon: List[int]) -> Tuple[Optional[int], List[int]]:
    """Find the minimum number of moves to escape the dungeon.

    Uses breadth-first search to guarantee the shortest path. At each
    position the knight tries all allowed move distances. The first
    path that reaches or overshoots the last platform is optimal.

    Args:
        dungeon: List of 0s and 1s where 1 represents a marble
            platform and 0 represents a lava pool.

    Returns:
        A tuple of (move_count, path) where path uses 1-based
        positions. If no solution exists, returns (None, [1]).
    """
    n: int = len(dungeon)
    goal: int = n - 1  # 0-based index of the last platform

    # Edge case: dungeon has only one platform (already at the end)
    if goal == 0:
        return (0, [1])

    # BFS setup: queue stores (current_index, path_so_far)
    queue: deque[Tuple[int, List[int]]] = deque([(0, [0])])
    visited: Set[int] = {0}

    while queue:
        position, path = queue.popleft()

        for distance in MOVE_DISTANCES:
            next_pos: int = position + distance

            # Landing on or jumping beyond the last platform counts as escape
            if next_pos >= goal:
                final_path: List[int] = path + [max(next_pos, goal)]
                return (len(path), [p + 1 for p in final_path])

            # Only step on marble platforms we haven't visited yet
            if (next_pos < n
                    and dungeon[next_pos] == 1
                    and next_pos not in visited):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

    # No path reaches the end
    return (None, [1])


def format_result(dungeon: List[int]) -> str:
    """Format the solution for a given dungeon as a readable string.

    Args:
        dungeon: List of 0s and 1s representing the dungeon layout.

    Returns:
        A human-readable string describing the move count and path.
    """
    moves, path = solve_dungeon(dungeon)
    if moves is None:
        return f"Dungeon: {dungeon}\n  Solution: No solution, Path: {path}"
    return f"Dungeon: {dungeon}\n  Solution: {moves} moves, Path: {path}"


if __name__ == "__main__":
    test_cases: List[List[int]] = [
        [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1],
        [1, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
        [1, 1, 1, 0, 1, 0, 1],
    ]

    for dungeon in test_cases:
        print(format_result(dungeon))
