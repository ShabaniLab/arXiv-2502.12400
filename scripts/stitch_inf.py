"""Stitch together data from Wsc=inf-SSE.

Some scans were interrupted by intermittent noise.

For the RMS error, since we don't have fraunhofer fits for each point, we just use the
current bias step size as a proxy for the uncertainty.
"""
from pathlib import Path

from pandas import concat, read_csv

root = "../data/processed/extract_ic/"
inprefix = root + "JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-"
outprefix = root + "JS633-W2/Wsc=inf-SSE_diode"


def save(dataframe, suffix):
    outdir = Path(outprefix + suffix)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "data.csv"
    dataframe.to_csv(outpath, index=False)
    print(f"Stitched {outpath}")


# -3V gate
scans = ["120", "121", "122"]
rmses = [20e-9, 5e-9, 2e-9]
dfs = [read_csv(inprefix + f"{scan}.csv") for scan in scans]
for df, rmse in zip(dfs, rmses):
    df[["rmse-", "rmse+"]] = rmse
df = concat(dfs)
save(df, "-3V")

# 0V gate
scans = ["078", "079", "082"]
rmses = [25e-9, 25e-9, 5e-9]
dfs = [read_csv(inprefix + f"{scan}.csv") for scan in scans]
for df, rmse in zip(dfs, rmses):
    df[["rmse-", "rmse+"]] = rmse
df = concat(dfs)
save(df[df["VectorMagnet - Field Z"] <= 1.5], "-0V")

# 10V gate
scans = ["101", "104", "109"]
rmses = [20e-9, 10e-9, 2e-9]
dfs = [read_csv(inprefix + f"{scan}.csv") for scan in scans]
for df, rmse in zip(dfs, rmses):
    df[["rmse-", "rmse+"]] = rmse
dfs[1] = dfs[1][dfs[1]["VectorMagnet - Field Z"] < 0.8]
df = concat(dfs)
save(df, "+10V")

# -3V gate, coarse field
df = read_csv(inprefix + f"156.csv")
df[["rmse-", "rmse+"]] = 25e-9
save(df, "-3V_coarsefield")
