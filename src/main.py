from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean
from typing import Callable, Dict, Optional

from src.experiments.compare import run_k_comparison
from src.maze.generators import (
    generate_kruskal_maze,
    generate_kruskal_maze_with_trace,
    generate_prim_maze,
    generate_prim_maze_with_trace,
)
from src.maze.grid import Cell, Maze
from src.search.algorithms import SearchResult, astar, bfs, dfs, ucs
from src.visualization.plotting import (
    save_generation_comparison_animation,
    save_maze_only_plot,
    save_maze_solution_animation,
    save_maze_solution_plot,
)

Generator = Callable[[int, int, int | None], Maze]
Solver = Callable[[Maze, Cell, Cell], SearchResult]

_DIVIDER = "=" * 56


def _get_generator(name: str) -> Generator:
    generators: Dict[str, Generator] = {
        "prim": generate_prim_maze,
        "kruskal": generate_kruskal_maze,
    }
    return generators[name]


def _get_solver(name: str) -> Solver:
    solvers: Dict[str, Solver] = {
        "bfs": bfs,
        "dfs": dfs,
        "ucs": ucs,
        "astar": astar,
    }
    return solvers[name]


# ---------------------------------------------------------------------------
# solve
# ---------------------------------------------------------------------------

def _run_solve(args: argparse.Namespace) -> None:
    generator = _get_generator(args.generator)
    solver = _get_solver(args.search)

    maze = generator(args.rows, args.cols, args.seed)
    start: Cell = (0, 0)
    goal: Cell = (args.rows - 1, args.cols - 1)
    result = solver(maze, start, goal)

    out_dir = Path(args.out_dir) if args.out_dir else Path(
        f"reports/solve_{args.generator}_{args.search}_{args.rows}x{args.cols}_seed{args.seed}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    path_len = len(result.path) - 1 if result.path else 0
    algo_label = f"{args.search.upper()} | {args.generator.capitalize()} {args.rows}×{args.cols}"

    # Output 01: maze only (no solution)
    maze_path = save_maze_only_plot(
        maze=maze,
        start=start,
        goal=goal,
        output_path=str(out_dir / "01_maze.png"),
        title=f"Laberinto — {args.generator.capitalize()} {args.rows}×{args.cols}  (seed={args.seed})",
    )

    # Output 02: animated GIF of the solving process
    gif_path: Optional[str] = None
    if not args.no_gif:
        gif_path = save_maze_solution_animation(
            maze=maze,
            start=start,
            goal=goal,
            path=result.path,
            explored_order=result.explored_order,
            output_path=str(out_dir / "02_solve.gif"),
            max_frames=args.animate_frames,
            fps=args.animate_fps,
            algo_label=args.search.upper(),
        )

    # Output 03: solved maze (static image)
    solved_path = save_maze_solution_plot(
        maze=maze,
        start=start,
        goal=goal,
        path=result.path,
        explored=result.explored_nodes,
        output_path=str(out_dir / "03_solved.png"),
        title=f"{args.search.upper()}  |  Camino: {path_len} pasos  |  Explorados: {result.explored_count}  |  {result.elapsed_ms:.1f} ms",
    )

    print(f"\n{_DIVIDER}")
    print(f"  SOLVE - {args.search.upper()} sobre {args.generator.capitalize()} {args.rows}x{args.cols}")
    print(_DIVIDER)
    print(f"  Camino     : {path_len} pasos")
    print(f"  Explorados : {result.explored_count} nodos")
    print(f"  Tiempo     : {result.elapsed_ms:.3f} ms")
    print(f"\n  Outputs -> {out_dir}")
    print(f"    [01] {Path(maze_path).name}   (laberinto)")
    if gif_path:
        print(f"    [02] {Path(gif_path).name}    (animacion)")
    print(f"    [03] {Path(solved_path).name}  (resuelto)")
    print(f"{_DIVIDER}\n")


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def _run_compare(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir) if args.out_dir else Path(
        f"reports/compare_{args.generator}_{args.rows}x{args.cols}_k{args.k}_seed{args.seed}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = str(out_dir / "comparison.csv")
    viz_subdir = str(out_dir / "scenarios")

    rows = run_k_comparison(
        rows=args.rows,
        cols=args.cols,
        k=args.k,
        generator_name=args.generator,
        seed=args.seed,
        min_manhattan=args.min_manhattan,
        output_csv=csv_path,
        viz_dir=viz_subdir,
    )

    per_algo: Dict[str, list[int]] = {}
    for row in rows:
        per_algo.setdefault(row.algorithm, []).append(row.rank)

    summary_lines = ["Ranking promedio (menor = mejor):"]
    for algo, ranks in sorted(per_algo.items(), key=lambda item: mean(item[1])):
        summary_lines.append(f"  {algo.upper():<10} {mean(ranks):.3f}")

    summary_path = out_dir / "ranking_summary.txt"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"\n{_DIVIDER}")
    print(f"  COMPARE - {args.k} escenarios  {args.generator.capitalize()} {args.rows}x{args.cols}")
    print(_DIVIDER)
    for line in summary_lines:
        print(f"  {line}")
    print(f"\n  Outputs -> {out_dir}")
    print(f"    comparison.csv       - metricas por escenario")
    print(f"    ranking_summary.txt  - ranking promedio texto")
    print(f"    scenarios/           - {args.k} x 2 imagenes por escenario")
    print(f"    scenarios/ranking_summary.png - grafico de ranking")
    print(f"{_DIVIDER}\n")


# ---------------------------------------------------------------------------
# buildviz
# ---------------------------------------------------------------------------

def _run_generation_compare(args: argparse.Namespace) -> None:
    prim_maze, prim_steps = generate_prim_maze_with_trace(args.rows, args.cols, args.seed)
    kruskal_maze, kruskal_steps = generate_kruskal_maze_with_trace(args.rows, args.cols, args.seed)

    out_dir = Path(args.out_dir) if args.out_dir else Path(
        f"reports/buildviz_{args.rows}x{args.cols}_seed{args.seed}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    start: Cell = (0, 0)
    goal: Cell = (args.rows - 1, args.cols - 1)

    # Output 01: Prim maze (final state, static)
    prim_path = save_maze_only_plot(
        maze=prim_maze,
        start=start,
        goal=goal,
        output_path=str(out_dir / "01_prim_maze.png"),
        title=f"Laberinto Prim — {args.rows}×{args.cols}  (seed={args.seed})",
    )

    # Output 02: Kruskal maze (final state, static)
    kruskal_path = save_maze_only_plot(
        maze=kruskal_maze,
        start=start,
        goal=goal,
        output_path=str(out_dir / "02_kruskal_maze.png"),
        title=f"Laberinto Kruskal — {args.rows}×{args.cols}  (seed={args.seed})",
    )

    # Output 03: side-by-side generation animation GIF
    gif_path = save_generation_comparison_animation(
        rows=args.rows,
        cols=args.cols,
        prim_steps=prim_steps,
        kruskal_steps=kruskal_steps,
        output_path=str(out_dir / "03_generation_compare.gif"),
        max_frames=args.max_frames,
        fps=args.fps,
    )

    print(f"\n{_DIVIDER}")
    print(f"  BUILDVIZ - Prim vs Kruskal {args.rows}x{args.cols}")
    print(_DIVIDER)
    print(f"  Pasos Prim    : {len(prim_steps)}")
    print(f"  Pasos Kruskal : {len(kruskal_steps)}")
    print(f"\n  Outputs -> {out_dir}")
    print(f"    [01] {Path(prim_path).name}    (Prim final)")
    print(f"    [02] {Path(kruskal_path).name} (Kruskal final)")
    print(f"    [03] {Path(gif_path).name}")
    print(f"{_DIVIDER}\n")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Proyecto 2 IA — Laberintos y búsqueda",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- solve ---
    solve_p = subparsers.add_parser(
        "solve",
        help="Genera un laberinto, lo resuelve y guarda 3 outputs (maze / gif / solved).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    solve_p.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    solve_p.add_argument("--search", choices=["bfs", "dfs", "ucs", "astar"], default="astar")
    solve_p.add_argument("--rows", type=int, default=60)
    solve_p.add_argument("--cols", type=int, default=80)
    solve_p.add_argument("--seed", type=int, default=42)
    solve_p.add_argument(
        "--out-dir",
        default=None,
        help="Directorio de salida (auto-generado si se omite).",
    )
    solve_p.add_argument("--animate-frames", type=int, default=140)
    solve_p.add_argument("--animate-fps", type=int, default=12)
    solve_p.add_argument(
        "--no-gif",
        action="store_true",
        default=False,
        help="Omite la generación del GIF animado.",
    )
    solve_p.set_defaults(func=_run_solve)

    # --- compare ---
    cmp_p = subparsers.add_parser(
        "compare",
        help="Ejecuta K escenarios y compara BFS/DFS/UCS/A*.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cmp_p.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    cmp_p.add_argument("--rows", type=int, default=45)
    cmp_p.add_argument("--cols", type=int, default=55)
    cmp_p.add_argument("--k", type=int, default=25)
    cmp_p.add_argument("--seed", type=int, default=42)
    cmp_p.add_argument("--min-manhattan", type=int, default=10)
    cmp_p.add_argument(
        "--out-dir",
        default=None,
        help="Directorio raíz de salida (auto-generado si se omite).",
    )
    cmp_p.set_defaults(func=_run_compare)

    # --- buildviz ---
    bviz_p = subparsers.add_parser(
        "buildviz",
        help="Genera 3 outputs: Prim final / Kruskal final / GIF de construcción.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    bviz_p.add_argument("--rows", type=int, default=30)
    bviz_p.add_argument("--cols", type=int, default=40)
    bviz_p.add_argument("--seed", type=int, default=42)
    bviz_p.add_argument("--max-frames", type=int, default=120)
    bviz_p.add_argument("--fps", type=int, default=12)
    bviz_p.add_argument(
        "--out-dir",
        default=None,
        help="Directorio de salida (auto-generado si se omite).",
    )
    bviz_p.set_defaults(func=_run_generation_compare)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
