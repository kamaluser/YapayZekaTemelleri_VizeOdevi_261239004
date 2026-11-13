"""BFS: en az kenarlı (hop) yol. Kenar maliyeti kullanılmaz."""
from __future__ import annotations
from collections import deque
from graph_utils import UAVGraph


def bfs(graph: UAVGraph, start: str, goal: str) -> list[str] | None:
    if start == goal:
        return [start]
    frontier = deque([start])
    parent = {start: None}  # aynı zamanda "reached" kümesi
    while frontier:
        node = frontier.popleft()
        for nb, _edge in graph.neighbors(node):
            if nb not in parent:
                parent[nb] = node
                if nb == goal:  # BFS'te hedef testi üretim anında optimaldir (maliyet = hop)
                    return _build_path(parent, nb)
                frontier.append(nb)
    return None


def _build_path(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]
