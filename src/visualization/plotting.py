from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

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


def _build_partial_maze(rows: int, cols: int, steps: List[Tuple[Cell, Cell]], step_count: int) -> Maze:
    maze = Maze(rows=rows, cols=cols)
    for cell_a, cell_b in steps[:step_count]:
        maze.carve_passage(cell_a, cell_b)
    return maze


def save_generation_comparison_animation(
    rows: int,
    cols: int,
    prim_steps: List[Tuple[Cell, Cell]],
    kruskal_steps: List[Tuple[Cell, Cell]],
    output_path: str = "reports/generation_compare.gif",
    max_frames: int = 120,
    fps: int = 12,
) -> str:
    total_steps = max(len(prim_steps), len(kruskal_steps))
    if total_steps == 0:
        raise ValueError("No hay pasos de generación para animar")

    frame_count = max(2, min(max_frames, total_steps + 1))
    sample_steps = [round(i * total_steps / (frame_count - 1)) for i in range(frame_count)]

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(0, cols)
        ax.set_ylim(rows, 0)
        ax.axis("off")

    def update(frame_idx: int):
        prim_count = min(sample_steps[frame_idx], len(prim_steps))
        kruskal_count = min(sample_steps[frame_idx], len(kruskal_steps))

        prim_maze = _build_partial_maze(rows, cols, prim_steps, prim_count)
        kruskal_maze = _build_partial_maze(rows, cols, kruskal_steps, kruskal_count)

        axes[0].clear()
        axes[1].clear()
        for ax in axes:
            ax.set_aspect("equal")
            ax.set_xlim(0, cols)
            ax.set_ylim(rows, 0)
            ax.axis("off")

        _draw_maze_walls(axes[0], prim_maze)
        _draw_maze_walls(axes[1], kruskal_maze)
        axes[0].set_title(f"Prim - paso {prim_count}/{len(prim_steps)}")
        axes[1].set_title(f"Kruskal - paso {kruskal_count}/{len(kruskal_steps)}")
        return axes

    animation = FuncAnimation(fig, update, frames=frame_count, interval=1000 / max(1, fps), blit=False)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out, writer=PillowWriter(fps=max(1, fps)))
    plt.close(fig)
    return str(out)


def save_maze_solution_animation(
    maze: Maze,
    start: Cell,
    goal: Cell,
    path: List[Cell],
    explored_order: List[Cell],
    output_path: str = "reports/solve_animation.gif",
    max_frames: int = 140,
    fps: int = 12,
) -> str:
    explored_total = len(explored_order)
    if explored_total == 0:
        raise ValueError("No hay nodos explorados para animar")

    frame_count = max(2, min(max_frames, explored_total + 2))
    sample_counts = [round(i * explored_total / (frame_count - 2)) for i in range(frame_count - 1)]

    fig, ax = plt.subplots(figsize=(9, 6))

    def update(frame_idx: int):
        ax.clear()
        ax.set_aspect("equal")
        ax.set_xlim(0, maze.cols)
        ax.set_ylim(maze.rows, 0)
        ax.axis("off")

        if frame_idx < frame_count - 1:
            explored_now = explored_order[: sample_counts[frame_idx]]
            _fill_cells(ax, explored_now, color="#c6dbef", alpha=0.65)
            _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
            _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
            _draw_maze_walls(ax, maze)
            ax.set_title(f"Exploracion: {len(explored_now)}/{explored_total}")
        else:
            _fill_cells(ax, explored_order, color="#c6dbef", alpha=0.65)
            _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
            _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
            _draw_path(ax, path)
            _draw_maze_walls(ax, maze)
            ax.set_title("Camino final encontrado")

        return [ax]

    animation = FuncAnimation(fig, update, frames=frame_count, interval=1000 / max(1, fps), blit=False)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out, writer=PillowWriter(fps=max(1, fps)))
    plt.close(fig)
    return str(out)
