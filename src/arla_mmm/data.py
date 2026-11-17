"""Data loading and shared constants."""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "data" / "arla_protein_mmm_weekly.csv"
RESULTS_DIR = REPO_ROOT / "results" / "part2"

CHANNELS = ["tv", "instagram", "tiktok", "influencer", "pos_promotion"]


def load_data(path: str | Path | None = None) -> pd.DataFrame:
    """Weekly data, one row per week, sorted, with a 0..n-1 integer index."""
    df = pd.read_csv(path or DATA_PATH, parse_dates=["week_beg"])
    df = df.sort_values("week_beg").reset_index(drop=True)
    if df.isna().any().any() or df["week_beg"].duplicated().any():
        raise ValueError("data has missing values or duplicate weeks")
    return df
