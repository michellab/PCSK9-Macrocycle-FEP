"""DDG and DG correlation plots and statistics tables for several FEP protocols.

Each protocol is a cinnabar CSV of the same perturbation network. Values are in
kcal/mol, and calculated DGs are offset to the experimental mean.
"""

import matplotlib.pyplot as plt
import numpy as np
from cinnabar import FEMap
from cinnabar.stats import bootstrap_statistic
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator

COLORS = ("#0072B2", "#D55E00", "#009E73")  # Okabe-Ito: colour-blind safe
MARKERS = ("o", "s", "^")
FONT_SIZE = 8
SEED = 42  # reseeded before every statistic, so intervals do not depend on protocol order
_KCAL = r"$\mathrm{kcal\,mol^{-1}}$"

plt.rcParams.update({"lines.markeredgecolor": "0.35", "lines.markeredgewidth": 0.4})


def extract_absolute(path):
    """Per-compound ``exp, calc, exp_err, calc_err, names`` from the MLE network."""
    g = FEMap.from_csv(path).to_legacy_graph()
    x, y, xerr, yerr = np.array([(d["exp_DG"], d["calc_DG"], d["exp_dDG"], d["calc_dDG"])
                                 for _, d in g.nodes(data=True)]).T
    return x, y - y.mean() + x.mean(), xerr, yerr, list(g.nodes)


def extract_relative(path):
    """Per-edge ``exp, calc, exp_err, calc_err, (A, B) pairs``."""
    g = FEMap.from_csv(path).to_legacy_graph()
    x, y, xerr, yerr = np.array([(d["exp_DDG"], d["calc_DDG"], d["exp_dDDG"], d["calc_dDDG"])
                                 for *_, d in g.edges(data=True)]).T
    return x, y, xerr, yerr, list(g.edges)


def _bootstrap(data, statistics):
    out = {}
    for stat in statistics:
        np.random.seed(SEED)
        out[stat] = bootstrap_statistic(*data[:4], statistic=stat)
    return out


def _plot(femaps, extract, delta, statistics, filename):
    series = [(name, extract(path)) for name, path in femaps.items()]
    fig, ax = plt.subplots(figsize=(4, 4))

    # shared square limits including error bars
    lo = min(np.min(d[i] - d[i + 2]) for _, d in series for i in (0, 1)) - 0.5
    hi = max(np.max(d[i] + d[i + 2]) for _, d in series for i in (0, 1)) + 0.5

    for band in (0.5, 1.0):
        ax.fill_between([lo, hi], [lo - band, hi - band], [lo + band, hi + band],
                        color="grey", alpha=0.2, lw=0, zorder=0)
    ax.plot([lo, hi], [lo, hi], ":", color="k", lw=1, zorder=1)

    handles, labels = [], []
    width = max(map(len, statistics)) + 1  # "RMSE:" / "R2:  " aligned
    for i, (name, d) in enumerate(series):
        ax.errorbar(d[0], d[1], xerr=d[2], yerr=d[3], fmt=MARKERS[i], color=COLORS[i],
                    ms=6, elinewidth=1.2, capsize=0, linestyle="none", zorder=2 + i)
        handles.append(Line2D([], [], marker=MARKERS[i], color=COLORS[i], linestyle="none", ms=6))
        labels.append("\n".join([name, *(f"{k + ':':<{width}} {r['mle']:.2f}"
                                         for k, r in _bootstrap(d, statistics).items())]))

    ax.set(xlim=(lo, hi), ylim=(lo, hi), aspect="equal")
    ax.set_xlabel(rf"Experimental ${delta}$G ({_KCAL})", fontsize=FONT_SIZE)
    ax.set_ylabel(rf"Calculated ${delta}$G ({_KCAL})", fontsize=FONT_SIZE)
    ax.tick_params(labelsize=FONT_SIZE)
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_minor_locator(AutoMinorLocator(2))

    legend = ax.legend(handles, labels, loc="upper left", frameon=True, framealpha=1.0,
                       prop={"size": FONT_SIZE, "family": "monospace"},
                       handlelength=1.0, borderaxespad=0.4)
    for text, color in zip(legend.get_texts(), COLORS):
        text.set_color(color)

    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")


def plot_multi_DGs(femaps, statistics, filename):
    _plot(femaps, extract_absolute, r"\Delta", statistics, filename)


def plot_multi_DDGs(femaps, statistics, filename):
    _plot(femaps, extract_relative, r"\Delta\Delta", statistics, filename)


def stats_table(femaps, kind, statistics):
    """Text table of per-protocol statistics with 95% CIs; ``kind`` is 'ddg' or 'dg'."""
    extract = {"ddg": extract_relative, "dg": extract_absolute}[kind]
    rows = [["Protocol", "N", *(f"{stat} [95% CI]" for stat in statistics)]]
    for name, path in femaps.items():
        d = extract(path)
        rows.append([name, str(len(d[0])), *(f"{r['mle']:.2f} [{r['low']:.2f}, {r['high']:.2f}]"
                                             for r in _bootstrap(d, statistics).values())])

    widths = [max(map(len, col)) for col in zip(*rows)]
    lines = ["  ".join([r[0].ljust(widths[0]), r[1].rjust(widths[1]),
                        *(c.center(w) for c, w in zip(r[2:], widths[2:]))]).rstrip()
             for r in rows]
    rule = "-" * len(lines[0])
    return "\n".join([rule, lines[0], rule, *lines[1:], rule])
