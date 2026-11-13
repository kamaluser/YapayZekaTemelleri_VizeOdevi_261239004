import sys, time
import pandas as pd
from graph_utils import UAVGraph, write_submission, format_path
from load_data import load_nodes, load_edges, PACKAGE_DIR
from bfs import bfs
from ucs import ucs
from greedy import greedy_best_first
from astar import astar


def run(files, out):
    g = UAVGraph(load_nodes(), load_edges())
    scen = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    rows = []
    for s in scen.itertuples():
        w = s.wind_condition
        calls = {"BFS": lambda: bfs(g, s.start_node, s.goal_node),
                 "UCS": lambda: ucs(g, s.start_node, s.goal_node, w),
                 "GREEDY": lambda: greedy_best_first(g, s.start_node, s.goal_node),
                 "ASTAR": lambda: astar(g, s.start_node, s.goal_node, w)}
        for name, fn in calls.items():
            g.reset_counter()
            t0 = time.perf_counter()
            p = fn()
            ms = (time.perf_counter() - t0) * 1000
            r = {"scenario_id": s.scenario_id, "algorithm": name, "success": p is not None,
                 "expanded_nodes": g.expansions, "runtime_ms": round(ms, 4), "path": format_path(p)}
            if p:
                t = g.path_totals(p, w)
                r.update(energy_wh=round(t["energy_wh"], 6), time_s=round(t["time_s"], 4),
                         distance_m=round(t["distance_m"], 3))
            rows.append(r)
    write_submission(rows, out)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    files = sys.argv[1:] or [PACKAGE_DIR / "train_scenarios.csv"]
    df = run(files, PACKAGE_DIR / "submission.csv")
    num = ["energy_wh", "time_s", "distance_m", "expanded_nodes", "runtime_ms"]
    print(df.groupby("algorithm")[num].mean().round(3))
    print(df.groupby("algorithm")["success"].mean().to_dict())
