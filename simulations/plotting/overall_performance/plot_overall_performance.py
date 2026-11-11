"""Plots, statistics and LaTeX tables of the overall performance of the PCSK-9 protocols."""

from pathlib import Path

from cinnabar_multi_plot import plot_multi_DDGs, plot_multi_DGs, stats_table
from cinnabar_multi_tables import write_tables

HERE = Path(__file__).resolve().parent
CSVS = {
    "Full": "cinnabar_plot_results_data_full_07_aug_2026.csv",
    "Rapid": "cinnabar_plot_results_data_rapid_07_aug_2026.csv",
    "Auto equil.": "cinnabar_plot_results_data_auto_equib_07_aug_2026.csv",
}
DDG_STATS = ("RMSE", "MUE")
DG_STATS = ("RMSE", "R2", "rho")

femaps = {name: HERE / csv for name, csv in CSVS.items()}

plot_multi_DDGs(femaps, DDG_STATS, HERE / "pcsk9_ddg_plot_all_protocols_multiplot.svg")
plot_multi_DGs(femaps, DG_STATS, HERE / "pcsk9_dg_plot_all_protocols_multi_exp_shift.svg")

print(stats_table(femaps, "ddg", DDG_STATS))
print(stats_table(femaps, "dg", DG_STATS))

write_tables(femaps["Auto equil."], HERE / "tables")
