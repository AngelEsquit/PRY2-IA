from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean
from typing import Callable, Dict

from src.experiments.compare import run_k_comparison
from src.maze.generators import generate_kruskal_maze, generate_prim_maze
from src.maze.grid import Cell, Maze
from src.search.algorithms import SearchResult, astar, bfs, dfs, ucs
from src.visualization.plotting import save_maze_solution_plot

Generator = Callable[[int, int, int | None], Maze]
Solver = Callable[[Maze, Cell, Cell], SearchResult]


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


def _run_solve(args: argparse.Namespace) -> None:
    generator = _get_generator(args.generator)
    solver = _get_solver(args.search)

    maze = generator(args.rows, args.cols, args.seed)
    start = (0, 0)
    goal = (args.rows - 1, args.cols - 1)
    result = solver(maze, start, goal)

    save_path = save_maze_solution_plot(
        maze=maze,
        start=start,
        goal=goal,
        path=result.path,
        output_path=args.output,
    )

    print(
        f"search={args.search} path_length={len(result.path)-1} "
        f"explored={result.explored_count} time_ms={result.elapsed_ms:.3f}"
    )
    print(f"plot_saved={save_path}")


def _run_compare(args: argparse.Namespace) -> None:
    rows = run_k_comparison(
        rows=args.rows,
        cols=args.cols,
        k=args.k,
        generator_name=args.generator,
        seed=args.seed,
        min_manhattan=args.min_manhattan,
        output_csv=args.output_csv,
    )

    per_algo: Dict[str, list[int]] = {}
    for row in rows:
        per_algo.setdefault(row.algorithm, []).append(row.rank)

    summary_lines = ["Resumen de ranking promedio (menor es mejor):"]
    for algo, ranks in sorted(per_algo.items(), key=lambda item: mean(item[1])):
        summary_lines.append(f"{algo}: {mean(ranks):.3f}")

    summary_path = Path(args.summary_txt)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"comparison_csv={args.output_csv}")
    print(f"summary_txt={summary_path}")
    for line in summary_lines:
        print(line)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Proyecto 2 IA - Laberintos y busqueda")
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="Genera un laberinto y resuelve de (0,0) a (M-1,N-1)")
    solve_parser.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    solve_parser.add_argument("--search", choices=["bfs", "dfs", "ucs", "astar"], default="astar")
    solve_parser.add_argument("--rows", type=int, default=60)
    solve_parser.add_argument("--cols", type=int, default=80)
    solve_parser.add_argument("--seed", type=int, default=42)
    solve_parser.add_argument("--output", default="reports/solve.png")
    solve_parser.set_defaults(func=_run_solve)

    compare_parser = subparsers.add_parser("compare", help="Ejecuta K escenarios y compara BFS/DFS/UCS/A*")
    compare_parser.add_argument("--generator", choices=["prim", "kruskal"], default="prim")
    compare_parser.add_argument("--rows", type=int, default=45)
    compare_parser.add_argument("--cols", type=int, default=55)
    compare_parser.add_argument("--k", type=int, default=25)
    compare_parser.add_argument("--seed", type=int, default=42)
    compare_parser.add_argument("--min-manhattan", type=int, default=10)
    compare_parser.add_argument("--output-csv", default="reports/comparison.csv")
    compare_parser.add_argument("--summary-txt", default="reports/ranking_summary.txt")
    compare_parser.set_defaults(func=_run_compare)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
