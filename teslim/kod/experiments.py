import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from graph_utils import UAVGraph
from load_data import load_nodes, load_edges, PACKAGE_DIR
from visualize_route import plot_graph, plot_path
from ucs import ucs

out = PACKAGE_DIR / "figures"; out.mkdir(exist_ok=True)
nodes, edges = load_nodes(), load_edges()
g = UAVGraph(nodes, edges)
sub = pd.read_csv(PACKAGE_DIR / "submission.csv")

num = ["energy_wh", "time_s", "distance_m", "expanded_nodes", "runtime_ms"]
tab = sub.groupby("algorithm")[num].mean().reindex(["BFS", "UCS", "GREEDY", "ASTAR"]).round(3)
tab.to_csv(out / "ozet_tablo.csv"); print(tab)
fig, axs = plt.subplots(1, 5, figsize=(17, 3.2))
titles = ["Enerji (Wh)", "Süre (s)", "Mesafe (m)", "Genişletilen düğüm", "Çalışma süresi (ms)"]
for ax, c, t in zip(axs, num, titles):
    ax.bar(tab.index, tab[c], color=["#999", "#2ca02c", "#ff7f0e", "#d62728"]); ax.set_title(t, fontsize=10)
    ax.tick_params(axis="x", labelsize=8)
fig.tight_layout(); fig.savefig(out / "karsilastirma.png", dpi=200); plt.close(fig)

p = sub.pivot(index="scenario_id", columns="algorithm", values="expanded_nodes")
fig, ax = plt.subplots(figsize=(10, 3.5)); p[["UCS", "ASTAR", "GREEDY", "BFS"]].plot.bar(ax=ax)
ax.set_ylabel("genişletilen düğüm"); fig.tight_layout(); fig.savefig(out / "genisletilen.png", dpi=200); plt.close(fig)

S, T = "N001", "N092"
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
for ax, w in zip(axs, ["LOW_WIND", "MEDIUM_WIND", "HIGH_WIND"]):
    plot_graph(nodes, edges, ax, show_ids=False)
    path = ucs(g, S, T, w)
    plot_path(nodes, path, ax, "UCS rotası", "#d62728", w, g)
    ax.set_title(f"{S}→{T}  {w}"); ax.legend(fontsize=7, loc="lower right")
    print(w, "|".join(path), g.path_totals(path, w))
fig.tight_layout(); fig.savefig(out / "ruzgar_etkisi.png", dpi=170); plt.close(fig)

sub2 = pd.read_csv(PACKAGE_DIR / "submission.csv"); sid, w = "T08", "MEDIUM_WIND"
fig, ax = plt.subplots(figsize=(12, 7)); plot_graph(nodes, edges, ax, show_ids=False)
cols = {"BFS": "#7f7f7f", "GREEDY": "#ff7f0e", "UCS": "#2ca02c"}
for a in ["GREEDY", "BFS", "UCS"]:
    pth = sub2[(sub2.scenario_id == sid) & (sub2.algorithm == a)].path.iloc[0].split("|")
    plot_path(nodes, pth, ax, a, cols[a], w, g)
ax.set_title(f"{sid} ({w}): BFS, Greedy ve UCS/A* rotaları (UCS ve A* aynı)"); ax.legend(fontsize=8, loc="best")
fig.tight_layout(); fig.savefig(out / "rota_karsilastirma_T08.png", dpi=170)
