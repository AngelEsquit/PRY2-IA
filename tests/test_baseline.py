from src.maze.generators import (
    generate_kruskal_maze,
    generate_kruskal_maze_with_trace,
    generate_prim_maze,
    generate_prim_maze_with_trace,
)
from src.search.algorithms import astar, bfs, dfs, ucs


def _is_fully_connected(maze) -> bool:
    start = (0, 0)
    visited = {start}
    stack = [start]

    while stack:
        node = stack.pop()
        for neighbor in maze.passable_neighbors(node):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            stack.append(neighbor)

    return len(visited) == maze.rows * maze.cols


def test_prim_and_kruskal_generate_connected_mazes():
    prim_maze = generate_prim_maze(12, 12, seed=123)
    kruskal_maze = generate_kruskal_maze(12, 12, seed=123)

    assert _is_fully_connected(prim_maze)
    assert _is_fully_connected(kruskal_maze)
    assert prim_maze.edge_count() == prim_maze.expected_tree_edges()
    assert kruskal_maze.edge_count() == kruskal_maze.expected_tree_edges()


def test_generation_trace_has_tree_edge_count():
    prim_maze, prim_steps = generate_prim_maze_with_trace(10, 11, seed=5)
    kruskal_maze, kruskal_steps = generate_kruskal_maze_with_trace(10, 11, seed=5)

    assert len(prim_steps) == prim_maze.expected_tree_edges()
    assert len(kruskal_steps) == kruskal_maze.expected_tree_edges()


def test_search_algorithms_find_a_valid_path():
    maze = generate_prim_maze(20, 20, seed=7)
    start = (0, 0)
    goal = (19, 19)

    results = [
        bfs(maze, start, goal),
        dfs(maze, start, goal),
        ucs(maze, start, goal),
        astar(maze, start, goal),
    ]

    for result in results:
        assert result.path
        assert result.path[0] == start
        assert result.path[-1] == goal
        assert result.explored_count > 0
        assert result.explored_nodes
        assert result.explored_order
        assert result.path[-1] in result.explored_nodes
