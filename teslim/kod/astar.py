"""A*: f = g + h; g = enerji (Wh), h = k * düz çizgi mesafesi.

k = min(energy_wh / distance_m) tüm kenarlar ve seçilen rüzgâr koşulu üzerinden.
Kabul edilebilir: her kenar için c(e) >= k*d(e) ve yol uzunluğu >= düz çizgi mesafesi.
Tutarlı: h(u) - h(v) = k(|u-g| - |v-g|) <= k*|u-v| <= k*d(u,v) <= c(u,v).
"""
from __future__ import annotations
import heapq
from itertools import count
from graph_utils import UAVGraph
from geo import sld
from load_data import energy_column

_K_CACHE: dict = {}


def compute_k(graph: UAVGraph, wind_condition: str) -> float:
    key = (id(graph), wind_condition)
    if key not in _K_CACHE:
        col = energy_column(wind_condition)
        _K_CACHE[key] = min(e[col] / e["distance_m"] for e in graph._edge.values())
    return _K_CACHE[key]


def heuristic(graph: UAVGraph, node: str, goal: str, wind_condition: str) -> float:
    return compute_k(graph, wind_condition) * sld(graph, node, goal)


def astar(graph: UAVGraph, start: str, goal: str, wind_condition: str) -> list[str] | None:
    tie = count()
    best_g = {start: 0.0}
    parent = {start: None}
    frontier = [(heuristic(graph, start, goal, wind_condition), next(tie), 0.0, start)]
    closed = set()
    while frontier:
        _, _, g, node = heapq.heappop(frontier)
        if node in closed:
            continue
        if node == goal:
            return _build_path(parent, node)
        closed.add(node)
        for nb, _edge in graph.neighbors(node):
            ng = g + graph.edge_cost(node, nb, wind_condition, "energy")
            if nb not in best_g or ng < best_g[nb]:
                best_g[nb] = ng
                parent[nb] = node
                f = ng + heuristic(graph, nb, goal, wind_condition)
                heapq.heappush(frontier, (f, next(tie), ng, nb))
    return None


def _build_path(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]
