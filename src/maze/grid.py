from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set, Tuple

Cell = Tuple[int, int]


@dataclass
class Maze:
    rows: int
    cols: int
    passages: Dict[Cell, Set[Cell]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("rows and cols must be positive")
        for row in range(self.rows):
            for col in range(self.cols):
                self.passages[(row, col)] = set()

    def all_cells(self) -> Iterable[Cell]:
        for row in range(self.rows):
            for col in range(self.cols):
                yield (row, col)

    def in_bounds(self, cell: Cell) -> bool:
        row, col = cell
        return 0 <= row < self.rows and 0 <= col < self.cols

    def grid_neighbors(self, cell: Cell) -> List[Cell]:
        row, col = cell
        candidates = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        return [neighbor for neighbor in candidates if self.in_bounds(neighbor)]

    def carve_passage(self, cell_a: Cell, cell_b: Cell) -> None:
        if not self.in_bounds(cell_a) or not self.in_bounds(cell_b):
            raise ValueError("Both cells must be inside the maze")
        self.passages[cell_a].add(cell_b)
        self.passages[cell_b].add(cell_a)

    def passable_neighbors(self, cell: Cell) -> List[Cell]:
        return list(self.passages[cell])

    def edge_count(self) -> int:
        return sum(len(neighbors) for neighbors in self.passages.values()) // 2

    def expected_tree_edges(self) -> int:
        return self.rows * self.cols - 1
