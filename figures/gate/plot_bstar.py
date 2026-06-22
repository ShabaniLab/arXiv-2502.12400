import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from numpy.polynomial import Polynomial
from pandas import read_csv

plt.style.use(["paper", "fullcolumn"])
wsc_kwargs = {
    "0.3-N": dict(
        color="tab:purple",
        marker="x",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.3$\,$μm",
        zorder=8,
    ),
    "0.6-NNW": dict(
        color="tab:blue",
        marker="D",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.6$\,$μm",
        zorder=7,
    ),
    "0.9-ENE": dict(
        color="tab:green",
        marker="s",
        ls="solid",
        label=r"$W_\mathrm{sc}=$0.9$\,$μm",
        zorder=6,
    ),
    "1.2-E": dict(
        color="tab:orange",
        marker="^",
        ls="solid",
        label=r"$W_\mathrm{sc}=$1.2$\,$μm",
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

# plot B*(Vg) for each Wsc
fig, ax = plt.subplots(figsize=(2.5, 2.5))
ax.set_xlabel(r"$V_\mathrm{g}$ (V)")
ax.set_ylabel("$B_*$ (mT)")
ax.axhline(0, color="lightgrey", lw=0.5)
ax.set_xlim((-6, 11))
fits = read_csv("../../data/icpm_fitparams.csv")
fits = fits.sort_values(["wsc", "gate"], ascending=[False, True])
# use Wsc=inf Vg=-3V scan with less-pronounced 0-field dip anomaly
fits.drop(
    fits[fits["datapath"].str.contains("/Wsc=inf-SSE_diode-3V/")].index, inplace=True
)
for device, df in fits.groupby("device", sort=False):
    ax.errorbar(
        df["gate"],
        df["bstar"] / 1e-3,
        yerr=df["bstar_err"] / 1e-3,
        color=wsc_kwargs[device]["color"],
        label=wsc_kwargs[device]["label"],
        marker=wsc_kwargs[device]["marker"],
        zorder=wsc_kwargs[device]["zorder"],
    )
ax.legend(fontsize="xx-small")
ax2 = ax.twinx()
ax2.tick_params(axis="y", which="both", right=True, labelright=False)
ax2.set_ylabel(r"$\longleftarrow\tau\qquad\alpha\longrightarrow$")

## eyeballed from lotfizadeh2024 arxiv:2303.01902v1 Fig. 3b
alpha = [2, 4, 6, 8, 10, 12]  # meV.nm
bstar = np.array([0.44, 1.14, 1.84, 2.52, 3.19, 3.87]) / 4.06 * 20  # mT
fit = Polynomial.fit(alpha, bstar, 1)
alpha_ticks = np.array([0, 10, 20])
ax2.set_ylim(ax.get_ylim())
ax2.set_yticks(fit(alpha_ticks))
ax2.set_yticklabels([])
# ax2.set_yticklabels(alpha_ticks)
# ax2.set_ylabel(r"$\alpha$ (meV$\,$nm)")

fig.savefig(f"bstar.{rcParams['savefig.format']}")
