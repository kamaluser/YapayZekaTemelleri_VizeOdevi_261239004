"""Düz çizgi mesafesi için hızlı (önbellekli) yardımcı; graph.straight_line_distance ile aynı sonucu verir."""
import math

_XY = {}


def sld(graph, a, b):
    xy = _XY.get(id(graph))
    if xy is None:
        xy = {n: (r["x_m"], r["y_m"]) for n, r in graph.nodes.iterrows()}
        _XY[id(graph)] = xy
    (x1, y1), (x2, y2) = xy[a], xy[b]
    return math.hypot(x2 - x1, y2 - y1)
