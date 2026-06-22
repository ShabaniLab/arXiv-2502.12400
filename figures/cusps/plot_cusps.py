"""Cusps in Ic(B∥) correspond to rapid changes in critical/switching phase φc.

See e.g. costa2023_diodeMicroscopic Fig. 7
https://journals.aps.org/prb/abstract/10.1103/PhysRevB.108.054522

These cusps are weak but visible in the data and depend on Wsc.  Try to bring them out
by analyzing at the 2nd derivative: a cusp is a segment with rapidly changing slope i.e.
large 2nd derivative.
"""

import re
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from pandas import read_csv
from scipy.constants import physical_constants
from scipy.signal import savgol_filter

# constants
Φ0 = physical_constants["mag. flux quantum"][0]
BMAX = 0.8  # T
WSC_LABEL = r"$W_\mathrm{sc}^{-1}$ (μm$^{-1}$)"
WSC_TICKS = list(range(4))
FIGSIZE = 3.375, 3.375


# load data
root = Path("../../data/")
datapaths = list(root.glob("*/JS633-W2/*/data_deduped.csv"))
data = []
for path in datapaths:
    match = re.search(
        "Wsc=(\d\.\d|inf)(um)?-([A-Z]+)_diode([-+]\d\.?\d?)V$", path.parent.name
    )
    if match is None:
        continue
    wsc, _, cardinals, gate = match.groups()
    dset = dict(
        device=wsc + "-" + cardinals,
        wsc=float(wsc) * 1e-6,
        gate=float(gate),
        path=path,
        ic_cols=(
            ["ic+ from fit", "ic- from fit"]
            if wsc != "inf"
            else ["ic+ smoothed", "ic- smoothed"]
        ),
        ic_err_cols=["rmse+", "rmse-"],
    )
    df = read_csv(path)
    df = df[(df.iloc[:, 0] <= BMAX) & (df.iloc[:, 0] >= -BMAX)]
    dset["dataframe"] = df
    data.append(dset)

# plot parameters
wsc_kwargs = {
    "0.3-N": dict(
        color="tab:purple",
        marker="x",
        label=r"$W_\mathrm{sc}=$0.3μm",
        zorder=8,
    ),
    "0.6-NNW": dict(
        color="tab:blue",
        marker="D",
        label=r"$W_\mathrm{sc}=$0.6μm",
        zorder=7,
    ),
    "0.9-ENE": dict(
        color="tab:green",
        marker="s",
        label=r"$W_\mathrm{sc}=$0.9μm",
        zorder=6,
    ),
    "1.2-E": dict(
        color="tab:orange",
        marker="^",
        label=r"$W_\mathrm{sc}=$1.2μm",
        zorder=5,
    ),
    "inf-SSE": dict(
        color="tab:red",
        marker="o",
        label=r"$W_\mathrm{sc}\rightarrow\infty$",
        zorder=4,
    ),
}

# figure setup
plt.style.use(["paper", "fullcolumn"])

# sort
sort_up = False
data.sort(key=lambda d: d["gate"], reverse=~sort_up)
data.sort(key=lambda d: d["wsc"], reverse=~sort_up)

# filter for Vg=0
dsets = list(filter(lambda d: d["gate"] == 0, data))

# plot Ic(B∥)
fig0, ax0 = plt.subplots(nrows=2, sharex=True, figsize=FIGSIZE)
ax0[-1].set_xlabel(r"$B_\parallel$ (T)")
ax0[0].set_ylabel(r"$I_{\mathrm{c}+}$ (μA)")
ax0[1].set_ylabel(r"$I_{\mathrm{c}-}$ (μA)")
for ax in ax0:
    ax.axvline(0, color="grey", lw=0.5)

# plot 1st derivative of Ic(B∥)
fig1, ax1 = plt.subplots(nrows=2, sharex=True, figsize=FIGSIZE)
ax1[-1].set_xlabel(r"$B_\parallel$ (T)")
ax1[0].set_ylabel(r"$\partial_B I_{\mathrm{c}+}$ (μA/T)")
ax1[1].set_ylabel(r"$\partial_B I_{\mathrm{c}-}$ (μA/T)")
for ax in ax1:
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)

# plot 2nd derivative of Ic(B∥)
fig2, ax2 = plt.subplots(nrows=2, sharex=True, figsize=FIGSIZE)
ax2[-1].set_xlabel(r"$B_\parallel$ (T)")
ax2[0].set_ylabel(r"$\partial_B^2 I_{\mathrm{c}+}$ (μA/T$^2$)")
ax2[1].set_ylabel(r"$\partial_B^2 I_{\mathrm{c}-}$ (μA/T$^2$)")
for ax in ax2:
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)

# plot for all Wsc @ Vg=0
for i, d in enumerate(dsets):
    df = d["dataframe"]

    # Ic(B∥)
    x = df.iloc[:, 0].values
    y = df[d["ic_cols"]].values
    # downsample Wsc=inf data
    # if d["device"] == "inf-SSE":
    #    x = x[::3]
    #    y = y[::3]
    for ax, y_ in zip(ax0, y.T):
        ax.plot(
            x,
            y_ / 1e-6,
            color=wsc_kwargs[d["device"]]["color"],
            lw=1,
            # marker=wsc_kwargs[d["device"]]["marker"],
            zorder=wsc_kwargs[d["device"]]["zorder"],
        )

    # 1st derivative of Ic(B∥)
    dydx = np.gradient(y, x, axis=0)
    # smooth Wsc=inf data
    if d["device"] == "inf-SSE":
        dydx = savgol_filter(dydx, window_length=15, polyorder=3, axis=0)
    for ax, dydx_ in zip(ax1, dydx.T):
        ax.plot(
            x,
            dydx_ / 1e-6,
            color=wsc_kwargs[d["device"]]["color"],
            lw=1,
            # marker=wsc_kwargs[d["device"]]["marker"],
            zorder=wsc_kwargs[d["device"]]["zorder"],
        )

    # 2nd derivative of Ic(B∥)
    d2ydx2 = np.gradient(dydx, x, axis=0)
    # smooth Wsc=inf data
    if d["device"] == "inf-SSE":
        d2ydx2 = savgol_filter(d2ydx2, window_length=15, polyorder=3, axis=0)
    for ax, d2ydx2_ in zip(ax2, d2ydx2.T):
        ax.plot(
            x,
            d2ydx2_ / 1e-6,
            color=wsc_kwargs[d["device"]]["color"],
            lw=1,
            # marker=wsc_kwargs[d["device"]]["marker"],
            zorder=wsc_kwargs[d["device"]]["zorder"],
        )

    # legends
    for ax in (ax0[0], ax1[0], ax2[0]):
        ax.plot(
            [],
            [],
            color=wsc_kwargs[d["device"]]["color"],
            # marker=wsc_kwargs[d["device"]]["marker"],
            label=wsc_kwargs[d["device"]]["label"],
        )
        ax.legend(fontsize="xx-small")

ax0[0].set_ylim((0, None))
ax0[1].set_ylim((None, 0))
ax2[0].set_ylim((0, None))
ax2[1].set_ylim((None, 0))

fig0.savefig(f"Ic.{rcParams['savefig.format']}")
fig1.savefig(f"Ic-1st-derivative.{rcParams['savefig.format']}")
fig2.savefig(f"Ic-2nd-derivative.{rcParams['savefig.format']}")
