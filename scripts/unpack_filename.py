"""Unpack device, Wsc, and gate info from filename."""
import argparse
import re

import numpy as np
from pandas import read_csv

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    "datapath",
    help="path to .csv file",
)
parser.add_argument(
    "--column",
    default="datapath",
    help="name of the column from which to extract the info",
)
args = parser.parse_args()

df = read_csv(args.datapath)
matches = [
    # *? = non-greedy *
    # (?: ) = non-capture group
    re.search("Wsc=(\d\.\d|inf)(?:um)?-([A-Z]+).*diode.*?([-+]?\d+(?:\.\d+)?)V", s)
    for s in df[args.column]
]
wsc, cardinals, gate = np.array([m.groups() for m in matches]).T
df["device"] = [f"{w}-{c}" for w, c in zip(wsc, cardinals)]
df["wsc"] = [float(w) * 1e-6 for w in wsc]
df["gate"] = [float(g) for g in gate]
df.to_csv(args.datapath, index=False)
print(f"Unpacked filename: {args.datapath}")
