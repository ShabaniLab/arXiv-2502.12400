"""Find extrema using splines."""
import argparse
from pathlib import Path
from pprint import pformat

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from pandas import DataFrame, read_csv
from scipy.interpolate import CubicSpline

# set up command-line interface
parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    "datapath",
    help="path to .csv file containing columns for Ic+, Ic-, and B//",
)
parser.add_argument(
    "--bcol",
    help=(
        "name of column containing B-field data; "
        "if None, the first column matching *[Ff]ield* is used"
    ),
)
parser.add_argument(
    "--icp_col",
    default="ic+ from fit",
    help="name of column containing Ic+ data",
)
parser.add_argument(
    "--icm_col",
    default="ic- from fit",
    help="name of column containing Ic- data",
)
parser.add_argument(
    "--delta_col",
    default="delta",
    help="name of column containing ΔIc data",
)
parser.add_argument(
    "--eta_col",
    default="eta",
    help="name of column containing η=ΔIc/ΣIc data",
)
parser.add_argument(
    "--bmax",
    default=0.15,
    type=float,
    help="limit plot to |B-fields| < bmax (T)",
)
parser.add_argument(
    "--quiet",
    default=False,
    action="store_true",
    help="do not show plots and suppress console output",
)
args = parser.parse_args()

df = read_csv(args.datapath)
# find bfield column name
if args.bcol is not None:
    bcol = args.bcol
else:
    try:
        bcol = next(c for c in df.columns if "field" in c.lower())
    except StopIteration:
        raise ValueError(
            "Can't find field column. Available columns are:\n"
            f"{pformat(list(df.columns))}"
        )
# limit field range
if args.bmax is not None:
    mask = (-args.bmax <= df[bcol]) & (df[bcol] <= args.bmax)
    df = df[mask]

# set up output
outdir = Path(args.datapath).parent / Path(__file__).stem
outdir.mkdir(exist_ok=True, parents=True)
outpath = str(outdir / Path(args.datapath).stem) + "_spline"


# find extrema of splines
def get_extrema(x, y):
    """Find and return [(xmin, xmax), (ymin, ymax)]."""
    if not np.all(np.diff(x) > 0):
        raise ValueError(
            "Cannot interpolate due to repeated or unsorted x values:"
            f" {x[np.append(np.diff(x) <= 0, False)].to_string(index=False)}"
        )
    cs = CubicSpline(x, y)
    x = np.arange(x.min(), x.max(), 1e-4)
    y = cs(x)
    x_ext = []
    y_ext = []
    for arg in (np.argmin, np.argmax):
        idx = arg(y)
        xpeak, ypeak = x[idx], y[idx]
        x_ext.append(xpeak)
        y_ext.append(ypeak)
    return np.array([x_ext, y_ext])


ic_extrema = np.array(
    [
        get_extrema(df[bcol], df[args.icm_col])[:, 0],
        get_extrema(df[bcol], df[args.icp_col])[:, 1],
    ]
).T
delta_extrema = get_extrema(df[bcol], df[args.delta_col])
eta_extrema = get_extrema(df[bcol], df[args.eta_col])

plt.style.use(["paper", "fullcolumn"])


def plot(
    ycol,
    yunit,
    ylabel=None,
    ytransform=lambda y: y,
    xcol=bcol,
    xunit=1e-3,
    xlabel=r"$B_\parallel$ (mT), $\theta=$90$^\circ$",
    label=None,
    fileprefix=None,
    extrema=None,
):
    fig, ax = plt.subplots()
    for ycol_, label_ in zip(np.atleast_1d(ycol), np.atleast_1d(label)):
        (line,) = ax.plot(
            df[xcol] / xunit,
            ytransform(df[ycol_] / yunit),
            label=label_,
            marker=".",
            linewidth=0,
        )
        cs = CubicSpline(df[xcol], df[ycol_])
        x = np.arange(df[xcol].min(), df[xcol].max(), 1e-4)
        ax.plot(
            x / xunit, ytransform(cs(x) / yunit), label="spline", color=line.get_color()
        )
    ax.plot(
        extrema[0] / xunit,
        ytransform(extrema[1] / yunit),
        label="extrema",
        lw=0,
        marker="x",
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.savefig(Path(outpath).parent / f"{fileprefix}.{rcParams['savefig.format']}")


plot(
    ycol=[args.icp_col, args.icm_col],
    yunit=1e-6,
    ylabel=r"$I_\mathrm{c}$ (μA)",
    ytransform=lambda y: np.abs(y),
    label=(r"$I_{\mathrm{c}+}$", r"$|I_{\mathrm{c}-}|$"),
    fileprefix="ic",
    extrema=ic_extrema,
)
plot(
    ycol=args.delta_col,
    yunit=1e-6,
    ylabel=r"$\Delta I_\mathrm{c}$ (μA)",
    label="data",
    fileprefix="delta",
    extrema=delta_extrema,
)
plot(
    ycol=args.eta_col,
    yunit=1 / 100,
    ylabel=r"$\eta$ (%)",
    label="data",
    fileprefix="eta",
    extrema=eta_extrema,
)


def cols(y):
    return [f"{y}_{a}" for a in ("argmin", "argmax", "min", "max")]


# save extrema
df = DataFrame(
    {
        **{k: [v] for k, v in zip(cols("ic"), np.array(ic_extrema).flatten())},
        **{k: [v] for k, v in zip(cols("delta"), np.array(delta_extrema).flatten())},
        **{k: [v] for k, v in zip(cols("eta"), np.array(eta_extrema).flatten())},
        **{k: [v] for k, v in args.__dict__.items() if k not in ("no_show",)},
    }
)
df.to_csv(outpath + ".csv", index=False)
print(f"Splined: {outdir}")
if not args.quiet:
    plt.show()
