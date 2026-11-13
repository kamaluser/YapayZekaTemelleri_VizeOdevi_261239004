"""UCS: g(n) = seçilen rüzgâr koşulundaki toplam enerji (Wh)."""
from __future__ import annotations
import heapq
from itertools import count
from graph_utils import UAVGraph


def ucs(graph: UAVGraph, start: str, goal: str, wind_condition: str) -> list[str] | None:
    tie = count()
    frontier = [(0.0, next(tie), start)]
    best_g = {start: 0.0}
    parent = {start: None}
    closed = set()
    while frontier:
        g, _, node = heapq.heappop(frontier)
        if node in closed:  # eski (daha kötü) kayıt
            continue
        if node == goal:  # hedef testi frontier'dan çıkarken
            return _build_path(parent, node)
        closed.add(node)
        for nb, _edge in graph.neighbors(node):
            ng = g + graph.edge_cost(node, nb, wind_condition, "energy")
            if nb not in best_g or ng < best_g[nb]:
                best_g[nb] = ng
                parent[nb] = node
                heapq.heappush(frontier, (ng, next(tie), nb))
    return None


def _build_path(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]
