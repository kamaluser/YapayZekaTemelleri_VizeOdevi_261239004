"""YZM537 Vize Projesi - veri yükleme yardımcıları.

Kullanım:
    python load_data.py            # veri setinin kısa özetini yazdırır

Dosyalar (paket kök dizininde):
    nodes.csv            düğümler (node_id, x_m, y_m, latitude, longitude, altitude_m, node_source)
    edges.csv            yönlü kenarlar ve rüzgâr koşullarına göre maliyetler
    train_scenarios.csv  açık eğitim senaryoları
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PACKAGE_DIR = Path(__file__).resolve().parents[1]

# Senaryo dosyasındaki rüzgâr adı -> edges.csv sütun soneki
WIND_SUFFIX = {"LOW_WIND": "low_wind", "MEDIUM_WIND": "medium_wind", "HIGH_WIND": "high_wind"}


def load_nodes(data_dir: Path = PACKAGE_DIR) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / "nodes.csv")


def load_edges(data_dir: Path = PACKAGE_DIR) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / "edges.csv")


def load_scenarios(data_dir: Path = PACKAGE_DIR, name: str = "train_scenarios.csv") -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / name)


def load_all(data_dir: Path = PACKAGE_DIR):
    return load_nodes(data_dir), load_edges(data_dir), load_scenarios(data_dir)


def energy_column(wind_condition: str) -> str:
    """Örn. 'HIGH_WIND' -> 'energy_high_wind_wh'"""
    return f"energy_{WIND_SUFFIX[wind_condition]}_wh"


def time_column(wind_condition: str) -> str:
    return f"time_{WIND_SUFFIX[wind_condition]}_s"


if __name__ == "__main__":
    nodes, edges, scenarios = load_all()
    print(f"Düğüm sayısı      : {len(nodes)}")
    print(f"Yönlü kenar sayısı: {len(edges)}")
    print(f"  gerçek uçuşta gözlenen (observed_real) : {(edges['edge_source'] == 'observed_real').sum()}")
    print(f"  model ile kestirilen (model_estimated)  : {(edges['edge_source'] == 'model_estimated').sum()}")
    print(f"Eğitim senaryosu  : {len(scenarios)}")
    print(scenarios.head())
