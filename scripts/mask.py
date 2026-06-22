"""Remove pathological data points.

Points to remove and why are tabulated in quality-control.csv adjacent to each datafile.
"""
from pathlib import Path
from warnings import warn

import numpy as np
from pandas import read_csv

root = Path("../data/processed/")
datapaths = list(root.glob("*/JS633-W2/*/data.csv"))
for datapath in datapaths:
    df = read_csv(datapath)
    qcpath = datapath.parent / "quality-control.csv"
    if qcpath.exists():
        qc = read_csv(qcpath)
        for _, row in qc.iterrows():
            dropidx = df.index[
                np.isclose(df.iloc[:, 0], row["field"])
                & (df["datafile"] == row["datafile"])
            ]
            if len(dropidx) > 0:
                df.drop(index=dropidx, inplace=True)
            else:
                warn(f"Mask did not apply ({row['field']}, {row['datafile']})")
    outpath = datapath.parent / "data_qca.csv"
    df.to_csv(outpath, index=False)
    print(f"Masked: {outpath}")
