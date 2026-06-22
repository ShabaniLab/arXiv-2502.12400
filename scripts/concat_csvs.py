"""Concatenate csv files."""

import argparse
from os.path import commonpath
from pathlib import Path

import pandas as pd

p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
p.add_argument("paths", help=".csv paths", nargs="+")
p.add_argument(
    "--output_filename",
    "-o",
    help="name of the concatenated output file",
    default="data_concat.csv",
)
p.add_argument(
    "--rename-from",
    "--rename",
    help="rename column `--rename-from` to `--rename-to` before concatenating",
    default=[],
    action="append",
)
p.add_argument(
    "--rename-to",
    "--to",
    help="rename column `--rename-from` to `--rename-to` before concatenating",
    default=[],
    action="append",
)
p.add_argument(
    "--force-write",
    "-f",
    help="force overwrite output data; otherwise you will be prompted",
    action="store_true",
)
args = p.parse_args()
if len(args.rename_from) != len(args.rename_to):
    raise ValueError(
        "`--rename_from` and `--rename_to` must be the same length."
        "\n--rename_from=\n{pformat(args.rename_from)}"
        "\n--rename_to=\n{pformat(args.rename_to)}"
    )
rename_map = {from_: to for from_, to in zip(args.rename_from, args.rename_to)}
if not args.output_filename.endswith(".csv"):
    args.output_filename += ".csv"
outdir = Path(commonpath(args.paths))

dfs = [pd.read_csv(path) for path in args.paths]
if rename_map:
    for df in dfs:
        df.rename(columns=rename_map, inplace=True)
for df, path in zip(dfs, args.paths):
    df["parent_csv"] = Path(path).relative_to(outdir)

df = pd.concat(dfs)

outpath = outdir / args.output_filename
if outpath.exists() and not args.force_write:
    overwrite = None
    while overwrite not in ("y", "n"):
        overwrite = input(f"{outpath} already exists.  Overwrite? [y/n]: ").lower()
    write = overwrite == "y"
else:
    write = True
if write:
    df.to_csv(outpath, index=False)
    print(f"Concatenated: {outpath}")
