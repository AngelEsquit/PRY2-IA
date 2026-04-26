from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from src.maze.generators import generate_kruskal_maze, generate_prim_maze
from src.maze.grid import Cell, Maze
from src.search.algorithms import SearchResult, astar, bfs, dfs, ucs

Generator = Callable[[int, int, int | None], Maze]
Solver = Callable[[Maze, Cell, Cell], SearchResult]


@dataclass
class ScenarioResult:
    scenario_id: int
    generator: str
    start: Cell
    goal: Cell
    algorithm: str
    explored: int
    path_length: int
    time_ms: float
    rank: int


def _pick_start_goal(rows: int, cols: int, rng: random.Random, min_manhattan: int) -> Tuple[Cell, Cell]:
    while True:
        start = (rng.randrange(rows), rng.randrange(cols))
        goal = (rng.randrange(rows), rng.randrange(cols))
        if abs(start[0] - goal[0]) + abs(start[1] - goal[1]) >= min_manhattan:
            return start, goal


def _rank_algorithms(metrics: Dict[str, SearchResult]) -> Dict[str, int]:
    ordered = sorted(
        metrics.items(),
        key=lambda item: (
            len(item[1].path) if item[1].path else float("inf"),
            item[1].explored_count,
            item[1].elapsed_ms,
        ),
    )
    return {name: idx + 1 for idx, (name, _) in enumerate(ordered)}


def run_k_comparison(
    rows: int,
    cols: int,
    k: int,
    generator_name: str,
    seed: int,
    min_manhattan: int = 10,
    output_csv: str = "reports/comparison.csv",
) -> List[ScenarioResult]:
    generators: Dict[str, Generator] = {
        "prim": generate_prim_maze,
        "kruskal": generate_kruskal_maze,
    }
    solvers: Dict[str, Solver] = {
        "bfs": bfs,
        "dfs": dfs,
        "ucs": ucs,
        "astar": astar,
    }

    if generator_name not in generators:
        raise ValueError(f"Unsupported generator: {generator_name}")

    rng = random.Random(seed)
    generator = generators[generator_name]
    all_rows: List[ScenarioResult] = []

    for scenario_id in range(1, k + 1):
        maze_seed = rng.randrange(1_000_000_000)
        maze = generator(rows, cols, maze_seed)
        start, goal = _pick_start_goal(rows, cols, rng, min_manhattan)

        metrics = {name: solver(maze, start, goal) for name, solver in solvers.items()}
        ranks = _rank_algorithms(metrics)

        for name, result in metrics.items():
            all_rows.append(
                ScenarioResult(
                    scenario_id=scenario_id,
                    generator=generator_name,
                    start=start,
                    goal=goal,
                    algorithm=name,
                    explored=result.explored_count,
                    path_length=(len(result.path) - 1) if result.path else -1,
                    time_ms=result.elapsed_ms,
                    rank=ranks[name],
                )
            )

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario_id", "generator", "start", "goal", "algorithm", "explored", "path_length", "time_ms", "rank"])
        for row in all_rows:
            writer.writerow(
                [
                    row.scenario_id,
                    row.generator,
                    f"{row.start[0]},{row.start[1]}",
                    f"{row.goal[0]},{row.goal[1]}",
                    row.algorithm,
                    row.explored,
                    row.path_length,
                    f"{row.time_ms:.3f}",
                    row.rank,
                ]
            )

    return all_rows
