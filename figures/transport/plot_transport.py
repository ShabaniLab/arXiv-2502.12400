import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import rcParams

csv = pd.read_csv(
    "../../data/density-mobility/JS633-W2/density-mobility/JS633-W2_transport-params.csv"
)
gate = csv["gate (V)"]
n = csv["density (e12 cm^-2)"]
μxx, μyy = [csv[f"mobility {_} (e3 cm^2/V.s)"] for _ in ("xx", "yy")]
lxx, lyy = [csv[f"mean free path {_} (nm)"] for _ in ("xx", "yy")]

plt.style.use(["paper", "fullcolumn"])
rcParams["lines.markersize"] = 2

# plot density and mobility vs. gate voltage
fig, ax = plt.subplots()
ax.set_xlabel(r"$V_\mathrm{g}$ (V)")
ax.set_ylabel(r"$n$ ($10^{12}\,$cm$^{-2}$)")
(linen,) = ax.plot(gate, n, "-ok", label=r"$n$")
ax = ax.twinx()
ax.set_ylabel(r"$\mu$ ($10^3\,$cm$^2/$V$\,$s)")
(linexx,) = ax.plot(gate, μxx, "-s", label=r"$\mu \parallel [110]$")
(lineyy,) = ax.plot(gate, μyy, "-D", label=r"$\mu \parallel [1\overline{1}0]$")
ax.legend(handles=(linen, linexx, lineyy), loc="lower center", bbox_to_anchor=(0.6, 0))
fig.savefig(f"density-mobility.{rcParams['savefig.format']}")

# plot mean free path vs. gate voltage
fig, ax = plt.subplots()
ax.set_xlabel(r"$V_\mathrm{g}$ (V)")
ax.set_ylabel(r"$\ell$ (nm)")
ax.plot(gate, lxx, "-s", label=r"$\ell \parallel [110]$")
ax.plot(gate, lyy, "-D", label=r"$\ell \parallel [1\overline{1}0]$")
ax.axhline(80, color="k", lw=0.5, ls="--")
ax.text(
    -1, 81, r"$W_\mathrm{n} = $80$\,$nm", ha="center", va="bottom", fontsize="small"
)
ax.legend()
fig.savefig(f"mean-free-path.{rcParams['savefig.format']}")
