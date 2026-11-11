"""Forward/backward MBAR convergence of a SOMD2 leg across its replicates.

Usage: python analyse_convergence.py c17_to_c5_ring_break_free

The leg directory must contain repl_*/energy_traj_*.parquet. Plots and CSVs are
written next to the leg directory, prefixed with its name.
"""

import argparse
import warnings
from pathlib import Path

import BioSimSpace as BSS
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from alchemlyb.convergence import forward_backward_convergence
from alchemlyb.postprocessors.units import to_kcalmol
from alchemlyb.preprocessing import decorrelate_u_nk, slicing

TEMPERATURE = 300.0  # K; must match the parquet metadata
N_POINTS = 10

# Time bounds are in ps
STRATEGIES = {
    "Full": {"t_min": 0, "t_max": None, "auto_eq": False},
    "Auto-Equilibrated": {"t_min": 0, "t_max": None, "auto_eq": True},
    "Rapid": {"t_min": 1001, "t_max": 5001, "auto_eq": False},
}


def load_replicate(repl_dir):
    """Load the raw u_nk data of every lambda window in a replicate."""
    files = sorted(repl_dir.glob("*.parquet"))
    u_nk_list = [BSS.FreeEnergy.Relative._somd2_extract(f, T=TEMPERATURE) for f in files]
    if len({len(df) for df in u_nk_list}) != 1:
        warnings.warn(f"Windows in {repl_dir} differ in length: {[len(df) for df in u_nk_list]}")
    return u_nk_list


def discard_metrics(window, trimmed, equilibrated):
    """Summarise how much of a window equilibration detection discarded."""
    times = trimmed.index.get_level_values("time")
    new_start = equilibrated.index.get_level_values("time").min()
    total, discarded = times.max() - times.min(), new_start - times.min()
    return {
        "Lambda_Window": window,
        "Original_Start_ns": round(times.min() / 1000, 3),
        "Equilibrated_Start_ns": round(new_start / 1000, 3),
        "Discarded_ns": round(discarded / 1000, 3),
        "Total_Original_ns": round(total / 1000, 3),
        "Fraction_Discarded": round(discarded / total if total > 0 else 0, 3),
    }


def apply_strategy(u_nk_list, t_min, t_max, auto_eq):
    """Trim each window and optionally detect equilibration and decorrelate.

    Returns the processed windows and the metrics of those that were decorrelated.
    """
    processed, metrics = [], []
    for window, df in enumerate(u_nk_list):
        trimmed = slicing(df, lower=t_min, upper=t_max)
        processed.append(trimmed)
        if auto_eq:
            try:
                processed[-1] = decorrelate_u_nk(trimmed, remove_burnin=True)
                metrics.append(discard_metrics(window, trimmed, processed[-1]))
            except Exception as e:
                warnings.warn(f"Auto-equilibration failed for window {window}, using raw data: {e}")
    return processed, metrics


def compute_convergence(leg_dir):
    """Return forward/backward ΔG (kcal/mol) and equilibration discard metrics."""
    repl_dirs = sorted(leg_dir.glob("repl_*"))
    if not repl_dirs:
        raise FileNotFoundError(f"No repl_* directories found in {leg_dir}")

    results, all_metrics, max_times = [], [], {}
    for repl_dir in repl_dirs:
        print(f"Processing {repl_dir}...")
        u_nk_list = load_replicate(repl_dir)
        max_ps = round(u_nk_list[0].index.get_level_values("time").max())
        max_times[repl_dir.name] = max_ps

        for name, strategy in STRATEGIES.items():
            processed, metrics = apply_strategy(u_nk_list, **strategy)
            all_metrics += [{"Replicate": repl_dir.name, "Strategy": name, **m} for m in metrics]

            convergence = to_kcalmol(forward_backward_convergence(processed, estimator="MBAR", num=N_POINTS))
            # to_kcalmol also rescales data_fraction, so restore the 0-1 range
            convergence["data_fraction"] /= convergence["data_fraction"].max()

            t_min, t_max = strategy["t_min"], strategy["t_max"] or max_ps
            span = "Variable Discard" if strategy["auto_eq"] else f"{round(t_min / 1000)} - {round(t_max / 1000)} ns"
            convergence["strategy"] = f"{name} ({span})"
            convergence["replicate"] = repl_dir.name
            results.append(convergence)

    if len(set(max_times.values())) != 1:
        raise ValueError(f"Replicates differ in sampling time (ps): {max_times}")
    return pd.concat(results, ignore_index=True), pd.DataFrame(all_metrics)


def summarise(results):
    """Return the mean and standard deviation of the final ΔG per strategy."""
    final = results[results["data_fraction"] == 1.0]
    return final.groupby("strategy", sort=False).agg(
        Mean_Final_Forward=("Forward", "mean"),
        Std_Final_Forward=("Forward", "std"),
        Mean_Final_Backward=("Backward", "mean"),
        Std_Final_Backward=("Backward", "std"),
    ).round(2).reset_index()


def plot_convergence(results, title, output_stem):
    """Plot replicate traces and their mean ± SD for each strategy."""
    sns.set_theme(style="ticks", context="paper", font_scale=1.3)
    strategies = results["strategy"].unique()
    fig, axes = plt.subplots(1, len(strategies), figsize=(12, 7.41), sharey=True)

    for ax, strategy in zip(axes, strategies):
        data = results[results["strategy"] == strategy]
        for direction, color, marker in (("Forward", "#007FFF", "o"), ("Backward", "#FF4500", "s")):
            for _, replicate in data.groupby("replicate"):
                ax.plot(replicate["data_fraction"], replicate[direction], color=color, alpha=0.25, linewidth=1, zorder=1)
            sns.lineplot(
                data=data, x="data_fraction", y=direction, ax=ax, color=color, marker=marker, markersize=6,
                linewidth=2.5, errorbar="sd", label=f"{direction} Mean", zorder=2,
            )
        ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_title(strategy.replace(" (", "\n("), weight="bold", pad=15)
        ax.set_xlabel("Fraction of Data Analyzed", weight="bold", labelpad=10)
        ax.set_ylabel("")
        ax.legend(frameon=False, loc="best")
        sns.despine(ax=ax)

    axes[0].set_ylabel("Convergence ΔG (kcal/mol)", weight="bold")
    fig.suptitle(f"ΔG Convergence {title}", weight="bold", y=1.05, fontsize=18)
    fig.tight_layout()
    for suffix in ("pdf", "png"):
        fig.savefig(f"{output_stem}_convergence.{suffix}", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("leg_dir", type=Path, help="directory containing the repl_* subdirectories")
    leg_dir = parser.parse_args().leg_dir
    output_stem = leg_dir.with_name(leg_dir.name)

    results, metrics = compute_convergence(leg_dir)
    summary = summarise(results)
    print("\nFinal free energy estimates (kcal/mol):")
    print(summary.to_string(index=False))

    summary.to_csv(f"{output_stem}_summary_statistics.csv", index=False)
    results.to_csv(f"{output_stem}_convergence_data.csv", index=False)
    if not metrics.empty:
        metrics.to_csv(f"{output_stem}_discard_metrics.csv", index=False)
        print("\nAverage discard per replicate (Auto-Equilibrated):")
        print(metrics.groupby("Replicate")["Discarded_ns"].mean().reset_index().to_string(index=False))

    plot_convergence(results, leg_dir.name, output_stem)
