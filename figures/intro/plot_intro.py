import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from pandas import merge, read_csv
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
from shabanipy.labber import ShaBlabberFile

VMIN, VMAX = 0, 100  # colorbar limits
# zoom-panels limits
ZOOM_XMIN, ZOOM_XMAX = -0.205, 0.205
ZOOM_YMIN, ZOOM_YMAX = 1.9, 3.9

plt.style.use(["paper", "onethirdpage"])

###################
# full fraunhofer #
###################

with ShaBlabberFile(
    "2023/05/Data_0516/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-018.hdf5"
) as f:
    bfield, ibias, dvdi = f.get_data(
        "VectorMagnet - Field X",
        "Yoko - Voltage",
        "SRS1 - Value",
        filters=[
            ("VectorMagnet - Field X", np.greater, -0.00375),
            ("VectorMagnet - Field X", np.less, 0.004),
        ],
    )
    ibias *= -1  # sign convention
    ibias /= 1e6  # 1MΩ resistor at Yoko output
    dvdi = dvdi.real
    dvdi /= 20e-3 / 1e6  # 20mV over 1MΩ resistor at lock-in output
fig, ax = plt.subplots()
ax.set_xlabel("$B_\perp$ (mT)")
ax.set_ylabel("$I$ (μA)")
mesh = ax.pcolormesh(
    bfield / 1e-3, ibias / 1e-6, dvdi, rasterized=True, vmin=VMIN, vmax=VMAX
)
ax.add_patch(
    Rectangle(
        (ZOOM_XMIN, ZOOM_YMIN),
        width=ZOOM_XMAX - ZOOM_XMIN,
        height=ZOOM_YMAX - ZOOM_YMIN,
        fc="none",
        ec="k",
        ls="--",
        lw=0.5,
    )
)
ax.add_patch(
    Rectangle(
        (ZOOM_XMIN, -ZOOM_YMAX),
        width=ZOOM_XMAX - ZOOM_XMIN,
        height=ZOOM_YMAX - ZOOM_YMIN,
        fc="none",
        ec="k",
        ls="--",
        lw=0.5,
    )
)
ax.text(
    0.97,
    0.95,
    "$B_\parallel=0$\n$V_\mathrm{g}$ $=0$",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize="small",
    bbox=dict(boxstyle="round,pad=0.1", color="w", alpha=0.5),
)
fig.savefig("fraunhofer")

##############
# gate sweep #
##############

with ShaBlabberFile(
    "2023/05/Data_0514/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-005.hdf5"
) as f1, ShaBlabberFile(
    "2023/05/Data_0515/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-006.hdf5"
) as f2:
    gate1, ibias1, dvdi1 = f1.get_data(
        "gate 11 - Source voltage",
        "Bias current",
        "VICurveTracer - dR vs I curve",
        filters=[("gate 11 - Source voltage", np.greater, -8.001)],
    )
    gate2, ibias2, dvdi2 = f2.get_data(
        "gate 11 - Source voltage",
        "Bias current",
        "VICurveTracer - dR vs I curve",
        filters=[("gate 11 - Source voltage", np.greater, 0)],
    )
    gate = np.concatenate([gate1, gate2], axis=-1)
    ibias = np.concatenate([ibias1, ibias2], axis=-1)
    dvdi = np.concatenate([dvdi1, dvdi2], axis=-1)
    dvdi = dvdi.real
fig, ax = plt.subplots()
mesh = ax.pcolormesh(gate, ibias / 1e-6, dvdi, rasterized=True, vmin=VMIN, vmax=VMAX)
ax.set_xlabel("$V_\mathrm{g}$ (V)")
ax.set_ylabel("$I$ (μA)")
mpl.rc("text.latex", preamble=r"\usepackage{bm}")
ax.text(
    0.5,
    0.5,
    r"$\bm{B}=0$",
    transform=ax.transAxes,
    ha="center",
    va="center",
    fontsize="small",
    bbox=dict(boxstyle="round,pad=0.1", color="w", alpha=0.5),
    usetex=True,
)
fig.savefig("gate")

######################
# zoomed fraunhofers #
######################


csv = read_csv("../../data/centermax/JS633-W2/Wsc=0.6um-NNW_diode-0V/data_qca.csv")
fig, axs = plt.subplots(nrows=3, gridspec_kw=dict(hspace=0.1))
fig.set_size_inches((0.95 * fig.get_figwidth(), 4))
labelpad = 15
axs[-1].set_xlabel("$B_\perp$ (mT)", labelpad=labelpad)
# insets
space = 0.05
height = (1 - space) / 2
paths = [
    "2023/05/Data_0531/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-103.hdf5",
    "2023/05/Data_0530/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-098.hdf5",
    "2023/05/Data_0527/JS633-W2_Wsc@v3.1_Wsc=0.6um-NNW_WFS01-086.hdf5",
]
markerprops = [
    dict(marker="^", ms=7, mec="k", mew=0.5, mfc="tab:red"),
    dict(marker="s", ms=6, mec="k", mew=0.5, mfc="tab:orange"),
    dict(marker="*", ms=9, mec="k", mew=0.5, mfc="tab:green"),
]
for i, (path, ax, blabel, thetalabel, mprops, icvas) in enumerate(
    zip(
        paths,
        axs,
        [r"$B_\parallel=-$125$\,$mT", r"$B_\parallel=$0", r"$B_\parallel=$125$\,$mT"],
        [r"$\theta=\pi/2$", "", r"$\theta=\pi/2$"],
        markerprops,
        [("bottom", "top"), ("top", "bottom"), ("bottom", "top")],
    )
):
    ax.text(
        0,
        1.01,
        blabel,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize="small",
    )
    ax.text(
        1,
        1.01,
        thetalabel,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize="small",
    )
    ax.set_ylabel("$I$ (μA)", labelpad=labelpad)
    ax.spines[:].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.plot(
        0.1,
        0.9,
        transform=ax.transAxes,
        lw=0,
        **mprops,
        zorder=10,
    )
    for overunder, y0, ybreak, hidespine, pm, icva in zip(
        (np.less, np.greater),
        (height + space, 0),
        (0, 1),
        ("bottom", "top"),
        ("+", "-"),
        icvas,
    ):
        inset = ax.inset_axes((0, y0, 1, height))  # x0, y0, width, height
        inset.tick_params(labelbottom=False)
        inset.set_xlim((ZOOM_XMIN, ZOOM_XMAX))
        # dashed spines
        if path.endswith("098.hdf5"):
            inset.spines[:].set_linestyle("--")
            inset.spines[:].set_linewidth(1)
        else:
            inset.spines[hidespine].set_visible(False)
        if hidespine == "bottom":
            inset.xaxis.tick_top()
        # broken y-axis
        kwargs = dict(
            marker=[(-1, -1), (1, 1)],
            color="k",
            ls="none",
            ms=5,
            mec="k",
            mew=0.5,
            clip_on=False,
        )
        inset.plot([0, 1], [ybreak, ybreak], transform=inset.transAxes, **kwargs)

        with ShaBlabberFile(path) as f:
            bfield, ibias, dvdi = f.get_data(
                "VectorMagnet - Field X",
                "Yoko - Voltage",
                "source/fundamental - Value",
                filters=[
                    ("Yoko - Voltage", overunder, 0),
                ],
            )
            ibias *= -1  # sign convention
            ibias /= 1e6  # 1MΩ resistor at Yoko output
            dvdi = dvdi.real
            dvdi /= 10e-3 / 1e6  # 10mV over 1MΩ resistor at lock-in output
            mesh = inset.pcolormesh(
                bfield / 1e-3, ibias / 1e-6, dvdi, rasterized=True, vmin=VMIN, vmax=VMAX
            )
        # Ic markers
        xa, ya = csv.loc[csv["datafile"] == path][
            [f"center{pm}", f"ic{pm} from fit"]
        ].values.squeeze()
        xa /= 1e-3  # mT
        ya /= 1e-6  # μA
        (offset,) = np.diff(inset.get_ylim()) * 0.1
        inset.plot(xa, ya, marker="x", c="w", ms=5, mew=1)
        inset.text(
            xa,
            ya + (-1 if icva == "top" else 1) * offset,
            f"$I_{{\mathrm{{c}}{pm}}}$",
            c="w",
            ha="center",
            va=icva,
        )
inset.tick_params(labelbottom=True)
cb = fig.colorbar(
    mesh,
    ax=axs,
    extend="max",
    norm=Normalize(vmin=VMIN, vmax=VMAX),
    aspect=35,
)
cb.set_label("$\mathrm{d}V/\mathrm{d}I$ (Ω)", labelpad=-3)
fig.savefig("fraunhofer-zoom")

###################
# diode vs. field #
###################

# for peer reviewer:
# estimate effect of in-plane field misalignment from true θ=0
# - taylor series to first order: η(θ) ~ η(0) + (dη/dθ|θ=0)θ
# - estimate (dη/dθ|θ=0) from linear interpolation of θ=π/2 data:
#     (dη/dθ|θ=0) ~ (η(π/2) - η(-π/2)) / π = 2η(π/2)/π
# - multiply by π/2 to correct systematic underestimation of slope:
#   - true slope of sinθ at θ=0 is 1
#   - above estimates slope as 2/π
#   => (dη/dθ|θ=0) ~ η(π/2)
# - estimate θ~2° from typical out-of-plane misalignment and η(θ) fit below

# merge θ=π/2 data onto θ=0 B-field values
csv_merged = merge(
    read_csv("../../data/centermax/JS633-W2/Wsc=0.6um-NNW_diode-y/data.csv"),  # θ=0
    csv,  # θ=π/2
    left_on="VectorMagnet - Field Y",
    right_on="VectorMagnet - Field Z",
    how="left",
    suffixes=("", "_perp"),
)
# drop multiplied B=0 datapoints from merge
csv_merged.drop(index=[9, 11], inplace=True)
# sign convention (make 0deg instead of 180deg)
csv_merged.loc[:, "VectorMagnet - Field Y"] *= -1
# η_err ~ η(π/2) x 2° according to estimate described above
csv_merged["eta_err_misalignment"] = csv_merged["eta_perp"] * np.radians(2)
csv_merged["eta_err"] += csv_merged["eta_err_misalignment"].abs()

fig, ax = plt.subplots()
ax.set_xlabel("$B_\parallel$ (T)")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
csvs = [csv, csv_merged]
for csv, kwargs in zip(
    reversed(csvs),
    (
        dict(
            lw=0,
            marker="o",
            ms=1,
            c="k",
            label=r"$\theta=0$",
        ),
        dict(lw=0, marker="s", ms=1, c="tab:blue", label=r"$\theta=\pi/2$"),
    ),
):
    bfield = csv.iloc[:, 0].values
    icp, icm, icp_err, icm_err = csv.loc[
        :, ["ic+ from fit", "ic- from fit", "rmse+", "rmse-"]
    ].values.T
    # delta
    delta = icp - np.abs(icm)
    delta_err = np.sqrt(icp_err**2 + icm_err**2)
    # eta
    sigma = icp + np.abs(icm)
    sigma_err = delta_err  # assuming covariance(Ic+, Ic-) = 0
    eta = delta / sigma
    eta_err = csv["eta_err"].values
    ax.plot(bfield, eta * 100, **kwargs)
    ax.fill_between(
        bfield,
        (eta + eta_err) * 100,
        (eta - eta_err) * 100,
        alpha=0.5,
        facecolor=kwargs["c"],
    )
for path, mprops in zip(paths, markerprops):
    mprops.update(dict(ms=mprops["ms"] - 3, zorder=10, mew=0.3))
    (idx,) = csvs[0].index[csvs[0]["datafile"] == path].tolist()
    ax.plot(bfield[idx], eta[idx] * 100, **mprops)
ax.legend(handletextpad=0.4, handlelength=1)
fig.savefig("in-plane")

# zoom plot η(θ=0) with estimate of misalignment err
fig, ax = plt.subplots()
ax.set_xlabel("$B_\parallel$ (T)")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
bfield = csv_merged.iloc[:, 0].values
ax.errorbar(
    bfield,
    csv_merged["eta"].values * 100,
    yerr=csv_merged["eta_err"].values * 100,
    elinewidth=0.5,
    lw=0,
    marker="o",
    ms=3,
    c="k",
    label=r"$\theta=0$",
)
# ax.plot(
#    bfield,
#    csv_merged["eta_err_misalignment"].values * 100,
#    lw=0,
#    marker="o",
#    ms=1,
#    c="tab:red",
#    label=r"$\theta=2^\circ$",
# )
ax.legend(handletextpad=0.4, handlelength=1)
ax.set_ylim((-0.5, 0.5))
fig.savefig("in-plane_misalignment")

###################
# ic+/- vs. angle #
###################

fig, axs = plt.subplots(nrows=2, sharex=True)
fig.set_figheight(2 * fig.get_figheight())
axs[-1].set_xlabel(r"$\theta$")
axs[-1].set_xticks([-180, -90, 0, 90, 180])
axs[-1].set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])

ax = axs[0]
ax.set_ylabel("$I_\mathrm{c}$ (μA)")
csv = read_csv("../../data/centermax/JS633-W2/Wsc=0.6um-NNW_diode-angle-125mT/data.csv")
angle, icp, icm, icp_err, icm_err = csv.loc[
    :, ["in-plane angle-from-z", "ic+ from fit", "ic- from fit", "rmse+", "rmse-"]
].values.T
kwargsp = dict(color="tab:blue", zorder=5)
kwargsm = dict(color="tab:orange", zorder=10)


def angle_from_I(angle_from_z):
    """Measure angle from current direction (θ) instead of z-coil axis (θz).

    N.b. Wsc=0.6um-NNW was hooked up with I polarity such that angle_from_I = *-90* +
    angle_from_z.  However we inverted the current in invert_current.py to conform to
    the convention that (IxB).growth > 0.  Therefore the *+90* below is correct.
    """
    return (angle_from_z + 90) % 360


def sym_domain(theta, y):
    """Roll data onto the symmetric interval [-π, π], given theta ∈ [0, 2π)."""
    shift = -np.argmax(theta + 180 >= 360)
    new_theta = ((theta + 180) % 360) - 180
    new_theta = np.roll(new_theta, shift)
    new_theta = np.append(new_theta, np.abs(new_theta[0]))  # duplicate -180° at +180°
    new_y = np.roll(y, shift)
    new_y = np.append(new_y, new_y[0])
    return new_theta, new_y


ax.plot(
    *sym_domain(angle_from_I(angle), icp / 1e-6),
    label=r"$I_{\mathrm{c}+}$",
    lw=0,
    marker="o",
    **kwargsp,
)
ax.plot(
    *sym_domain(angle_from_I(angle), np.abs(icm) / 1e-6),
    label=r"$|I_{\mathrm{c}-}|$",
    lw=0,
    marker="s",
    **kwargsm,
)
# n.b. data endpoints θz=0 and 360 are both mapped to θ=90 by θ = (θz + 90) % 360;
# interpolate over the original θz domain [0, 360] to avoid duplicate points
angle_interp = np.arange(angle.min(), angle.max(), 1)
csp = CubicSpline(angle, icp)(angle_interp)
csm = CubicSpline(angle, np.abs(icm))(angle_interp)
angle_interp_sym, csp = sym_domain(angle_from_I(angle_interp), csp)
angle_interp_sym, csm = sym_domain(angle_from_I(angle_interp), csm)
split = np.argmax(angle_interp_sym == 90)
for s in (slice(None, split + 1), slice(split, None)):
    ax.plot(angle_interp_sym[s], csp[s] / 1e-6, **kwargsp)
    ax.plot(angle_interp_sym[s], csm[s] / 1e-6, **kwargsm)
ax.text(
    0,
    1.01,
    r"$B_\parallel=$125$\,$mT",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize="small",
)
ax.legend(handletextpad=0.4, handlelength=1)

###################
# diode vs. angle #
###################

ax = axs[-1]
ax.set_xlabel(r"$\theta$")
ax.set_ylabel("$\eta$ (%)")
ax.axhline(0, c="lightgrey", lw=0.5, zorder=-1)
ax.axvline(0, c="lightgrey", lw=0.5, zorder=-1)
# delta
delta = icp - np.abs(icm)
delta_err = np.sqrt(icp_err**2 + icm_err**2)
# eta
sigma = icp + np.abs(icm)
sigma_err = delta_err  # assuming covariance(Ic+, Ic-) = 0
eta = delta / sigma
eta_err = np.abs(eta) * np.sqrt((delta_err / delta) ** 2 + (sigma_err / sigma) ** 2)
# largest error bars are ~ +/-0.2%
ax.plot(
    *sym_domain(angle_from_I(angle), eta * 100),
    label="data",
    lw=0,
    marker="o",
    color="k",
)


def sin(degrees, amplitude, offset):
    return amplitude * np.sin(np.radians(degrees + offset))


popt, pcov = curve_fit(sin, angle + 90, eta)
# from fit: amplitude=0.04945108, offset=-1.587580deg
print(f"amplitude={popt[0]}, offset={popt[1]}deg")
x = np.arange(360)  # angle from I
ax.plot(
    *sym_domain(x, sin(x, *popt) * 100),
    "tab:gray",
    label=r"fit",
    zorder=-1,
)
ax.legend()

mpl.rc("font", size=8)
ins = ax.inset_axes((0.53, 0.05, 0.45, 0.35))
ins.set_xlim(ax.get_xlim())
ins.set_xticks([-180, -90, 0, 90, 180])
ins.set_xticklabels([])
ins.set_yticks([0])
ins.set_yticklabels([])
# ins.axhline(0, color="lightgrey", lw=0.5)
# ins.axvline(0, color="lightgrey", lw=0.5)
angle_res = angle_from_I(angle)
angle_res_sym, residual = sym_domain(angle_res, eta - sin(angle_res, *popt))
angle_res_sym, res_err = sym_domain(angle_res, eta_err)
split = np.argmax(angle_res_sym == 90)
for s in (slice(None, split + 1), slice(split, None)):
    ins.errorbar(
        angle_res_sym,
        residual * 100,
        yerr=res_err * 100,
        lw=0.3,
        marker="o",
        ms=1.5,
        color="k",
    )
fig.savefig("angle")
