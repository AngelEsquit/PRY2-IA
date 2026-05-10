from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, PillowWriter

from src.maze.grid import Cell, Maze

# (algo_key, display_label, explored_nodes, path, explored_count, elapsed_ms, rank)
AlgoPlotEntry = Tuple[str, str, Set[Cell], List[Cell], int, float, int]

_ALGO_LABELS: Dict[str, str] = {
    "bfs": "BFS",
    "dfs": "DFS",
    "ucs": "Dijkstra",
    "astar": "A*",
}


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


def _setup_maze_ax(ax, maze: Maze) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(0, maze.cols)
    ax.set_ylim(maze.rows, 0)
    ax.axis("off")


# ---------------------------------------------------------------------------
# Public plot functions
# ---------------------------------------------------------------------------

def save_maze_only_plot(
    maze: Maze,
    start: Cell,
    goal: Cell,
    output_path: str = "reports/maze.png",
    title: str = "",
) -> str:
    """Saves the maze without any solution overlay — just walls and start/goal."""
    fig, ax = plt.subplots(figsize=(9, 6))
    _setup_maze_ax(ax, maze)

    _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
    _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
    _draw_maze_walls(ax, maze)

    if title:
        ax.set_title(title, fontsize=11, pad=8)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(out)


def save_maze_solution_plot(
    maze: Maze,
    start: Cell,
    goal: Cell,
    path: List[Cell],
    explored: Optional[Set[Cell]] = None,
    output_path: str = "reports/solution.png",
    title: str = "",
) -> str:
    """Saves the solved maze: explored region (blue), path (orange), start (green), goal (red)."""
    fig, ax = plt.subplots(figsize=(9, 6))
    _setup_maze_ax(ax, maze)

    if explored:
        _fill_cells(ax, explored, color="#c6dbef", alpha=0.65)

    _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
    _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)

    _draw_path(ax, path)
    _draw_maze_walls(ax, maze)

    if title:
        ax.set_title(title, fontsize=10, pad=8)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(out)


def save_scenario_comparison_plot(
    maze: Maze,
    start: Cell,
    goal: Cell,
    algo_data: List[AlgoPlotEntry],
    scenario_id: int,
    generator: str,
    output_path: str,
) -> str:
    """
    2×2 maze grid (one per algorithm) + stats table panel.
    algo_data entries: (algo_key, display_label, explored_nodes, path, explored_count, elapsed_ms, rank)
    """
    fig = plt.figure(figsize=(18, 10))
    gs = gridspec.GridSpec(2, 3, figure=fig, width_ratios=[5, 5, 3], hspace=0.35, wspace=0.12)

    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    algo_data_display = sorted(algo_data, key=lambda e: e[6])  # sort by rank for table

    for idx, (algo_key, label, explored_nodes, path, explored_count, elapsed_ms, rank) in enumerate(algo_data[:4]):
        r, c = positions[idx]
        ax = fig.add_subplot(gs[r, c])
        _setup_maze_ax(ax, maze)

        if explored_nodes:
            _fill_cells(ax, explored_nodes, color="#c6dbef", alpha=0.65)
        _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
        _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
        _draw_path(ax, path)
        _draw_maze_walls(ax, maze)
        ax.set_title(f"{label} — {maze.cols}×{maze.rows}", fontsize=10)

    # Stats table (right column, spans both rows)
    ax_table = fig.add_subplot(gs[:, 2])
    ax_table.axis("off")

    table_rows = []
    for _, label, _, path, explored_count, elapsed_ms, rank in algo_data_display:
        dist = str(len(path) - 1) if path else "∞"
        table_rows.append([label, dist, str(explored_count), f"{elapsed_ms:.1f}", str(rank)])

    col_labels = ["Algoritmo", "Distancia", "Nodos", "ms", "Lugar"]
    tbl = ax_table.table(
        cellText=table_rows,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.05, 2.2)

    # Highlight header and best-rank row
    for j in range(len(col_labels)):
        tbl[(0, j)].set_facecolor("#2c7bb6")
        tbl[(0, j)].get_text().set_color("white")
        tbl[(0, j)].get_text().set_fontweight("bold")
    for i, row in enumerate(table_rows):
        if row[4] == "1":
            for j in range(len(col_labels)):
                tbl[(i + 1, j)].set_facecolor("#c7e9c0")

    ax_table.set_title("Comparación de algoritmos", fontsize=11, pad=12)

    fig.suptitle(
        f"Escenario {scenario_id}  —  Generador: {generator.capitalize()}  —  {maze.rows}×{maze.cols}",
        fontsize=13,
        y=1.01,
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(out)


def save_ranking_bar_chart(
    avg_ranks: Dict[str, float],
    output_path: str,
    title: str = "Ranking promedio por algoritmo",
    k: int = 0,
) -> str:
    """Bar chart showing average rank (1 = best) per algorithm across K scenarios."""
    sorted_items = sorted(avg_ranks.items(), key=lambda x: x[1])
    algos = [a for a, _ in sorted_items]
    values = [v for _, v in sorted_items]
    labels = [_ALGO_LABELS.get(a, a.upper()) for a in algos]

    palette = ["#1a9641", "#a6d96a", "#fdae61", "#d7191c"]
    colors = palette[: len(algos)]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.8, zorder=3)
    ax.set_ylim(0, 4.6)
    ax.set_ylabel("Ranking promedio (1 = mejor)", fontsize=11)
    ax.set_xlabel("Algoritmo", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    full_title = f"{title}\n(K = {k} escenarios)" if k else title
    ax.set_title(full_title, fontsize=12)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.06,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.axhline(y=2.5, color="gray", linestyle="--", alpha=0.4)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ---------------------------------------------------------------------------
# Animation functions
# ---------------------------------------------------------------------------

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
        axes[0].set_title(f"Prim — paso {prim_count}/{len(prim_steps)}", fontsize=10)
        axes[1].set_title(f"Kruskal — paso {kruskal_count}/{len(kruskal_steps)}", fontsize=10)
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
    algo_label: str = "",
) -> str:
    explored_total = len(explored_order)
    if explored_total == 0:
        raise ValueError("No hay nodos explorados para animar")

    frame_count = max(2, min(max_frames, explored_total + 2))
    sample_counts = [round(i * explored_total / (frame_count - 2)) for i in range(frame_count - 1)]

    fig, ax = plt.subplots(figsize=(9, 6))

    def update(frame_idx: int):
        ax.clear()
        _setup_maze_ax(ax, maze)

        if frame_idx < frame_count - 1:
            explored_now = explored_order[: sample_counts[frame_idx]]
            _fill_cells(ax, explored_now, color="#c6dbef", alpha=0.65)
            _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
            _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
            _draw_maze_walls(ax, maze)
            subtitle = f"Explorando: {len(explored_now)}/{explored_total} nodos"
            ax.set_title(f"{algo_label}  {subtitle}" if algo_label else subtitle, fontsize=10)
        else:
            _fill_cells(ax, explored_order, color="#c6dbef", alpha=0.65)
            _fill_cells(ax, [start], color="#2ca25f", alpha=0.95)
            _fill_cells(ax, [goal], color="#de2d26", alpha=0.95)
            _draw_path(ax, path)
            _draw_maze_walls(ax, maze)
            path_len = len(path) - 1 if path else 0
            subtitle = f"Camino encontrado: {path_len} pasos"
            ax.set_title(f"{algo_label}  {subtitle}" if algo_label else subtitle, fontsize=10)

        return [ax]

    animation = FuncAnimation(fig, update, frames=frame_count, interval=1000 / max(1, fps), blit=False)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    animation.save(out, writer=PillowWriter(fps=max(1, fps)))
    plt.close(fig)
    return str(out)
