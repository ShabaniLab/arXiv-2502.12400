"""Deduplicate data.

Ic+/- were measured multiple times at certain (Wsc, B//, Vg) configurations.

Some operations (e.g. cubic spline interpolation, savgol filtering, ...) require Ic(Wsc,
B//, Vg) to be a function and therefore require deduplication.  (I.e. can't have
multiple Ic's for the same (Wsc, B//, Vg).
"""
from pathlib import Path

from pandas import read_csv

TOL = 1e-9  # 1 nT tolerance for identifying duplicate field values

root = Path("../data/processed/")
datapaths = list(root.glob("*/JS633-W2/*/data_qca.csv"))
for datapath in datapaths:
    df = read_csv(datapath)
    # find duplicate field (column 0) values
    df = df.sort_values(df.columns[0])
    mask = df[df.columns[0]].diff() < TOL
    mask |= mask.shift(-1)
    dupes = df[mask].copy()
    # choose data points with the lowest average RMSE
    dupes["mean_rmse"] = dupes[["rmse+", "rmse-"]].mean(axis=1)
    dupes.sort_values([dupes.columns[0], "mean_rmse"], inplace=True)
    mask = dupes[df.columns[0]].diff() > TOL
    if len(mask) > 0:
        mask.iloc[0] = True
    keeps = dupes[mask]
    drop_idxs = dupes.index.difference(keeps.index)
    df.drop(index=drop_idxs, inplace=True)
    outpath = datapath.parent / "data_deduped.csv"
    df.to_csv(outpath, index=False)
    print(f"Deduped: {outpath}")
