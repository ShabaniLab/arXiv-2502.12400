"""Compute Ic (arg)min/(arg)max from Ic±(B∥) fit parameters."""

import argparse

from pandas import read_csv

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    "path",
    help="path to csv containing Ic±(B∥) fits",
)
args = parser.parse_args()
df = read_csv(args.path)

df["ic_argmax"] = df["bstar"]
df["ic_argmin"] = -df["bstar"]
df["ic_argmax_err"] = df["bstar_err"]
df["ic_argmin_err"] = df["bstar_err"]

df["ic_max"] = df["imax"]
df["ic_min"] = -df["imax"]
df["ic_max_err"] = df["imax_err"]
df["ic_min_err"] = df["imax_err"]

df.to_csv(args.path, index=False)
print(f"Got argminmax from fits: {args.path}")
