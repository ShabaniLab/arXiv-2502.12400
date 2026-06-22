from matplotlib import pyplot as plt
from matplotlib import rcParams
from pandas import read_csv

data = [
    dict(
        datapath="../../data/extract_ic/JS633-W2/Wsc=inf-SSE_diode+10V/data_deduped.csv",
        label=r"$V_\mathrm{g}=$10$\,$V",
        colors=("tab:green", "tab:blue"),
    ),
    dict(
        datapath="../../data/extract_ic/JS633-W2/Wsc=inf-SSE_diode-0V/data_deduped.csv",
        label=r"$V_\mathrm{g}=$0$\,$V",
        colors=("tab:orange", "tab:red"),
    ),
    dict(
        datapath="../../data/extract_ic/JS633-W2/Wsc=inf-SSE_diode-3V_coarsefield/data_deduped.csv",
        label=r"$V_\mathrm{g}=-$3$\,$V",
        colors=("tab:pink", "tab:purple"),
    ),
]

plt.style.use(["paper", "fullcolumn"])
fig, ax = plt.subplots()
ax.set_xlabel(r"$B_\parallel$ (T)")
ax.set_ylabel(r"$\eta$ (%)")
ax.axhline(0, color="lightgrey", lw=0.5)
ax.axvline(0, color="lightgrey", lw=0.5)

for d in data:
    df = read_csv(d["datapath"])
    b = df.iloc[:, 0]
    df = df[b.abs() <= 0.4]
    b = df.iloc[:, 0]

    c1, c2 = d["colors"]
    ax.plot(b, df["eta"] / 0.01, color=c1, lw=0.5, label=d["label"] + " raw", zorder=1)
    ax.plot(
        b,
        df["eta smoothed"] / 0.01,
        color=c2,
        lw=0.5,
        label=d["label"] + " smoothed",
        zorder=2,
    )

ax.set_xlim((-0.4, 0.4))
ax.legend(fontsize="xx-small")
fig.savefig(f"savgol.{rcParams['savefig.format']}")
