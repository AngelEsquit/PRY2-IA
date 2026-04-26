from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Set

import matplotlib.pyplot as plt

from src.maze.grid import Cell, Maze


def _draw_maze_walls(ax, maze: Maze) -> None:
    ax.plot([0, maze.cols], [0, 0], color="black", linewidth=1.2)
    ax.plot([0, maze.cols], [maze.rows, maze.rows], color="black", linewidth=1.2)
    ax.plot([0, 0], [0, maze.rows], color="black", linewidth=1.2)
    ax.plot([maze.cols, maze.cols], [0, maze.rows], color="black", linewidth=1.2)

    for row in range(maze.rows):
        for col in range(maze.cols):
            cell = (row, col)
            if col + 1 < maze.cols and (row, col + 1) not in maze.passages[cell]:
                x = col + 1
                ax.plot([x, x], [row, row + 1], color="black", linewidth=0.8)
            if row + 1 < maze.rows and (row + 1, col) not in maze.passages[cell]:
                y = row + 1
                ax.plot([col, col + 1], [y, y], color="black", linewidth=0.8)


def _fill_cells(ax, cells: Iterable[Cell], color: str, alpha: float) -> None:
    for row, col in cells:
        ax.add_patch(plt.Rectangle((col, row), 1, 1, color=color, alpha=alpha))


def _draw_path(ax, path: List[Cell], color: str = "#d95f02") -> None:
    if not path:
        return
    xs = [cell[1] + 0.5 for cell in path]
    ys = [cell[0] + 0.5 for cell in path]
    ax.plot(xs, ys, color=color, linewidth=2.2)


def save_maze_solution_plot(
    maze: Maze,
    start: Cell,
    goal: Cell,
    path: List[Cell],
    explored: Optional[Set[Cell]] = None,
    output_path: str = "reports/solution.png",
) -> str:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_aspect("equal")
    ax.set_xlim(0, maze.cols)
    ax.set_ylim(maze.rows, 0)
    ax.axis("off")

    if explored:
        _fill_cells(ax, explored, color="#c6dbef", alpha=0.65)

    _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
    _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)

    _draw_path(ax, path)
    _draw_maze_walls(ax, maze)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(out)
