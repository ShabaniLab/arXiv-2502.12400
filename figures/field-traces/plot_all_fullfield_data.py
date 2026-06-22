"""Plot all field (magnitude) dependence data.

Plot y(Β//, Wsc, Vg), where y is Ic or η.

Also plot extrema and argextrema (w.r.t. B//) of the above.
"""
import re
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from pandas import read_csv
from scipy.constants import physical_constants

Φ0 = physical_constants["mag. flux quantum"][0]

plt.style.use(["paper", "onethirdpage"])
WIDTH, HEIGHT = rcParams["figure.figsize"]
rcParams["figure.figsize"] = WIDTH, 2 * HEIGHT

root = Path("../../data/")
datapaths = list(root.glob("*/JS633-W2/*/data_deduped.csv"))
data = []
for path in datapaths:
    if "Wsc=inf-SSE_diode-3V/" in str(path):
        # skip Wsc=inf Vg=-3V scan with larger zero-field anomaly
        continue
    match = re.search(
        "Wsc=(\d\.\d|inf)(um)?-([A-Z]+)_diode([-+]\d\.?\d?)V.*$", path.parent.name
    )
    if match is None:
        continue
    wsc, _, cardinals, gate = match.groups()
    dset = dict(
        device=wsc + "-" + cardinals,
        wsc=float(wsc) * 1e-6,
        gate=float(gate),
        path=path,
    )
    data.append(dset)

BMAX = 1  # T

for dset in data:
    df = read_csv(dset["path"])
    df = df[(df.iloc[:, 0] <= BMAX) & (df.iloc[:, 0] >= -BMAX)]
    if "ic+ from fit" in df:
        pass
    elif "ic+ smoothed" in df:
        print(f"Using smoothed data for Wsc={dset['device']} Vg={dset['gate']}")
        for pm in "+-":
            df[f"ic{pm} from fit"] = df[f"ic{pm} smoothed"]
        df["delta"] = df["delta smoothed"]
        df["eta"] = df["eta smoothed"]
    else:
        print(f"Using non-fit data for Wsc={dset['device']} Vg={dset['gate']}")
        for pm in "+-":
            df[f"ic{pm} from fit"] = df[f"ic{pm}"]
    dset["dataframe"] = df


wsc_kwargs = {
    "0.3-N": dict(
        color="tab:purple",
        marker="x",
        label=r"$W_\mathrm{sc}=$0.3$\,$μm",
        fileprefix="Wsc=0.3um",
        zorder=8,
    ),
    "0.6-NNW": dict(
        color="tab:blue",
        marker="D",
        label=r"$W_\mathrm{sc}=$0.6$\,$μm",
        fileprefix="Wsc=0.6um",
        zorder=7,
    ),
    "0.9-ENE": dict(
        color="tab:green",
        marker="s",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm",
        fileprefix="Wsc=0.9um",
        zorder=6,
    ),
    "1.2-E": dict(
        color="tab:orange",
        marker="^",
        label=r"$W_\mathrm{sc}=$1.2$\,$μm",
        fileprefix="Wsc=1.2um",
        zorder=5,
    ),
    "inf-SSE": dict(
        color="tab:red",
        marker="o",
        label=r"$W_\mathrm{sc}\rightarrow\infty$",
        fileprefix="Wsc=inf",
        zorder=4,
    ),
}
gate_kwargs = {
    -1: dict(
        color="tab:red",
        marker="v",
        label=r"$V_\mathrm{g}<$0$\,$V",
        fileprefix="Vg=-V",
        zorder=6,
    ),
    0: dict(
        color="black",
        marker="o",
        label=r"$V_\mathrm{g}=$0$\,$V",
        fileprefix="Vg=0V",
        zorder=5,
    ),
    +1: dict(
        color="tab:blue",
        marker="^",
        label=r"$V_\mathrm{g}=$10$\,$V",
        fileprefix="Vg=10V",
        zorder=4,
    ),
}


def plot_vs_bpar(dsets, ic_extrema, eta_extrema, plotkwargs, title, fileprefix):
    """Plot Ic(B∥) and η(B∥).

    `dsets`, `ic_extrema`, `eta_extrema`, and `plotkwargs` should have same length and sort order.
    """
    fig, axs = plt.subplots(nrows=2, sharex=True)
    for ax in axs:
        ax.axhline(0, color="lightgrey", lw=0.5)
        ax.axvline(0, color="lightgrey", lw=0.5)
    axs[1].set_xlabel(r"$B_\parallel$ (T)")
    axs[0].set_ylabel(r"$I_\mathrm{c}$ (μA)")
    axs[1].set_ylabel(r"$\eta$ (%)")
    fig.suptitle(title)

    for i, (d, kwargs) in enumerate(zip(dsets, plotkwargs)):
        df = d["dataframe"]
        x = df.iloc[:, 0]

        # plot Ic(B∥)
        ic = df[["ic+ from fit", "ic- from fit"]].values
        icerr = df[["rmse+", "rmse-"]].values
        for ic_, icerr_ in zip(ic.T, icerr.T):
            # plot data
            axs[0].plot(
                x,
                ic_ / 1e-6,
                color=kwargs["color"],
                lw=1,
                zorder=kwargs["zorder"],
            )
            # plot uncertainty
            axs[0].fill_between(
                x,
                (ic_ + icerr_) / 1e-6,
                (ic_ - icerr_) / 1e-6,
                alpha=0.5,
                facecolor=kwargs["color"],
            )
        # plot Ic(B∥) extrema
        axs[0].plot(
            ic_extrema.iloc[i][["ic_argmin", "ic_argmax"]],
            ic_extrema.iloc[i][["ic_min", "ic_max"]] / 1e-6,
            color=kwargs["color"],
            marker=kwargs["marker"],
            ms=2,
            lw=0,
            zorder=10,
        )
        # for legend
        axs[1].plot(
            [],
            [],
            color=kwargs["color"],
            marker=kwargs["marker"],
            label=kwargs["label"],
        )

        # plot η(B∥)
        eta = df["eta"]
        etaerr = df["eta_err"]
        # plot data
        axs[1].plot(
            x,
            eta / 0.01,
            color=kwargs["color"],
            lw=1,
            zorder=kwargs["zorder"],
        )
        # plot uncertainty
        axs[1].fill_between(
            x,
            (eta + etaerr) / 0.01,
            (eta - etaerr) / 0.01,
            alpha=0.5,
            facecolor=kwargs["color"],
        )
        # plot η(B∥) extrema
        axs[1].plot(
            eta_extrema.iloc[i][["eta_argmin", "eta_argmax"]],
            eta_extrema.iloc[i][["eta_min", "eta_max"]] / 0.01,
            color=kwargs["color"],
            marker=kwargs["marker"],
            ms=2,
            lw=0,
            zorder=10,
        )

    axs[1].legend(fontsize="xx-small", loc="lower right")
    fig.savefig(fileprefix + f".{rcParams['savefig.format']}")


splines = read_csv(root / "spline_extrema.csv")
fits = read_csv(root / "icpm_fitparams.csv")
# Wsc traces (1 plot for each gate voltage)
for gate_sign in (-1, 0, 1):
    sort_wsc_up = False
    dsets = list(filter(lambda d: np.sign(d["gate"]) == gate_sign, data))
    dsets.sort(key=lambda d: d["wsc"], reverse=~sort_wsc_up)
    eta_extrema = splines[np.sign(splines["gate"]) == gate_sign]
    eta_extrema = eta_extrema.sort_values(by="wsc", ascending=sort_wsc_up)
    ic_extrema = fits[np.sign(fits["gate"]) == gate_sign]
    ic_extrema = ic_extrema.sort_values(by="wsc", ascending=sort_wsc_up)

    plotkwargs = [wsc_kwargs[d["device"]] for d in dsets]
    title = gate_kwargs[gate_sign]["label"]
    fileprefix = gate_kwargs[gate_sign]["fileprefix"]

    plot_vs_bpar(
        dsets, ic_extrema, eta_extrema, plotkwargs, title=title, fileprefix=fileprefix
    )

# gate traces (1 plot for each Wsc)
for device in wsc_kwargs.keys():
    sort_gate_up = False
    dsets = list(filter(lambda d: d["device"] == device, data))
    dsets.sort(key=lambda d: d["gate"], reverse=~sort_gate_up)
    eta_extrema = splines[splines["device"] == device]
    eta_extrema = eta_extrema.sort_values(by="gate", ascending=sort_gate_up)
    ic_extrema = fits[fits["device"] == device]
    ic_extrema = ic_extrema.sort_values(by="gate", ascending=sort_gate_up)

    plotkwargs = [gate_kwargs[np.sign(d["gate"])] for d in dsets]
    title = wsc_kwargs[device]["label"]
    fileprefix = wsc_kwargs[device]["fileprefix"]

    plot_vs_bpar(
        dsets, ic_extrema, eta_extrema, plotkwargs, title=title, fileprefix=fileprefix
    )
