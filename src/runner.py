"""
src/runner.py
Core execution functions shared by the CLI (main.py) and the interactive menu (menu.py).
"""
from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Optional

from src.experiments.compare import run_k_comparison
from src.maze.generators import (
    generate_kruskal_maze,
    generate_kruskal_maze_with_trace,
    generate_prim_maze,
    generate_prim_maze_with_trace,
)
from src.maze.grid import Cell
from src.search.algorithms import astar, bfs, dfs, ucs
from src.visualization.plotting import (
    save_generation_comparison_animation,
    save_maze_only_plot,
    save_maze_solution_animation,
    save_maze_solution_plot,
)

_DIV = "=" * 56
_GENERATORS = {"prim": generate_prim_maze, "kruskal": generate_kruskal_maze}
_SOLVERS = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "astar": astar}


def run_solve(
    generator: str = "prim",
    search: str = "astar",
    rows: int = 60,
    cols: int = 80,
    seed: int = 42,
    animate_frames: int = 140,
    animate_fps: int = 12,
    no_gif: bool = False,
    out_dir: Optional[str] = None,
) -> None:
    gen_fn = _GENERATORS[generator]
    solver_fn = _SOLVERS[search]

    maze = gen_fn(rows, cols, seed)
    start: Cell = (0, 0)
    goal: Cell = (rows - 1, cols - 1)
    result = solver_fn(maze, start, goal)

    _out = Path(out_dir) if out_dir else Path(
        f"reports/solve_{generator}_{search}_{rows}x{cols}_seed{seed}"
    )
    _out.mkdir(parents=True, exist_ok=True)

    path_len = len(result.path) - 1 if result.path else 0

    maze_path = save_maze_only_plot(
        maze=maze,
        start=start,
        goal=goal,
        output_path=str(_out / "01_maze.png"),
        title=f"Laberinto - {generator.capitalize()} {rows}x{cols}  (seed={seed})",
    )

    gif_path: Optional[str] = None
    if not no_gif:
        gif_path = save_maze_solution_animation(
            maze=maze,
            start=start,
            goal=goal,
            path=result.path,
            explored_order=result.explored_order,
            output_path=str(_out / "02_solve.gif"),
            max_frames=animate_frames,
            fps=animate_fps,
            algo_label=search.upper(),
        )

    solved_path = save_maze_solution_plot(
        maze=maze,
        start=start,
        goal=goal,
        path=result.path,
        explored=result.explored_nodes,
        output_path=str(_out / "03_solved.png"),
        title=(
            f"{search.upper()}  |  Camino: {path_len} pasos  |  "
            f"Explorados: {result.explored_count}  |  {result.elapsed_ms:.1f} ms"
        ),
    )

    print(f"\n{_DIV}")
    print(f"  SOLVE - {search.upper()} sobre {generator.capitalize()} {rows}x{cols}")
    print(_DIV)
    print(f"  Camino     : {path_len} pasos")
    print(f"  Explorados : {result.explored_count} nodos")
    print(f"  Tiempo     : {result.elapsed_ms:.3f} ms")
    print(f"\n  Outputs -> {_out}")
    print(f"    [01] {Path(maze_path).name}")
    if gif_path:
        print(f"    [02] {Path(gif_path).name}")
    print(f"    [03] {Path(solved_path).name}")
    print(f"{_DIV}\n")


def run_compare(
    generator: str = "prim",
    rows: int = 45,
    cols: int = 55,
    k: int = 25,
    seed: int = 42,
    min_manhattan: int = 10,
    out_dir: Optional[str] = None,
) -> None:
    _out = Path(out_dir) if out_dir else Path(
        f"reports/compare_{generator}_{rows}x{cols}_k{k}_seed{seed}"
    )
    _out.mkdir(parents=True, exist_ok=True)

    rows_data = run_k_comparison(
        rows=rows,
        cols=cols,
        k=k,
        generator_name=generator,
        seed=seed,
        min_manhattan=min_manhattan,
        output_csv=str(_out / "comparison.csv"),
        viz_dir=str(_out / "scenarios"),
    )

    per_algo: dict[str, list[int]] = {}
    for row in rows_data:
        per_algo.setdefault(row.algorithm, []).append(row.rank)

    summary_lines = ["Ranking promedio (menor = mejor):"]
    for algo, ranks in sorted(per_algo.items(), key=lambda x: mean(x[1])):
        summary_lines.append(f"  {algo.upper():<10} {mean(ranks):.3f}")

    (_out / "ranking_summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"\n{_DIV}")
    print(f"  COMPARE - {k} escenarios  {generator.capitalize()} {rows}x{cols}")
    print(_DIV)
    for line in summary_lines:
        print(f"  {line}")
    print(f"\n  Outputs -> {_out}")
    print(f"    comparison.csv, ranking_summary.txt")
    print(f"    scenarios/ - {k} x 2 imagenes por escenario")
    print(f"    scenarios/ranking_summary.png")
    print(f"{_DIV}\n")


def run_buildviz(
    rows: int = 30,
    cols: int = 40,
    seed: int = 42,
    max_frames: int = 120,
    fps: int = 12,
    out_dir: Optional[str] = None,
) -> None:
    prim_maze, prim_steps = generate_prim_maze_with_trace(rows, cols, seed)
    kruskal_maze, kruskal_steps = generate_kruskal_maze_with_trace(rows, cols, seed)

    _out = Path(out_dir) if out_dir else Path(f"reports/buildviz_{rows}x{cols}_seed{seed}")
    _out.mkdir(parents=True, exist_ok=True)

    start: Cell = (0, 0)
    goal: Cell = (rows - 1, cols - 1)

    prim_path = save_maze_only_plot(
        maze=prim_maze,
        start=start,
        goal=goal,
        output_path=str(_out / "01_prim_maze.png"),
        title=f"Laberinto Prim - {rows}x{cols}  (seed={seed})",
    )
    kruskal_path = save_maze_only_plot(
        maze=kruskal_maze,
        start=start,
        goal=goal,
        output_path=str(_out / "02_kruskal_maze.png"),
        title=f"Laberinto Kruskal - {rows}x{cols}  (seed={seed})",
    )
    gif_path = save_generation_comparison_animation(
        rows=rows,
        cols=cols,
        prim_steps=prim_steps,
        kruskal_steps=kruskal_steps,
        output_path=str(_out / "03_generation_compare.gif"),
        max_frames=max_frames,
        fps=fps,
    )

    print(f"\n{_DIV}")
    print(f"  BUILDVIZ - Prim vs Kruskal {rows}x{cols}")
    print(_DIV)
    print(f"  Pasos Prim    : {len(prim_steps)}")
    print(f"  Pasos Kruskal : {len(kruskal_steps)}")
    print(f"\n  Outputs -> {_out}")
    print(f"    [01] {Path(prim_path).name}")
    print(f"    [02] {Path(kruskal_path).name}")
    print(f"    [03] {Path(gif_path).name}")
    print(f"{_DIV}\n")
