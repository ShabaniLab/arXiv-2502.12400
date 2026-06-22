"""Invert current polarity to conform to diode sign convention.

Sign convention: (IxB).z > 0 where
- I is the positive direction of current
- B is the positive direction of the in-plane field axis perpendicular to the current
- z is the direction of growth (from substrate to Al)

If (IxB).z < 0, we manually swap ic+ and ic-, etc.

Three devices were hooked up with the opposite current bias polarity:
- Wsc=0.3um-N
- Wsc=0.6um-NNW
- Wsc=0.9um-NNE (WFS06)
"""

import argparse as ap

from pandas import read_csv

parser = ap.ArgumentParser(
    description=__doc__, formatter_class=ap.ArgumentDefaultsHelpFormatter
)
parser.add_argument("paths", nargs="+", help="one or more paths to csv files")
args = parser.parse_args()


def rename(colname):
    if colname in (
        "ic+",
        "ic-",
        "center+",
        "center-",
        "ic+ from fit",
        "ic- from fit",
        "rmse+",
        "rmse-",
        "#points in +fit",
        "#points in -fit",
    ):
        return colname.replace("+", "~").replace("-", "+").replace("~", "-")
    else:
        return colname


for path in args.paths:
    csv = read_csv(path)
    csv.rename(columns=rename, inplace=True)
    csv.loc[:, ["ic+", "ic-", "ic+ from fit", "ic- from fit"]] *= -1
    csv.to_csv(path, index=False)
    print(f"Inverted current: {path}")
