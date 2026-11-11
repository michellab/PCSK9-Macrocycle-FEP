# Plotting the overall performance

This directory contains the scripts and data used to compare the overall performance of the free energy protocols reported in the manuscript against experiment. The results of the 3 reported analysis methods are compared:
1. Full (no data discarded)
2. Rapid (first 1ns discarded, 1-5ns kept, the rest is discarded)
3. Auto-equilibration (same as full, but equilibration detection and decorrelation are applied)

## Prerequisites

- Use the `openbiosim-pcsk9-repro` conda environment installed previously, with `cinnabar` version `0.5.0` added to it:

```bash
conda activate openbiosim-pcsk9-repro
conda install -c conda-forge cinnabar=0.5.0
```

## Usage

The results of each method are stored in a `cinnabar_plot_results_data_*.csv` file in the legacy cinnabar format, with experimental binding free energies followed by calculated relative free energies, all in kcal/mol. To generate the plots and tables, run the following from this directory:

```bash
conda activate openbiosim-pcsk9-repro
python plot_overall_performance.py
```

The input files (`CSVS`) and the reported statistics (`DDG_STATS`, `DG_STATS`) are set at the top of `plot_overall_performance.py`. The plotting functions are in `cinnabar_multi_plot.py` and the LaTeX tables are written by `cinnabar_multi_tables.py`. Bootstrap confidence intervals use a fixed random seed (`SEED`, 42) and are reproducible. cinnabar warns that it is assuming kcal/mol units, which is the expected unit of the input files.

## Outputs

The RMSE, MUE, R², and Pearson's r of each method with their 95% bootstrap confidence intervals are printed to the terminal, followed by a summary of the auto-equilibration network. The following files are written to this directory:

| File | Description |
|---|---|
| `pcsk9_ddg_plot_all_protocols_multiplot.svg` | Calculated against experimental ΔΔG of every perturbation for all methods, with the RMSE and MUE of each method in the legend. |
| `pcsk9_dg_plot_all_protocols_multi_exp_shift.svg` | Calculated (MLE, offset to the experimental mean) against experimental ΔG of every compound for all methods, with the RMSE, R², and Pearson's r of each method in the legend. |
| `tables/table_mle.tex` | LaTeX table of the experimental and calculated ΔG (kcal/mol) and deviation of every compound for the auto-equilibration method. |
| `tables/table_edges.tex` | LaTeX table of the experimental and calculated ΔΔG (kcal/mol), uncertainty, and error of every perturbation for the auto-equilibration method. |
