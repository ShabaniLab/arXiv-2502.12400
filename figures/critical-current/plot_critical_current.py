# TODO: missing factor of 2 in coherence length fit?  (wavefunction squared)
import re
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from numpy.polynomial import Polynomial
from pandas import read_csv
from scipy.constants import physical_constants

# constants
Φ0 = physical_constants["mag. flux quantum"][0]
BMAX = 1  # T
WSC_LABEL = r"$W_\mathrm{sc}^{-1}$ (μm$^{-1}$)"
WSC_TICKS = list(range(4))

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
splines = read_csv(root / "spline_extrema.csv")
fits = read_csv(root / "icpm_fitparams.csv")
# use Wsc=inf Vg=-3V scan with less-pronounced 0-field dip anomaly
fits.drop(
    fits[fits["datapath"].str.contains("/Wsc=inf-SSE_diode-3V/")].index, inplace=True
)

# calculate quantities to plot
fits["ic_extremum"] = fits[["ic_min", "ic_max"]].abs().mean(axis=1)
fits["ic_arg_extremum"] = fits[["ic_argmin", "ic_argmax"]].diff(axis=1).iloc[:, -1] / 2

# plot parameters
wsc_kwargs = {
    "0.3-N": dict(
        color="tab:purple",
        marker="x",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.3μm",
        zorder=8,
    ),
    "0.6-NNW": dict(
        color="tab:blue",
        marker="D",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.6μm",
        zorder=7,
    ),
    "0.9-ENE": dict(
        color="tab:green",
        marker="s",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9μm",
        zorder=6,
    ),
    "1.2-E": dict(
        color="tab:orange",
        marker="^",
        ls="solid",
        label=r"$W_\mathrm{sc}=$1.2μm",
        zorder=5,
    ),
    "inf-SSE": dict(
        color="tab:red",
        marker="o",
        ls="solid",
        label=r"$W_\mathrm{sc}\rightarrow\infty$",
        zorder=4,
    ),
}
gate_kwargs = {
    -1: dict(
        color="tab:red",
        marker="v",
        ls="solid",
        label=r"$V_\mathrm{g}<$0$\,$V",
        zorder=6,
    ),
    0: dict(
        color="black",
        marker="o",
        ls="solid",
        label=r"$V_\mathrm{g}=$0$\,$V",
        zorder=5,
    ),
    +1: dict(
        color="tab:blue",
        marker="^",
        ls="solid",
        label=r"$V_\mathrm{g}=$10$\,$V",
        zorder=4,
    ),
}

# figure setup
plt.style.use(["paper", "fullcolumn"])

# sort
sort_up = False
data.sort(key=lambda d: d["gate"], reverse=~sort_up)
data.sort(key=lambda d: d["wsc"], reverse=~sort_up)
splines = splines.sort_values(by=["wsc", "gate"], ascending=[sort_up, sort_up])
fits = fits.sort_values(by=["wsc", "gate"], ascending=[sort_up, sort_up])

# filter for Vg=0
dsets = list(filter(lambda d: d["gate"] == 0, data))
splines0V = splines[splines["gate"] == 0].copy()
fits0V = fits[fits["gate"] == 0].copy()

# plot Ic(B//) @ Vg=0 forall Wsc
fig, ax = plt.subplots()
ax.set_xlabel(r"$B_\parallel$ (T)")
ax.set_ylabel(r"$I_\mathrm{c}$ (μA)")
ax.axhline(0, color="lightgrey", lw=0.5)
ax.axvline(0, color="lightgrey", lw=0.5)
ax.text(
    0.02, 0.02, r"$V_\mathrm{g}=$0$\,$V", transform=ax.transAxes, ha="left", va="bottom"
)
for i, d in enumerate(dsets):
    df = d["dataframe"]
    x = df.iloc[:, 0]
    y = df[d["ic_cols"]]
    yerr = df[d["ic_err_cols"]]
    for y_, yerr_ in zip(y.T.values, yerr.T.values):
        # data
        ax.errorbar(
            x,
            y_ / 1e-6,
            yerr=yerr_ / 1e-6,
            color=wsc_kwargs[d["device"]]["color"],
            lw=1,
            elinewidth=0,
            zorder=wsc_kwargs[d["device"]]["zorder"],
        )
        # uncertainty
        ax.fill_between(
            x,
            (y_ + yerr_) / 1e-6,
            (y_ - yerr_) / 1e-6,
            alpha=0.5,
            facecolor=wsc_kwargs[d["device"]]["color"],
        )
    # extrema
    ax.errorbar(
        fits0V.iloc[i][["ic_argmin", "ic_argmax"]],
        fits0V.iloc[i][["ic_min", "ic_max"]] / 1e-6,
        color=wsc_kwargs[d["device"]]["color"],
        marker=wsc_kwargs[d["device"]]["marker"],
        ms=2,
        lw=0,
        zorder=10,
    )
    # legend
    ax.errorbar(
        [],
        [],
        color=wsc_kwargs[d["device"]]["color"],
        marker=wsc_kwargs[d["device"]]["marker"],
        ls=wsc_kwargs[d["device"]]["ls"],
        label=wsc_kwargs[d["device"]]["label"],
    )
    ax.legend(fontsize="xx-small", loc="upper left")
# constrained layout cuts off y-axis label, use bbox_inches
fig.savefig(f"field-dependence.{rcParams['savefig.format']}", bbox_inches="tight")

fig, axs = plt.subplots(ncols=2)

# plot 1/logmax[Ic...](1/Wsc) @ Vg=0
ax = axs[0]
ax.set_xlabel(WSC_LABEL)
ax.set_xticks(WSC_TICKS)
ax.set_ylabel(
    r"$1 / \ln\left(\frac"
    r"{I_\mathrm{c}^\infty}"
    r"{I_\mathrm{c}^\infty - \max|I_{\mathrm{c}\pm}|}"
    r"\right)$"
)
(ic_inf,) = fits0V[fits0V["wsc"] == float("inf")]["ic_extremum"]
fits0V["1/ln"] = 1 / np.log(ic_inf / (ic_inf - fits0V["ic_extremum"]))
for i, extrema in fits0V.iterrows():
    x = 1 / extrema["wsc"]
    y = extrema["1/ln"]
    ax.plot(
        x / (1 / 1e-6),
        y,
        color=wsc_kwargs[extrema["device"]]["color"],
        marker=wsc_kwargs[extrema["device"]]["marker"],
        ms=4,
    )
fit = Polynomial.fit(1 / fits0V["wsc"], fits0V["1/ln"], 1)
xi_nm = fit.convert().coef[1] / 1e-9
print(f"Fit logmax(Ic): ξ = {xi_nm} nm")
ax.plot(
    1 / (fits0V["wsc"] / 1e-6),
    fit(1 / fits0V["wsc"]),
    color="k",
    lw=1,
    zorder=-1,
    label=r"$\xi=$" f"{xi_nm:.0f}" r"$\,$nm",
)
ax.legend(fontsize="xx-small")

# plot B* = argmax[Ic](1/Wsc) @ all gates
ax = axs[1]
ax.set_xlabel(WSC_LABEL)
ax.set_xticks(WSC_TICKS)
ax.set_ylabel(r"$B_*$ (mT)")
for gate_sign in (1, 0, -1):
    gate_mask = np.sign(fits["gate"]) == gate_sign
    x = 1 / fits[gate_mask]["wsc"]
    y = fits[gate_mask]["ic_arg_extremum"]
    ax.errorbar(
        x / (1 / 1e-6),
        y / 1e-3,
        yerr=fits[gate_mask]["bstar_err"] / 1e-3,
        label=gate_kwargs[gate_sign]["label"],
        color=gate_kwargs[gate_sign]["color"],
        marker=gate_kwargs[gate_sign]["marker"],
        ms=4,
    )
ax.legend(fontsize="xx-small")

fig.savefig(f"wsc-dependence.{rcParams['savefig.format']}")
