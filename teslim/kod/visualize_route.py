"""Rota görselleştirme (çevrimiçi harita GEREKMEZ; yerel x_m / y_m koordinatları kullanılır).

Örnekler:
    python visualize_route.py
    python visualize_route.py --path "N001|N005|N011" --wind MEDIUM_WIND --out rota.png
    python visualize_route.py --path "N001|N005" --path "N001|N007|N005" --label BFS --label UCS
"""
from __future__ import annotations

import argparse

import matplotlib.pyplot as plt

from graph_utils import UAVGraph
from load_data import load_edges, load_nodes


def plot_graph(nodes, edges, ax=None, show_ids=True):
    ax = ax or plt.gca()
    xy = nodes.set_index("node_id")[["x_m", "y_m"]]
    for src, style in [("model_estimated", dict(color="#bbbbbb", lw=0.6, ls="--")),
                       ("observed_real", dict(color="#4a7bb7", lw=1.0, ls="-"))]:
        e = edges[edges["edge_source"] == src]
        for u, v in zip(e["u"], e["v"]):
            ax.plot([xy.at[u, "x_m"], xy.at[v, "x_m"]], [xy.at[u, "y_m"], xy.at[v, "y_m"]], zorder=1, **style)
    sc = ax.scatter(nodes["x_m"], nodes["y_m"], c=nodes["altitude_m"], cmap="viridis", s=22, zorder=2)
    if show_ids:
        for r in nodes.itertuples():
            ax.annotate(r.node_id[1:], (r.x_m, r.y_m), fontsize=5, xytext=(2, 2), textcoords="offset points")
    plt.colorbar(sc, ax=ax, label="irtifa (m, kalkış noktasına göre)")
    ax.plot([], [], color="#4a7bb7", label="gözlenen gerçek kenar")
    ax.plot([], [], color="#bbbbbb", ls="--", label="model ile kestirilen kenar")
    ax.set_aspect("equal")
    ax.set_xlabel("x_m (Doğu, m)")
    ax.set_ylabel("y_m (Kuzey, m)")
    return ax


def plot_path(nodes, path, ax, label, color, wind=None, graph=None):
    xy = nodes.set_index("node_id")[["x_m", "y_m"]]
    xs = [xy.at[n, "x_m"] for n in path]
    ys = [xy.at[n, "y_m"] for n in path]
    if graph is not None and wind:
        t = graph.path_totals(path, wind)
        label = f"{label}: {t['energy_wh']:.2f} Wh, {t['time_s']:.0f} s, {t['distance_m']:.0f} m, {t['hops']} kenar"
    ax.plot(xs, ys, color=color, lw=2.5, label=label, zorder=3)
    ax.scatter([xs[0]], [ys[0]], marker="o", s=80, color=color, edgecolor="k", zorder=4)
    ax.scatter([xs[-1]], [ys[-1]], marker="*", s=160, color=color, edgecolor="k", zorder=4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", action="append", default=[], help='"N001|N005|..." (birden çok verilebilir)')
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--wind", default="MEDIUM_WIND", choices=["LOW_WIND", "MEDIUM_WIND", "HIGH_WIND"])
    ap.add_argument("--out", default=None, help="PNG dosyası (verilmezse ekranda gösterilir)")
    a = ap.parse_args()
    nodes, edges = load_nodes(), load_edges()
    g = UAVGraph(nodes, edges)
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_graph(nodes, edges, ax)
    colors = ["#d62728", "#2ca02c", "#ff7f0e", "#9467bd"]
    for i, p in enumerate(a.path):
        lab = a.label[i] if i < len(a.label) else f"rota {i + 1}"
        plot_path(nodes, p.split("|"), ax, lab, colors[i % len(colors)], a.wind, g)
    ax.legend(loc="best", fontsize=8)
    ax.set_title(f"UAV rota grafı ({a.wind})")
    fig.tight_layout()
    if a.out:
        fig.savefig(a.out, dpi=200)
        print("kaydedildi:", a.out)
    else:
        plt.show()


if __name__ == "__main__":
    main()
