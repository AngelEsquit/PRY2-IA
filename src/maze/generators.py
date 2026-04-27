from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.maze.grid import Cell, Maze

GenerationStep = Tuple[Cell, Cell]


def _generate_prim_maze(rows: int, cols: int, seed: int | None = None) -> tuple[Maze, List[GenerationStep]]:
    rng = random.Random(seed)
    maze = Maze(rows=rows, cols=cols)
    steps: List[GenerationStep] = []

    start = (0, 0)
    visited = {start}
    frontier: List[Tuple[Cell, Cell]] = []

    def add_frontier(cell: Cell) -> None:
        for neighbor in maze.grid_neighbors(cell):
            if neighbor not in visited:
                frontier.append((cell, neighbor))

    add_frontier(start)

    while frontier:
        wall_index = rng.randrange(len(frontier))
        source, target = frontier.pop(wall_index)

        if target in visited:
            continue

        maze.carve_passage(source, target)
        steps.append((source, target))
        visited.add(target)
        add_frontier(target)

    return maze, steps


def generate_prim_maze(rows: int, cols: int, seed: int | None = None) -> Maze:
    maze, _ = _generate_prim_maze(rows=rows, cols=cols, seed=seed)
    return maze


def generate_prim_maze_with_trace(rows: int, cols: int, seed: int | None = None) -> tuple[Maze, List[GenerationStep]]:
    return _generate_prim_maze(rows=rows, cols=cols, seed=seed)


@dataclass
class UnionFind:
    parent: Dict[Cell, Cell]
    rank: Dict[Cell, int]

    @classmethod
    def from_cells(cls, cells: List[Cell]) -> "UnionFind":
        return cls(parent={cell: cell for cell in cells}, rank={cell: 0 for cell in cells})

    def find(self, cell: Cell) -> Cell:
        if self.parent[cell] != cell:
            self.parent[cell] = self.find(self.parent[cell])
        return self.parent[cell]

    def union(self, cell_a: Cell, cell_b: Cell) -> bool:
        root_a = self.find(cell_a)
        root_b = self.find(cell_b)
        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b
        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a
        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1
        return True


def _generate_kruskal_maze(rows: int, cols: int, seed: int | None = None) -> tuple[Maze, List[GenerationStep]]:
    rng = random.Random(seed)
    maze = Maze(rows=rows, cols=cols)
    cells = list(maze.all_cells())
    dsu = UnionFind.from_cells(cells)
    steps: List[GenerationStep] = []

    walls: List[Tuple[Cell, Cell]] = []
    for cell in cells:
        row, col = cell
        if row + 1 < rows:
            walls.append((cell, (row + 1, col)))
        if col + 1 < cols:
            walls.append((cell, (row, col + 1)))

    rng.shuffle(walls)

    for cell_a, cell_b in walls:
        if dsu.union(cell_a, cell_b):
            maze.carve_passage(cell_a, cell_b)
            steps.append((cell_a, cell_b))

    return maze, steps


def generate_kruskal_maze(rows: int, cols: int, seed: int | None = None) -> Maze:
    maze, _ = _generate_kruskal_maze(rows=rows, cols=cols, seed=seed)
    return maze


def generate_kruskal_maze_with_trace(rows: int, cols: int, seed: int | None = None) -> tuple[Maze, List[GenerationStep]]:
    return _generate_kruskal_maze(rows=rows, cols=cols, seed=seed)
