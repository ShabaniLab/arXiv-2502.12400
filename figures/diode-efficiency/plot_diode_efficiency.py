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
        diode_col="eta" if wsc != "inf" else "eta smoothed",
        diode_err_col="eta_err",
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
splines["eta_extremum"] = splines[["eta_min", "eta_max"]].abs().mean(axis=1)
fits["ic_arg_extremum"] = fits[["ic_argmin", "ic_argmax"]].diff(axis=1).iloc[:, -1] / 2
splines["eta_arg_extremum"] = (
    splines[["eta_argmin", "eta_argmax"]].diff(axis=1).iloc[:, -1] / 2
)

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

# plot η(B//) @ Vg=0 forall Wsc
fig, ax = plt.subplots()
ax.set_xlabel(r"$B_\parallel$ (T)")
ax.set_ylabel(r"$\eta$ (%)")
ax.axhline(0, color="lightgrey", lw=0.5)
ax.axvline(0, color="lightgrey", lw=0.5)
ax.text(
    0.02, 0.02, r"$V_\mathrm{g}=$0$\,$V", transform=ax.transAxes, ha="left", va="bottom"
)
for i, d in enumerate(dsets):
    df = d["dataframe"]
    x = df.iloc[:, 0]
    y = df[d["diode_col"]]
    yerr = df[d["diode_err_col"]]

    # data
    ax.errorbar(
        x,
        y / (1 / 100),
        yerr=yerr / (1 / 100),
        color=wsc_kwargs[d["device"]]["color"],
        lw=1,
        elinewidth=0,
        zorder=wsc_kwargs[d["device"]]["zorder"],
    )
    # uncertainty
    ax.fill_between(
        x,
        (y + yerr) / (1 / 100),
        (y - yerr) / (1 / 100),
        alpha=0.5,
        facecolor=wsc_kwargs[d["device"]]["color"],
    )
    # extrema
    ax.errorbar(
        splines0V.iloc[i][["eta_argmin", "eta_argmax"]],
        splines0V.iloc[i][["eta_min", "eta_max"]] / (1 / 100),
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
fig.savefig(f"field-dependence.{rcParams['savefig.format']}")

fig, axs = plt.subplots(ncols=2)

# plot max[η](1/Wsc) @ Vg=0
ax = axs[0]
ax.set_xlabel(WSC_LABEL)
ax.set_ylabel(r"$\max\left|\eta\right|$ (%)")
ax.set_xticks(WSC_TICKS)
(norm,) = splines0V[splines0V["wsc"] == float("inf")]["eta_extremum"]
splines0V["log_eta_extremum"] = np.log(splines0V["eta_extremum"] / norm)
for i, extrema in splines0V.iterrows():
    x = 1 / extrema["wsc"]
    y = extrema["eta_extremum"]
    ax.plot(
        x / (1 / 1e-6),
        y / (1 / 100),
        color=wsc_kwargs[extrema["device"]]["color"],
        marker=wsc_kwargs[extrema["device"]]["marker"],
        ms=4,
    )

# plot argmax[η](1/Wsc) @ all gates
ax = axs[1]
ax.set_xlabel(WSC_LABEL)
ax.set_ylabel(r"$B_\eta$ (mT)")
ax.set_xticks(WSC_TICKS)
handles = []
for gate_sign in (1, 0, -1):
    gate_mask = np.sign(splines["gate"]) == gate_sign
    x = 1 / splines[gate_mask]["wsc"]
    y = splines[gate_mask]["eta_arg_extremum"]
    eb = ax.errorbar(
        x / (1 / 1e-6),
        y / 1e-3,
        label=gate_kwargs[gate_sign]["label"],
        color=gate_kwargs[gate_sign]["color"],
        marker=gate_kwargs[gate_sign]["marker"],
        ms=4,
        lw=0,
        elinewidth=1,
    )
    handles.append(eb)
legend = ax.legend(handles=handles, loc="lower right", fontsize="xx-small")
ax.add_artist(legend)
# fit for flux fraction
finite_mask = np.isfinite(splines0V["wsc"])
fit = Polynomial.fit(
    1 / splines0V[finite_mask]["wsc"], splines0V[finite_mask]["eta_arg_extremum"], 1
)
slope = fit.convert().coef[1]
fluxfrac = slope / Φ0
print(f"Fit argmax(η): {slope=:+.3e} T.m\t Φ/Φ0={fluxfrac / (1 / 1e-9):.6f} x d[nm]")
(line,) = ax.plot(
    1 / (splines0V["wsc"] / 1e-6),
    fit(1 / splines0V["wsc"]) / 1e-3,
    color="k",
    lw=1,
    zorder=-1,
    label=r"$\dfrac{\Phi}{\Phi_0}=$"
    f"{fluxfrac / (1 / 1e-9):.3f}"
    r"$\,$nm$^{-1}$"
    r"$\times d$",
)
ax.legend(handles=[line], loc="upper left", fontsize="xx-small")
# add vertical line at 1/2ξ
inverse_2ξ = 1 / (586e-9 * 2)
ax.axvline(inverse_2ξ / 1e6, color="k", ls="--", lw=0.5)
ax.text(inverse_2ξ / 1e6 + 0.05, 200, r"$(2\xi)^{-1}$", fontsize="xx-small")
ax.set_ylim((0, None))

fig.savefig(f"wsc-dependence.{rcParams['savefig.format']}")
