"""Compute diode efficiency and standard errors."""

import argparse

from pandas import read_csv

p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
p.add_argument("path", help=".csv path")
args = p.parse_args()

df = read_csv(args.path)
if "ic+ from fit" in df:
    icp_col, icm_col = [f"ic{pm} from fit" for pm in "+-"]
else:
    icp_col, icm_col = [f"ic{pm}" for pm in "+-"]
df["delta"] = df[icp_col] - df[icm_col].abs()
df["delta_err"] = (df[["rmse+", "rmse-"]] ** 2).sum(axis=1) ** (1 / 2)
df["sigma"] = df[[icp_col, icm_col]].abs().sum(axis=1)
df["sigma_err"] = df["delta_err"]
df["eta"] = df["delta"] / df["sigma"]
df["eta_err"] = (
    (df["delta_err"] / df["sigma"]) ** 2
    + (df["eta"] * df["sigma_err"] / df["sigma"]) ** 2
) ** (1 / 2)
df.to_csv(args.path, index=False)
print(f"Computed diode: {args.path}")
