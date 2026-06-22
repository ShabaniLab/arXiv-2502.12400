"""Plot Tc data."""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from shabanipy.labber import ShaBlabberFile

data = [
    dict(name="AlHB", channel="AlHB", label=r"Al HB", marker="o"),
    dict(
        name="inf-SSE",
        channel="source/fundamental",
        label=r"$W_\mathrm{sc}\rightarrow\infty$ (SSE)",
        marker="s",
    ),
]

plt.style.use(["paper", "fullcolumn"])
fig, ax = plt.subplots()
ax.set_xlabel(r"$B_\parallel$ (T)")
ax.set_ylabel(r"$R / R_\mathrm{n}$")
ax.axhline(0, color="black", lw=0.5)
ax.axvline(2.68, color="black", ls="--", lw=0.5)
ax.text(
    2.68,
    1,
    r"$B_\mathrm{c}\approx$2.68$\,$T",
    ha="right",
    va="center",
    fontsize="x-small",
)

f = ShaBlabberFile(
    "2023/10/Data_1012/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_AlHB_WFS03-090.hdf5"
)
for d in data:
    field, resistance = f.get_data("VectorMagnet - Field Z", d["channel"] + " - Value")
    ibias = (
        f.get_channel(f"{d['channel']} - Output amplitude").instrument.config[
            "Output amplitude"
        ]
        / 1e6
    )  # 1 MΩ output resistor
    resistance = np.real(resistance) / ibias
    resistance /= resistance[np.argmax(field)]

    ax.plot(
        field,
        resistance,
        lw=0.5,
        label=d["label"],
        marker=d["marker"],
        ms=1,
    )

ax.set_xlim((0, None))
ax.legend(fontsize="xx-small")
fig.savefig(f"bc.{rcParams['savefig.format']}")
