"""Greedy Best-First: f(n) = h(n) = hedefe düz çizgi mesafesi (m)."""
from __future__ import annotations
import heapq
from itertools import count
from graph_utils import UAVGraph
from geo import sld


def greedy_best_first(graph: UAVGraph, start: str, goal: str) -> list[str] | None:
    tie = count()
    frontier = [(sld(graph, start, goal), next(tie), start)]
    parent = {start: None}
    closed = set()
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in closed:
            continue
        if node == goal:
            return _build_path(parent, node)
        closed.add(node)
        for nb, _edge in graph.neighbors(node):
            if nb not in parent:  # döngü önleme: her düğüm bir kez eklenir
                parent[nb] = node
                heapq.heappush(frontier, (sld(graph, nb, goal), next(tie), nb))
    return None


def _build_path(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]
