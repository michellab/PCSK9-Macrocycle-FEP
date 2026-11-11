"""Per-compound (MLE) and per-edge booktabs LaTeX tables for one protocol.

Numbers come from the extraction functions in ``cinnabar_multi_plot``, so a table
and its figure cannot disagree. Deviations are calculated minus experimental.
"""

import os

import pandas as pd

from cinnabar_multi_plot import extract_absolute, extract_relative

_UNIT = r"(kcal mol$^{-1}$)"
ABSOLUTE_COLUMNS = [
    ("compound", "Compound", ""),
    ("exp", r"$\Delta G_{\mathrm{exp}}$", _UNIT),
    ("exp_unc", r"$\sigma_{\mathrm{exp}}$", _UNIT),
    ("calc", r"$\Delta G_{\mathrm{calc}}$", _UNIT),
    ("deviation", "Deviation", _UNIT),
]
RELATIVE_COLUMNS = [
    ("perturbation", "Perturbation", ""),
    ("exp", r"$\Delta\Delta G_{\mathrm{exp}}$", _UNIT),
    ("calc", r"$\Delta\Delta G_{\mathrm{calc}}$", _UNIT),
    ("sem", "SEM", _UNIT),
    ("error", "Error", _UNIT),
]


def _compound_number(names):
    """Sort key: C2 < C7 < C17 rather than C17 < C2 < C7."""
    return names.str.lstrip("C").astype(int)


def _absolute_table(path):
    x, y, xerr, _, names = extract_absolute(path)
    df = pd.DataFrame(dict(compound=names, exp=x, exp_unc=xerr, calc=y, deviation=y - x))
    return df.sort_values("compound", key=_compound_number)


def _relative_table(path):
    x, y, _, yerr, pairs = extract_relative(path)
    a, b = zip(*pairs)
    df = pd.DataFrame(dict(labelA=a, labelB=b, exp=x, calc=y, sem=yerr, error=y - x))
    df["perturbation"] = df["labelA"] + r" $\rightarrow$ " + df["labelB"]
    return df.sort_values(["labelA", "labelB"], key=_compound_number)


def _to_latex(df, columns, signed):
    def cell(value, col):
        return value if isinstance(value, str) else f"${value:{'+' if col == signed else ''}.2f}$"

    return "\n".join([
        r"\begin{table}[htbp]", r"\centering",
        r"\begin{tabular}{l" + "r" * (len(columns) - 1) + "}", r"\toprule",
        " & ".join(c[1] for c in columns) + r" \\", " & ".join(c[2] for c in columns) + r" \\",
        r"\midrule",
        *(" & ".join(cell(row[c[0]], c[0]) for c in columns) + r" \\" for _, row in df.iterrows()),
        r"\bottomrule", r"\end{tabular}", r"\end{table}"])


def write_tables(path, outdir):
    """Write ``table_mle.tex`` and ``table_edges.tex`` and print a network summary."""
    abs_df, rel_df = _absolute_table(path), _relative_table(path)
    tables = {
        "mle": _to_latex(abs_df, ABSOLUTE_COLUMNS, "deviation"),
        "edges": _to_latex(rel_df, RELATIVE_COLUMNS, "error"),
    }
    os.makedirs(outdir, exist_ok=True)
    for key, tex in tables.items():
        with open(os.path.join(outdir, f"table_{key}.tex"), "w") as handle:
            handle.write(tex + "\n")

    n_nodes, n_edges = len(abs_df), len(rel_df)
    worst = abs_df.loc[abs_df["deviation"].abs().idxmax()]
    edge = rel_df.loc[rel_df["error"].abs().idxmax()]
    print(f"{n_nodes} compounds, {n_edges} perturbations\n"
          f"independent cycles: {n_edges - n_nodes + 1} (assuming a connected network)\n"
          f"sum of deviations: {abs_df['deviation'].sum():+.3f} (zero by construction when offset to a mean)\n"
          f"largest deviation: {worst['compound']} {worst['deviation']:+.2f} kcal/mol\n"
          f"largest edge error: {edge['labelA']} -> {edge['labelB']} {edge['error']:+.2f} kcal/mol")
