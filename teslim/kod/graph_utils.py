"""YZM537 Vize Projesi - graf yardımcıları.

Bu dosyada HAZIR arama algoritması YOKTUR. BFS, UCS, Greedy ve A* kodlarını siz yazacaksınız.

Önemli kural: bir düğümü GENİŞLETTİĞİNİZDE (expand) komşularını yalnızca
``graph.neighbors(node)`` ile alın. Böylece ``graph.expansions`` sayacı genişletilen düğüm
sayısını tutarlı biçimde sayar (değerlendirmenin isteğe bağlı kod modunda bu sayaç kullanılır).
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd

from load_data import WIND_SUFFIX


class UAVGraph:
    """Yönlü, ağırlıklı UAV rota grafı."""

    def __init__(self, nodes: pd.DataFrame, edges: pd.DataFrame):
        self.nodes = nodes.set_index("node_id")
        self._adj: dict[str, list[tuple[str, dict]]] = {n: [] for n in self.nodes.index}
        self._edge: dict[tuple[str, str], dict] = {}
        for row in edges.to_dict("records"):
            self._adj[row["u"]].append((row["v"], row))
            self._edge[(row["u"], row["v"])] = row
        self.expansions = 0

    # -- arama sırasında kullanılacak tek genişletme fonksiyonu
    def neighbors(self, node: str) -> list[tuple[str, dict]]:
        """``node`` düğümünden çıkan kenarlar: [(komşu_id, kenar_satırı_dict), ...].

        Her çağrı bir düğüm genişletmesi olarak sayılır.
        """
        self.expansions += 1
        return self._adj[node]

    def reset_counter(self) -> None:
        self.expansions = 0

    # -- yardımcılar
    def edge(self, u: str, v: str) -> dict | None:
        return self._edge.get((u, v))

    def edge_cost(self, u: str, v: str, wind_condition: str, objective: str = "energy") -> float:
        """Kenar maliyeti. objective: 'energy' (Wh), 'time' (s), 'distance' (m) veya 'hops'."""
        e = self._edge[(u, v)]
        if objective == "energy":
            return float(e[f"energy_{WIND_SUFFIX[wind_condition]}_wh"])
        if objective == "time":
            return float(e[f"time_{WIND_SUFFIX[wind_condition]}_s"])
        if objective == "distance":
            return float(e["distance_m"])
        if objective == "hops":
            return 1.0
        raise ValueError(objective)

    def straight_line_distance(self, a: str, b: str) -> float:
        """İki düğüm arası yatay düz çizgi (Öklid) mesafesi, metre (x_m, y_m kullanılır)."""
        pa, pb = self.nodes.loc[a], self.nodes.loc[b]
        return math.hypot(pb["x_m"] - pa["x_m"], pb["y_m"] - pa["y_m"])

    def path_totals(self, path: list[str], wind_condition: str) -> dict:
        """Bir yolun toplam enerji/süre/mesafe/adım sayısı. Geçersiz kenarda ValueError."""
        tot = {"energy_wh": 0.0, "time_s": 0.0, "distance_m": 0.0, "hops": max(0, len(path) - 1)}
        for a, b in zip(path, path[1:]):
            if (a, b) not in self._edge:
                raise ValueError(f"kenar yok: {a}->{b}")
            tot["energy_wh"] += self.edge_cost(a, b, wind_condition, "energy")
            tot["time_s"] += self.edge_cost(a, b, wind_condition, "time")
            tot["distance_m"] += self.edge_cost(a, b, wind_condition, "distance")
        return tot


def format_path(path: list[str] | None) -> str:
    return "|".join(path) if path else ""


SUBMISSION_COLUMNS = ["scenario_id", "algorithm", "success", "energy_wh", "time_s", "distance_m",
                      "expanded_nodes", "runtime_ms", "path"]


def write_submission(rows: list[dict], out_path: str | Path = "submission.csv") -> None:
    """rows: SUBMISSION_COLUMNS anahtarlarına sahip sözlükler. algorithm: BFS, UCS, GREEDY, ASTAR."""
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SUBMISSION_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in SUBMISSION_COLUMNS})
