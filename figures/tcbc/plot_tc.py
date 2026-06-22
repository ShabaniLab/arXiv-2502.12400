"""Plot Tc data."""

from itertools import cycle

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from shabanipy.labber import ShaBlabberFile

TMIN, TMAX = 0.1, 4

# datasets with bad pins requiring offset correction are commented out
data = {
    "cooldown 1": dict(
        datapath=(
            "2023/05/Data_0511/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_AlHB_FL_WFS01-001.hdf5"
        ),
        Tchannel="Fridge - MC-RuOx-Temperature",
        devices=[
            dict(name="AlHB", channel="AlHB", Tmin=TMIN, Tmax=TMAX),
            dict(name="0.6-NNW", channel="Wsc=0.6um-NNW", Tmin=TMIN, Tmax=TMAX),
        ],
    ),
    "cooldown 2": dict(
        datapath="2023/08/Data_0820/JS633-W2_Wsc@v3.1_Wsc=1.2um-E_WFS02-001.hdf5",
        Tchannel="Fridge - MC-RuOx-Temperature",
        devices=[
            dict(name="1.2-E", channel="source/fundamental", Tmin=TMIN, Tmax=TMAX)
        ],
    ),
    "cooldown 3": dict(
        datapath="2023/10/Data_1002/JS633-W2_Wsc@v3.1_Wsc=0.3um-N_Wsc=inf-ESE_AlHB_WFS03-001.hdf5",
        Tchannel="Fridge - MC-RuOx-Temperature",
        devices=[
            dict(name="AlHB", channel="AlHB", Tmin=1.4, Tmax=TMAX),
            #            dict(name="0.3-N", channel="Wsc=0.3um-N", Tmin=1.33, Tmax=TMAX, offset=True),
            #            dict(name="inf-ESE", channel="Wsc=inf-ESE", Tmin=TMIN, Tmax=TMAX, offset=True),
        ],
    ),
    "cooldown 4": dict(
        datapath="2023/11/Data_1105/JS633-W2_Wsc@v3.1_Wsc=0.3um-N_Wsc=0.9um-NNE_Wsc=inf-ESE_WFS04-001.hdf5",
        Tchannel="Fridge - MC-RuOx-Temperature",
        devices=[
            dict(name="0.3-N", channel="Wsc=0.3um-N (8-12)", Tmin=TMIN, Tmax=TMAX),
            #            dict(name="0.9-NNE", channel="Wsc=0.9um-NNE (10-17)", Tmin=1.31, Tmax=TMAX, offset=True),
        ],
    ),
    # only polled temperature every 30s this cooldown
    #    "cooldown 5": dict(
    #        datapath="2023/12/Data_1213/JS633-W2_Wsc@v3.1_Wsc=0.3um-W_Wsc=inf-ESE_WFS05-001.hdf5",
    #        Tchannel="Fridge - MC Plate RuOx",
    #        devices=[
    ##            dict(name="0.3-W", channel="Wsc=0.3um-W", Tmin=TMIN, Tmax=8, offset=True),
    #            dict(name="inf-ESE", channel="Wsc=inf-ESE", Tmin=TMIN, Tmax=8),
    #        ]
    #    ),
    "cooldown 6": dict(
        datapath="2023/12/Data_1215/JS633-W2_Wsc@v3.1_Wsc=0.9um-ENE_Wsc=0.9um-NNE_WFS06-001.hdf5",
        Tchannel="Fridge - MC Plate RuOx",
        devices=[
            dict(name="0.9-ENE", channel="Wsc=0.9um-ENE", Tmin=TMIN, Tmax=TMAX),
            dict(name="0.9-NNE", channel="Wsc=0.9um-NNE", Tmin=1.23, Tmax=TMAX),
        ],
    ),
    "cooldown 7": dict(
        datapath="2024/06/Data_0606/JS633-W2_Wsc@v3.1_Wsc=0.9um-NNE_Wsc=0.9um-ENE_WFS07-001.hdf5",
        Tchannel="Fridge - MC Plate RuOx",
        devices=[
            dict(name="0.9-NNE", channel="Wsc=0.9um-NNE", Tmin=TMIN, Tmax=TMAX),
        ],
    ),
}

labels = {
    "AlHB": r"Al HB",
    "0.3-N": r"$W_\mathrm{sc}=$0.3$\,$μm (N)",
    "0.3-W": r"$W_\mathrm{sc}=$0.3$\,$μm (W)",
    "0.6-NNW": r"$W_\mathrm{sc}=$0.6$\,$μm (NNW)",
    "0.9-ENE": r"$W_\mathrm{sc}=$0.9$\,$μm (ENE)",
    "0.9-NNE": r"$W_\mathrm{sc}=$0.9$\,$μm (NNE)",
    "1.2-E": r"$W_\mathrm{sc}=$1.2$\,$μm (E)",
    "inf-SSE": r"$W_\mathrm{sc}\rightarrow\infty$ (SSE)",
    "inf-ESE": r"$W_\mathrm{sc}\rightarrow\infty$ (ESE)",
}
markers = cycle("o^vsDpHX<>*dP")


def drop_stale(x, y):
    """Drop stale data points.

    This is due to the Oxford control software pulling temperature data infrequently
    from Lakeshore resistance bridge.
    """
    x_fresh = [x[0]]
    indexs = [0]
    for i, x_ in enumerate(x):
        if x_ == x_fresh[-1]:
            continue
        x_fresh.append(x_)
        indexs.append(i)
    sort_idx = np.argsort(x_fresh)
    x_fresh = np.array(x_fresh)[sort_idx]
    y_fresh = y[indexs][sort_idx]
    return (x_fresh, y_fresh)


plt.style.use(["paper", "fullcolumn"])
fig, ax = plt.subplots()
ax.set_xlabel(r"$T$ (K)")
ax.set_ylabel(r"$R / R_\mathrm{n}$")
ax.axhline(0, color="black", lw=0.5)
ax.axvline(1.63, color="black", ls="--", lw=0.5)
ax.text(
    1.63,
    1,
    r"$T_\mathrm{c}\approx$1.63$\,$K",
    ha="right",
    va="center",
    fontsize="x-small",
)
for cooldown, dset in data.items():
    f = ShaBlabberFile(dset["datapath"])
    for device in dset["devices"]:
        temperature, resistance = f.get_data(
            dset["Tchannel"], device["channel"] + " - Value"
        )
        mask = (temperature > device["Tmin"]) & (temperature < device["Tmax"])
        temperature, resistance = temperature[mask], resistance[mask]
        temperature, resistance = drop_stale(temperature, resistance)
        ibias = (
            f.get_channel(f"{device['channel']} - Output amplitude").instrument.config[
                "Output amplitude"
            ]
            / 1e6
        )  # 1 MΩ output resistor
        resistance = np.real(resistance) / ibias
        if device.get("offset"):
            resistance -= resistance[np.argmin(temperature)]
        resistance /= resistance[np.argmax(temperature)]

        ax.plot(
            temperature,
            resistance,
            lw=0.5,
            label=f"{cooldown}: " + labels[device["name"]],
            marker=next(markers),
        )

ax.set_xlim((1, 2.5))
ax.legend(fontsize="xx-small")
fig.savefig(f"tc.{rcParams['savefig.format']}")
