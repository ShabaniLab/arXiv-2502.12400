"""Apply Savitzky-Golay filter to Wsc=inf data."""
from pathlib import Path

from pandas import read_csv
from scipy.signal import savgol_filter

root = Path("../data/processed/")
paths = list(root.glob("*/JS633-W2/Wsc=inf*V*/data_deduped.csv"))
for path in paths:
    df = read_csv(path)
    savgol_args = (15, 3)  # window_len, (>) polyorder
    df["ic+ smoothed"] = savgol_filter(df["ic+"], *savgol_args)
    df["ic- smoothed"] = savgol_filter(df["ic-"], *savgol_args)
    df["delta smoothed"] = savgol_filter(df["delta"], *savgol_args)
    df["eta smoothed"] = savgol_filter(df["eta"], *savgol_args)
    df.to_csv(path, index=False)
    print(f"Smoothed: {path}")
