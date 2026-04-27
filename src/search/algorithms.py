from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

from src.maze.grid import Cell, Maze


@dataclass
class SearchResult:
    path: List[Cell]
    explored_count: int
    explored_nodes: Set[Cell]
    explored_order: List[Cell]
    path_cost: float
    elapsed_ms: float


def _reconstruct_path(parent: Dict[Cell, Optional[Cell]], goal: Cell) -> List[Cell]:
    path: List[Cell] = []
    node: Optional[Cell] = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def _empty_result(elapsed_ms: float, explored_nodes: Set[Cell]) -> SearchResult:
    return SearchResult(
        path=[],
        explored_count=len(explored_nodes),
        explored_nodes=set(explored_nodes),
        explored_order=[],
        path_cost=float("inf"),
        elapsed_ms=elapsed_ms,
    )


def bfs(maze: Maze, start: Cell, goal: Cell) -> SearchResult:
    t0 = time.perf_counter()
    queue = deque([start])
    visited = {start}
    explored_nodes: Set[Cell] = set()
    explored_order: List[Cell] = []
    parent: Dict[Cell, Optional[Cell]] = {start: None}

    while queue:
        node = queue.popleft()
        explored_nodes.add(node)
        explored_order.append(node)

        if node == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            path = _reconstruct_path(parent, goal)
            return SearchResult(
                path=path,
                explored_count=len(explored_nodes),
                explored_nodes=explored_nodes,
                explored_order=explored_order,
                path_cost=float(len(path) - 1),
                elapsed_ms=elapsed_ms,
            )

        for neighbor in maze.passable_neighbors(node):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            parent[neighbor] = node
            queue.append(neighbor)

    return _empty_result((time.perf_counter() - t0) * 1000, explored_nodes)


def dfs(maze: Maze, start: Cell, goal: Cell) -> SearchResult:
    t0 = time.perf_counter()
    stack = [start]
    visited: Set[Cell] = set()
    explored_nodes: Set[Cell] = set()
    explored_order: List[Cell] = []
    parent: Dict[Cell, Optional[Cell]] = {start: None}

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        explored_nodes.add(node)
        explored_order.append(node)

        if node == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            path = _reconstruct_path(parent, goal)
            return SearchResult(
                path=path,
                explored_count=len(explored_nodes),
                explored_nodes=explored_nodes,
                explored_order=explored_order,
                path_cost=float(len(path) - 1),
                elapsed_ms=elapsed_ms,
            )

        for neighbor in maze.passable_neighbors(node):
            if neighbor in visited:
                continue
            if neighbor not in parent:
                parent[neighbor] = node
            stack.append(neighbor)

    return _empty_result((time.perf_counter() - t0) * 1000, explored_nodes)


def ucs(maze: Maze, start: Cell, goal: Cell) -> SearchResult:
    t0 = time.perf_counter()
    frontier: List[Tuple[float, Cell]] = [(0.0, start)]
    parent: Dict[Cell, Optional[Cell]] = {start: None}
    best_cost: Dict[Cell, float] = {start: 0.0}
    explored_nodes: Set[Cell] = set()
    explored_order: List[Cell] = []

    while frontier:
        current_cost, node = heapq.heappop(frontier)
        if current_cost > best_cost[node]:
            continue
        explored_nodes.add(node)
        explored_order.append(node)

        if node == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            path = _reconstruct_path(parent, goal)
            return SearchResult(
                path=path,
                explored_count=len(explored_nodes),
                explored_nodes=explored_nodes,
                explored_order=explored_order,
                path_cost=current_cost,
                elapsed_ms=elapsed_ms,
            )

        for neighbor in maze.passable_neighbors(node):
            new_cost = current_cost + 1.0
            if new_cost >= best_cost.get(neighbor, float("inf")):
                continue
            best_cost[neighbor] = new_cost
            parent[neighbor] = node
            heapq.heappush(frontier, (new_cost, neighbor))

    return _empty_result((time.perf_counter() - t0) * 1000, explored_nodes)


def _manhattan(a: Cell, b: Cell) -> float:
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def astar(maze: Maze, start: Cell, goal: Cell, heuristic: Callable[[Cell, Cell], float] = _manhattan) -> SearchResult:
    t0 = time.perf_counter()
    frontier: List[Tuple[float, float, Cell]] = [(heuristic(start, goal), 0.0, start)]
    parent: Dict[Cell, Optional[Cell]] = {start: None}
    g_cost: Dict[Cell, float] = {start: 0.0}
    explored_nodes: Set[Cell] = set()
    explored_order: List[Cell] = []

    while frontier:
        _, current_cost, node = heapq.heappop(frontier)
        if current_cost > g_cost[node]:
            continue
        explored_nodes.add(node)
        explored_order.append(node)

        if node == goal:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            path = _reconstruct_path(parent, goal)
            return SearchResult(
                path=path,
                explored_count=len(explored_nodes),
                explored_nodes=explored_nodes,
                explored_order=explored_order,
                path_cost=current_cost,
                elapsed_ms=elapsed_ms,
            )

        for neighbor in maze.passable_neighbors(node):
            tentative = current_cost + 1.0
            if tentative >= g_cost.get(neighbor, float("inf")):
                continue
            g_cost[neighbor] = tentative
            parent[neighbor] = node
            f_cost = tentative + heuristic(neighbor, goal)
            heapq.heappush(frontier, (f_cost, tentative, neighbor))

    return _empty_result((time.perf_counter() - t0) * 1000, explored_nodes)
